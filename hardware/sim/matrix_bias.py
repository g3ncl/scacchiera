"""Selected-cell bias current against the choke's own absolute maximum.

The matrix RF bench proves the bias lands inside the band the design wants, at
one nominal operating point. It has never been swept, and the part carrying that
current is rated 15 mA, so the question this answers is different: over the rail
tolerance and the setting resistor's, how close does the current get to the
component maximum rather than to the design intent?
"""

import re
import subprocess
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterator

from hardware.sim.matrix_rf import CELL_SUBCKT, _build_cell, _includes
from hardware.sim.spice import emit_subckt


GENERATED_DIR = Path(__file__).parent / "generated" / "matrix" / "bias"

# LQM21DH100M70L data sheet, specifications table: the saturation-type rated
# current, by inductance change (the temperature-rise rating is higher, 300 mA
# at 125 C ambient). This is a component absolute maximum, not a design
# preference.
CHOKE_RATED_A = 0.250

# The 3.3 V rail's own regulation band, from the AP63203WU-7 data sheet's CCM
# feedback voltage of 3.27 to 3.33 V. The matrix is fed from that rail.
RAIL_V = (3.27, 3.30, 3.33)

# R_SET is a 1% part, and the bias current is roughly inversely proportional
# to it, so its extremes bound the current.
RESISTOR_TOLERANCE = 0.01
BIAS_RESISTOR_REF = "R2"
BIAS_RESISTOR_OHM = 180.0


@dataclass(frozen=True)
class Corner:
    rail_v: float
    resistor_scale: float

    @property
    def resistor_ohm(self) -> float:
        return BIAS_RESISTOR_OHM * self.resistor_scale


@dataclass(frozen=True)
class BiasResult:
    corners: tuple[Corner, ...]
    current_a: tuple[float, ...]

    @property
    def highest_a(self) -> float:
        return max(self.current_a)

    @property
    def lowest_a(self) -> float:
        return min(self.current_a)

    @property
    def headroom_to_rating(self) -> float:
        """Fraction of the choke's rating still unused at the worst corner."""
        return 1.0 - self.highest_a / CHOKE_RATED_A


def corners() -> Iterator[Corner]:
    for rail, scale in product(
        RAIL_V, (1.0 - RESISTOR_TOLERANCE, 1.0 + RESISTOR_TOLERANCE)
    ):
        yield Corner(rail_v=rail, resistor_scale=scale)


def deck(corner_list: tuple[Corner, ...]) -> str:
    circuit, ports = _build_cell()
    lines = ["Matrix selected-cell bias current, per tolerance corner", _includes()]
    probes: list[str] = []
    for index, corner in enumerate(corner_list):
        block = f"{CELL_SUBCKT}{index}"
        lines.append(
            emit_subckt(
                circuit,
                block,
                ports,
                values={BIAS_RESISTOR_REF: f"{corner.resistor_ohm:.4f}"},
            ).rstrip("\n")
        )
        lines.append(f"X{index} rf{index} vbias{index} seln{index} {block}")
        lines.append(f"Vbias{index} vbias{index} 0 DC {corner.rail_v}")
        # Selected: the steering PMOS gate is pulled low.
        lines.append(f"Vsel{index} seln{index} 0 DC 0")
        lines.append(f"Rsrc{index} rf{index} 0 1")
        probes.append(f"print i(Vbias{index})")
    lines.append(".control")
    lines.append("op")
    lines.extend(probes)
    lines.append("quit")
    lines.append(".endc")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def run() -> BiasResult:
    corner_list = tuple(corners())
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    deck_path = GENERATED_DIR / "bias.cir"
    deck_path.write_text(deck(corner_list), encoding="utf-8")
    completed = subprocess.run(
        ("ngspice", "-b", deck_path.name),
        check=True,
        capture_output=True,
        text=True,
        cwd=GENERATED_DIR,
    )
    if "solution failed" in completed.stdout.lower():
        raise RuntimeError(f"ngspice did not converge:\n{completed.stdout}")
    measured = {
        match.group(1).lower(): float(match.group(2))
        for match in re.finditer(
            r"^(\S+)\s*=\s*([-+0-9.eE]+)", completed.stdout, re.MULTILINE
        )
    }
    currents: list[float] = []
    for index in range(len(corner_list)):
        key = f"i(vbias{index})"
        if key not in measured:
            raise RuntimeError(f"ngspice reported no {key}")
        currents.append(abs(measured[key]))
    return BiasResult(corners=corner_list, current_a=tuple(currents))


if __name__ == "__main__":
    result = run()
    print(f"corners simulated: {len(result.corners)}")
    print(f"bias current: {result.lowest_a * 1e3:.3f} to {result.highest_a * 1e3:.3f} mA")
    print(f"choke rating: {CHOKE_RATED_A * 1e3:.0f} mA")
    print(f"headroom at the worst corner: {result.headroom_to_rating * 100:.0f} percent")
