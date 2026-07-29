"""V3 power-stage validation for the 5 V, 2 A TPS61088 boost.

TI's official transient model is filed beside this bench. It parses under
ngspice's PSpice mode but does not switch, settling at the body-diode voltage.
This bench therefore models only the synchronous switching stage. Its switch
resistances, frequency, inductor tolerance and DCR come from the filed device
and inductor data sheets. It proves passive stress and ripple, not control-loop
stability, startup, protection timing, or charger handover.
"""

import re
import subprocess
from math import sqrt
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterator


GENERATED_DIR = Path(__file__).parent / "generated" / "power" / "boost"

OUTPUT_V = 5.0
SWITCHING_HZ = 500e3
INDUCTOR_H = 1.2e-6
INDUCTOR_TOLERANCE = 0.20
INDUCTOR_DCR_OHM = 0.007
INDUCTOR_SAT_A = 12.2
INDUCTOR_RMS_A = 12.9
HIGH_SIDE_RDS_OHM = 0.018
LOW_SIDE_RDS_OHM = 0.0165
BATFET_RMS_A = 6.0
BATFET_OCP_A = 9.0
EFFICIENCY_FLOOR = 0.80

SUPPLY_V = (2.87, 3.6, 4.2)
LOAD_A = (0.1, 1.0, 2.0)
CAPACITANCE_F = 45e-6
CAPACITANCE_DERATING = (1.0, 0.5)

# TPS61088 data sheet equation 5 with the 100 and 51 kohm resistors at +1 percent,
# and the stated 1.3 A subtraction from the typical threshold.
CURRENT_LIMIT_FLOOR_A = 1_190_000.0 / (151_000.0 * 1.01) - 1.3

SETTLE_S = 120e-6
MEASURE_PERIODS = 8


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
        """Duty that balances the bounded conduction-stage equations."""
        low = 0.0
        high = min(0.95, 1.0 - self.supply_v / OUTPUT_V + 0.25)
        for _ in range(80):
            duty = (low + high) / 2.0
            current = self.load_a / (1.0 - duty)
            required = (
                duty * current * (INDUCTOR_DCR_OHM + LOW_SIDE_RDS_OHM)
                + (1.0 - duty)
                * (OUTPUT_V + current * (INDUCTOR_DCR_OHM + HIGH_SIDE_RDS_OHM))
            )
            if required > self.supply_v:
                low = duty
            else:
                high = duty
        return (low + high) / 2.0

    @property
    def average_inductor_a(self) -> float:
        return self.load_a / (1.0 - self.duty)


@dataclass(frozen=True)
class BoostResult:
    corners: tuple[Corner, ...]
    ripple_v: tuple[float, ...]
    output_v: tuple[float, ...]
    peak_a: tuple[float, ...]
    rms_a: tuple[float, ...]
    conservative_peak_a: tuple[float, ...]
    conservative_rms_a: tuple[float, ...]

    @property
    def worst_ripple_v(self) -> float:
        return max(self.ripple_v)

    @property
    def worst_peak_a(self) -> float:
        return max(self.conservative_peak_a)

    @property
    def worst_rms_a(self) -> float:
        return max(self.conservative_rms_a)

    @property
    def simulated_peak_a(self) -> float:
        return max(self.peak_a)

    @property
    def simulated_rms_a(self) -> float:
        return max(self.rms_a)


def corners() -> Iterator[Corner]:
    inductance = (1.0 - INDUCTOR_TOLERANCE, 1.0, 1.0 + INDUCTOR_TOLERANCE)
    for supply, scale_l, scale_c, load in product(
        SUPPLY_V, inductance, CAPACITANCE_DERATING, LOAD_A
    ):
        yield Corner(supply, scale_l, scale_c, load)


def deck(corner_list: tuple[Corner, ...]) -> str:
    period = 1.0 / SWITCHING_HZ
    start = SETTLE_S - MEASURE_PERIODS * period
    lines = [
        "TPS61088 synchronous boost power stage, per tolerance corner",
        f".model LOWSW SW(Ron={LOW_SIDE_RDS_OHM} Roff=1G Vt=0.5 Vh=0)",
        f".model HIGHSW SW(Ron={HIGH_SIDE_RDS_OHM} Roff=1G Vt=0.5 Vh=0)",
    ]
    initial: list[str] = []
    measures: list[str] = []
    for index, corner in enumerate(corner_list):
        period_text = f"{period:.12g}"
        on_time = corner.duty * period
        lines.extend(
            (
                f"Vin{index} in{index} 0 {corner.supply_v}",
                f"L{index} in{index} lx{index} {corner.inductance_h:.12g} "
                f"ic={corner.average_inductor_a:.12g}",
                f"Rdcr{index} lx{index} sw{index} {INDUCTOR_DCR_OHM}",
                f"Von{index} gon{index} 0 PULSE(0 1 0 1n 1n {on_time:.12g} {period_text})",
                f"Voff{index} goff{index} 0 PULSE(1 0 0 1n 1n {on_time:.12g} {period_text})",
                f"Slow{index} sw{index} 0 gon{index} 0 LOWSW",
                f"Shigh{index} sw{index} out{index} goff{index} 0 HIGHSW",
                f"Cout{index} out{index} 0 {CAPACITANCE_F * corner.capacitor_scale:.12g}",
                f"Rload{index} out{index} 0 {OUTPUT_V / corner.load_a:.12g}",
            )
        )
        initial.append(f"v(out{index})={OUTPUT_V}")
        measures.extend(
            (
                f"meas tran ripple{index} PP v(out{index}) FROM={start:.12g} TO={SETTLE_S:.12g}",
                f"meas tran vout{index} AVG v(out{index}) FROM={start:.12g} TO={SETTLE_S:.12g}",
                f"meas tran ipk{index} MAX i(L{index}) FROM={start:.12g} TO={SETTLE_S:.12g}",
                f"meas tran irms{index} RMS i(L{index}) FROM={start:.12g} TO={SETTLE_S:.12g}",
            )
        )
    lines.extend((".ic " + " ".join(initial), ".control", f"tran 10n {SETTLE_S:.12g} uic"))
    lines.extend(measures)
    lines.extend(("quit", ".endc", ".end"))
    return "\n".join(lines) + "\n"


def run() -> BoostResult:
    corner_list = tuple(corners())
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / "boost.cir"
    path.write_text(deck(corner_list), encoding="utf-8")
    completed = subprocess.run(
        ("ngspice", "-b", path.name),
        check=True,
        capture_output=True,
        text=True,
        cwd=GENERATED_DIR,
    )
    measured = {
        match.group(1): float(match.group(2))
        for match in re.finditer(r"^(\w+)\s*=\s*([-+0-9.eE]+)", completed.stdout, re.MULTILINE)
    }

    def values(prefix: str) -> tuple[float, ...]:
        return tuple(measured[f"{prefix}{index}"] for index in range(len(corner_list)))

    conservative_peak: list[float] = []
    conservative_rms: list[float] = []
    for corner in corner_list:
        average = corner.load_a * OUTPUT_V / (corner.supply_v * EFFICIENCY_FLOOR)
        ripple = (
            corner.supply_v * corner.duty
            / (corner.inductance_h * SWITCHING_HZ)
        )
        conservative_peak.append(average + ripple / 2.0)
        conservative_rms.append(sqrt(average * average + ripple * ripple / 12.0))
    return BoostResult(
        corner_list,
        values("ripple"),
        values("vout"),
        values("ipk"),
        values("irms"),
        tuple(conservative_peak),
        tuple(conservative_rms),
    )


if __name__ == "__main__":
    result = run()
    print(f"corners simulated: {len(result.corners)}")
    print(f"worst ripple: {result.worst_ripple_v * 1e3:.1f} mV pk-pk")
    print(f"worst peak: {result.worst_peak_a:.3f} A")
    print(f"worst RMS: {result.worst_rms_a:.3f} A")
    print(f"switching-model peak: {result.simulated_peak_a:.3f} A")
    print(f"switching-model RMS: {result.simulated_rms_a:.3f} A")
