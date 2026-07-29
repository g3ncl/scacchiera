"""Power stage of the hub's 3.3 V buck, over its published tolerances.

Everything on this board except the light bars runs from this rail, and its
inductor and output capacitors were chosen from the data sheet's application
table rather than from a simulation. This bench builds the stage from the same
SKiDL objects as the netlist and asks three questions the passives decide:
how much ripple reaches the MCU, how much peak current the inductor sees
against its saturation rating, and how much RMS current it carries against its
thermal one.

The converter runs open loop here, at a duty computed per corner from the
conduction drops, because Diodes publishes no model and the internal
compensation is not in the data sheet. See hardware/sim/models/ap63203.lib for
what that does and does not license a reader to conclude.
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


GENERATED_DIR = Path(__file__).parent / "generated" / "hub" / "buck"

# The converter and its filter. L1 is left out and rebuilt below with the series
# resistance a netlist cannot carry.
BUCK_PARTS = frozenset({"U5", "C1", "C2", "C3", "C4"})
PORT_NETS = ("MODULE_5V", "BUCK_SW", "3V3")

# AP63203WU-7 data sheet: Electrical Characteristics.
SWITCHING_HZ = 1.1e6
RDS_HIGH_SIDE = 0.125
RDS_LOW_SIDE = 0.068
OUTPUT_V = 3.30

# NR6045S4R7MT data sheet: 4.7 uH +/-20%, DC resistance, Isat and Irms. Rated
# current is the smaller of Isat and Irms, which is Irms here.
INDUCTOR_H = 4.7e-6
INDUCTOR_TOLERANCE = 0.20
INDUCTOR_DCR_OHM = 0.034
INDUCTOR_SAT_A = 4.97
INDUCTOR_RMS_A = 3.30

# The module output range the power-module interface admits.
SUPPLY_V = (4.5, 5.0, 5.5)

# Up to the converter's own 2 A rating, so the rail is characterised across its
# usable range rather than against a system budget that is not measured yet.
LOAD_A = (0.2, 0.8, 1.5, 2.0)

# Both output capacitors are 22 uF 25 V X5R 0805. Their data sheet prints only
# example bias curves, no numeric derating for this part, so effective
# capacitance is bounded rather than claimed: full nominal, and half of it. Half
# is well beyond the tolerance, temperature and bias a 25 V part loses at 3.3 V,
# and it is applied only in the pessimistic direction, since less capacitance
# means more ripple. A design that passes at the bound passes at the truth.
CAPACITANCE_DERATING = (1.0, 0.5)

# Started at the operating point, so the measurement sees switching ripple and
# not the undamped LC ring an open-loop stage takes milliseconds to settle.
SETTLE_S = 200e-6
STEP_S = 10e-9
MEASURE_PERIODS = 5


@dataclass(frozen=True)
class Corner:
    supply_v: float
    inductor_scale: float
    capacitor_scale: float
    load_a: float

    @property
    def inductance_h(self) -> float:
        return INDUCTOR_H * self.inductor_scale

    @property
    def duty(self) -> float:
        """Duty this corner needs, from the synchronous stage's conduction drops.

        Vout = D*Vin - I*(D*Rhs + (1-D)*Rls), solved for D. The inductor's own
        resistance is left out because the deck models it explicitly.
        """
        numerator = OUTPUT_V + self.load_a * RDS_LOW_SIDE
        denominator = self.supply_v - self.load_a * (RDS_HIGH_SIDE - RDS_LOW_SIDE)
        return numerator / denominator


@dataclass(frozen=True)
class BuckResult:
    corners: tuple[Corner, ...]
    ripple_v: tuple[float, ...]
    output_v: tuple[float, ...]
    peak_a: tuple[float, ...]
    rms_a: tuple[float, ...]

    @property
    def worst_ripple_v(self) -> float:
        return max(self.ripple_v)

    @property
    def worst_peak_a(self) -> float:
        return max(self.peak_a)

    @property
    def worst_rms_a(self) -> float:
        return max(self.rms_a)

    @property
    def worst_inductor_loss_w(self) -> float:
        """Conduction loss in the inductor at its worst simulated RMS current."""
        return self.worst_rms_a**2 * INDUCTOR_DCR_OHM


def corners() -> Iterator[Corner]:
    inductor_extremes = (1.0 - INDUCTOR_TOLERANCE, 1.0, 1.0 + INDUCTOR_TOLERANCE)
    for supply, inductor, capacitor, load in product(
        SUPPLY_V, inductor_extremes, CAPACITANCE_DERATING, LOAD_A
    ):
        yield Corner(
            supply_v=supply,
            inductor_scale=inductor,
            capacitor_scale=capacitor,
            load_a=load,
        )


def deck(corner_list: tuple[Corner, ...]) -> str:
    circuit = build_hub()
    ports = tuple(
        next(net for net in circuit.get_nets() if str(net.name) == name)
        for name in PORT_NETS
    )
    period = 1.0 / SWITCHING_HZ
    window_start = SETTLE_S - MEASURE_PERIODS * period
    lines = [
        "Hub 3.3 V buck power stage, per tolerance corner",
        f'.include "{MODELS_DIR / "ap63203.lib"}"',
    ]
    measurements: list[str] = []
    initial: list[str] = []
    for index, corner in enumerate(corner_list):
        block = f"BUCK{index}"
        lines.append(
            emit_subckt(
                circuit,
                block,
                ports,
                only=BUCK_PARTS,
                values={
                    "U5": f"duty={corner.duty:.6f}",
                    "C3": f"{22e-6 * corner.capacitor_scale:.9f}",
                    "C4": f"{22e-6 * corner.capacitor_scale:.9f}",
                },
            ).rstrip("\n")
        )
        lines.append(f"Vin{index} in{index} 0 DC {corner.supply_v}")
        lines.append(f"Xbuck{index} in{index} sw{index} out{index} {block}")
        # The schematic's inductor plus the series resistance its data sheet
        # publishes, which a netlist has nowhere to record.
        lines.append(f"Lout{index} sw{index} lx{index} {corner.inductance_h:.9e} ic={corner.load_a}")
        lines.append(f"Rdcr{index} lx{index} out{index} {INDUCTOR_DCR_OHM}")
        lines.append(f"Iload{index} out{index} 0 DC {corner.load_a}")
        initial.append(f"v(out{index})={OUTPUT_V}")
        measurements.append(
            f"meas tran ripple{index} PP v(out{index}) FROM={window_start:.12g} TO={SETTLE_S:.12g}"
        )
        measurements.append(
            f"meas tran vout{index} AVG v(out{index}) FROM={window_start:.12g} TO={SETTLE_S:.12g}"
        )
        measurements.append(
            f"meas tran ipk{index} MAX i(Lout{index}) FROM={window_start:.12g} TO={SETTLE_S:.12g}"
        )
        measurements.append(
            f"meas tran irms{index} RMS i(Lout{index}) FROM={window_start:.12g} TO={SETTLE_S:.12g}"
        )
    lines.append(".ic " + " ".join(initial))
    lines.append(".control")
    lines.append(f"tran {STEP_S:.12g} {SETTLE_S:.12g} uic")
    lines.extend(measurements)
    lines.append("quit")
    lines.append(".endc")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def run() -> BuckResult:
    corner_list = tuple(corners())
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    deck_path = GENERATED_DIR / "buck.cir"
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
            raise RuntimeError(f"ngspice reported no measurement {key}")
        return value

    indices = range(len(corner_list))
    return BuckResult(
        corners=corner_list,
        ripple_v=tuple(abs(required(f"ripple{index}")) for index in indices),
        output_v=tuple(required(f"vout{index}") for index in indices),
        peak_a=tuple(required(f"ipk{index}") for index in indices),
        rms_a=tuple(required(f"irms{index}") for index in indices),
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
    print(f"worst output ripple: {result.worst_ripple_v * 1e3:.2f} mV pk-pk")
    print(f"worst inductor peak: {result.worst_peak_a:.3f} A against {INDUCTOR_SAT_A} A saturation")
    print(f"worst inductor rms:  {result.worst_rms_a:.3f} A against {INDUCTOR_RMS_A} A rated")
    print(f"worst inductor loss: {result.worst_inductor_loss_w * 1e3:.1f} mW")
    print(f"output range: {min(result.output_v):.3f} to {max(result.output_v):.3f} V")
