"""Current limit of the hub's light-bar rail, on TI's own transient model.

The 39 k programming resistor was chosen from the data sheet's IOS formula, and
a formula is not release evidence. This bench drives the vendor model with the
rail's real connectivity and measures what the limiter actually does: it has to
carry both light bars at full white without tripping, and clamp a fault below
the 1.0 A its harness contacts are rated for.

The model is PSpice, so ngspice runs it in compatibility mode. ngspice picks
that up from a .spiceinit in the deck's own directory, which is why this bench
generates into a directory of its own: sharing one with another deck silently
changed how that deck parsed.
"""

import re
import subprocess
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterator

from skidl import Circuit, Net

from hardware.pcb.hub import build_hub
from hardware.sim.spice import MODELS_DIR, emit_subckt


# Its own directory, not the shared hub one. ngspice reads .spiceinit from the
# deck's directory, so a compatibility mode left beside another bench's deck
# silently changes how that bench parses. This bench needs PSpice mode; nothing
# else does.
GENERATED_DIR = Path(__file__).parent / "generated" / "hub" / "led_rail"

# The rail: the limiter, its programming resistor, the fault pull-up and the
# decoupling either side of the switch.
RAIL_PARTS = frozenset({"U7", "R17", "R18", "C10", "C11"})
PORT_NETS = ("MODULE_5V", "LED_5V", "LED_EN", "LED_FAULT_N", "3V3")

# 0603WAF3902T5E, a 1% part, checked in the V1 audit.
LIMIT_RESISTOR_OHM = 39e3
RESISTOR_TOLERANCE = 0.01

# A power module's output, swept over the range the interface admits.
SUPPLY_V = (4.5, 5.0, 5.5)

# docs/hardware/lightbar.md: 14 pixels at 16 mA per bar, both bars white.
BAR_LOAD_A = 0.448

# Time base. The vendor model has a soft start of a few milliseconds, so the
# rail is left to settle before either measurement.
SETTLE_S = 15e-3
FAULT_S = 20e-3
STOP_S = 60e-3
STEP_S = 20e-6


@dataclass(frozen=True)
class Corner:
    supply_v: float
    limit_resistor: float

    @property
    def resistor_ohm(self) -> float:
        return LIMIT_RESISTOR_OHM * self.limit_resistor


@dataclass(frozen=True)
class RailResult:
    """Per corner: the rail under its real load, and under a dead short."""

    corners: tuple[Corner, ...]
    normal_a: tuple[float, ...]
    normal_v: tuple[float, ...]
    limit_a: tuple[float, ...]

    @property
    def lowest_limit_a(self) -> float:
        return min(self.limit_a)

    @property
    def highest_limit_a(self) -> float:
        return max(self.limit_a)

    @property
    def worst_rail_v(self) -> float:
        return min(self.normal_v)


def corners() -> Iterator[Corner]:
    for supply, resistor in product(
        SUPPLY_V, (1.0 - RESISTOR_TOLERANCE, 1.0 + RESISTOR_TOLERANCE)
    ):
        yield Corner(supply_v=supply, limit_resistor=resistor)


def deck(corner_list: tuple[Corner, ...]) -> str:
    circuit = build_hub()
    ports = tuple(
        next(net for net in circuit.get_nets() if str(net.name) == name)
        for name in PORT_NETS
    )
    lines = [
        "Hub light-bar rail current limit, per tolerance corner",
        f'.include "{MODELS_DIR / "tps2553.lib"}"',
    ]
    measurements: list[str] = []
    for index, corner in enumerate(corner_list):
        block = f"RAIL{index}"
        lines.append(
            emit_subckt(
                circuit,
                block,
                ports,
                only=RAIL_PARTS,
                values={"R17": f"{corner.resistor_ohm:.4f}"},
            ).rstrip("\n")
        )
        lines.append(f"Vin{index} in{index} 0 DC {corner.supply_v}")
        lines.append(f"Vlogic{index} logic{index} 0 DC 3.3")
        lines.append(f"Ven{index} en{index} 0 DC 3.3")
        lines.append(
            f"Xrail{index} in{index} out{index} en{index} fault{index} logic{index} {block}"
        )
        # Both bars at full white, then a dead short to force the limiter.
        normal_ohm = corner.supply_v / BAR_LOAD_A
        lines.append(
            f"Rload{index} out{index} 0 R = 'time < {FAULT_S} ? {normal_ohm:.4f} : 0.5'"
        )
        measurements.append(f"meas tran inorm{index} FIND i(Vin{index}) AT={SETTLE_S}")
        measurements.append(f"meas tran vnorm{index} FIND v(out{index}) AT={SETTLE_S}")
        measurements.append(
            f"meas tran ilim{index} MIN i(Vin{index}) FROM={FAULT_S + 5e-3} TO={STOP_S}"
        )
    lines.append(".control")
    lines.append(f"tran {STEP_S} {STOP_S}")
    lines.extend(measurements)
    lines.append("quit")
    lines.append(".endc")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def run() -> RailResult:
    corner_list = tuple(corners())
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    # PSpice parsing is scoped to this directory, which holds only this deck.
    (GENERATED_DIR / ".spiceinit").write_text("set ngbehavior=psa\n", encoding="utf-8")
    deck_path = GENERATED_DIR / "led_rail.cir"
    deck_path.write_text(deck(corner_list), encoding="utf-8")
    completed = subprocess.run(
        ("ngspice", "-b", deck_path.name),
        check=True,
        capture_output=True,
        text=True,
        cwd=GENERATED_DIR,
    )
    measured = _parse(completed.stdout)

    def required(key: str) -> float:
        value = measured.get(key)
        if value is None:
            raise RuntimeError(f"ngspice reported no measurement {key}\n{completed.stdout}")
        return value

    indices = range(len(corner_list))
    return RailResult(
        corners=corner_list,
        # The source current is negative into the supply, so magnitudes are used.
        normal_a=tuple(abs(required(f"inorm{index}")) for index in indices),
        normal_v=tuple(required(f"vnorm{index}") for index in indices),
        limit_a=tuple(abs(required(f"ilim{index}")) for index in indices),
    )


def _parse(output: str) -> dict[str, float]:
    measured: dict[str, float] = {}
    for match in re.finditer(r"^(\w+)\s*=\s*([-+0-9.eE]+)", output, re.MULTILINE):
        try:
            measured[match.group(1)] = float(match.group(2))
        except ValueError:
            continue
    return measured


if __name__ == "__main__":
    result = run()
    print(f"corners simulated: {len(result.corners)}")
    print(f"both bars white:   {min(result.normal_a) * 1e3:.1f} mA, rail {result.worst_rail_v:.3f} V")
    print(f"limit into a short: {result.lowest_limit_a * 1e3:.1f} to {result.highest_limit_a * 1e3:.1f} mA")
