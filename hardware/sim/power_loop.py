"""TPS61088 boost-loop small-signal sensitivity analysis.

The transfer functions are TI data-sheet equations 13 through 17. The error
amplifier transconductance has only a typical specification, so its plus or
minus 30 percent sweep is a sensitivity bound, not a guaranteed production
corner. This analysis selects the compensation network and catches regressions;
it does not close V3 without a guaranteed model or physical loop measurement.
"""

import cmath
from dataclasses import dataclass
from itertools import product
from math import atan, degrees, exp, inf, log, log10, pi
from typing import Callable, Iterator

from hardware.sim.power_boost import (
    CAPACITANCE_F,
    CAPACITANCE_SCALE,
    INDUCTOR_H,
    INDUCTOR_SCALE,
    LOAD_A,
    OUTPUT_ESR_OHM,
    OUTPUT_V,
    SUPPLY_V,
    SWITCHING_HZ,
)


RSENSE_OHM = 0.08
VREF_V = 1.204
ERROR_AMPLIFIER_TRANSCONDUCTANCE_S = 190e-6
ERROR_AMPLIFIER_TRANSCONDUCTANCE_SCALE = (0.70, 1.0, 1.30)
ERROR_AMPLIFIER_OUTPUT_RESISTANCE_OHM = 80e6
COMPENSATION_RESISTOR_OHM = 5.1e3
COMPENSATION_RESISTOR_SCALE = (0.99, 1.0, 1.01)
COMPENSATION_CAPACITOR_F = 22e-9
# FH specifies plus or minus 10 percent initial tolerance and X7R plus or
# minus 15 percent temperature change. The independent limits are compounded.
COMPENSATION_CAPACITOR_SCALE = (0.90 * 0.85, 1.0, 1.10 * 1.15)


@dataclass(frozen=True)
class LoopCorner:
    supply_v: float
    load_a: float
    inductance_h: float
    output_capacitance_f: float
    output_esr_ohm: float
    transconductance_s: float
    compensation_resistor_ohm: float
    compensation_capacitor_f: float

    @property
    def duty(self) -> float:
        return 1.0 - self.supply_v / OUTPUT_V

    @property
    def load_resistance_ohm(self) -> float:
        return OUTPUT_V / self.load_a

    @property
    def output_pole_hz(self) -> float:
        return 1.0 / (pi * self.load_resistance_ohm * self.output_capacitance_f)

    @property
    def esr_zero_hz(self) -> float:
        if self.output_esr_ohm == 0.0:
            return inf
        return 1.0 / (2.0 * pi * self.output_esr_ohm * self.output_capacitance_f)

    @property
    def rhp_zero_hz(self) -> float:
        return (
            self.load_resistance_ohm * (1.0 - self.duty) ** 2
            / (2.0 * pi * self.inductance_h)
        )

    @property
    def maximum_crossover_hz(self) -> float:
        return min(SWITCHING_HZ / 10.0, self.rhp_zero_hz / 5.0)


@dataclass(frozen=True)
class LoopPoint:
    corner: LoopCorner
    crossover_hz: float
    phase_margin_deg: float
    gain_margin_db: float


@dataclass(frozen=True)
class LoopResult:
    points: tuple[LoopPoint, ...]

    @property
    def minimum_phase_margin_deg(self) -> float:
        return min(point.phase_margin_deg for point in self.points)

    @property
    def minimum_gain_margin_db(self) -> float:
        return min(point.gain_margin_db for point in self.points)

    @property
    def maximum_crossover_ratio(self) -> float:
        return max(
            point.crossover_hz / point.corner.maximum_crossover_hz
            for point in self.points
        )


def corners(compensation_capacitor_f: float = COMPENSATION_CAPACITOR_F) -> Iterator[LoopCorner]:
    for supply, load, scale_l, scale_c, esr, scale_gm, scale_r, scale_comp_c in product(
        SUPPLY_V,
        LOAD_A,
        INDUCTOR_SCALE,
        CAPACITANCE_SCALE,
        OUTPUT_ESR_OHM,
        ERROR_AMPLIFIER_TRANSCONDUCTANCE_SCALE,
        COMPENSATION_RESISTOR_SCALE,
        COMPENSATION_CAPACITOR_SCALE,
    ):
        yield LoopCorner(
            supply_v=supply,
            load_a=load,
            inductance_h=INDUCTOR_H * scale_l,
            output_capacitance_f=CAPACITANCE_F * scale_c,
            output_esr_ohm=esr,
            transconductance_s=ERROR_AMPLIFIER_TRANSCONDUCTANCE_S * scale_gm,
            compensation_resistor_ohm=COMPENSATION_RESISTOR_OHM * scale_r,
            compensation_capacitor_f=compensation_capacitor_f * scale_comp_c,
        )


def loop_gain(corner: LoopCorner, frequency_hz: float) -> complex:
    """Return the equation 13 power stage times the exact series-RC impedance."""
    s = 2j * pi * frequency_hz
    plant_gain = (
        corner.load_resistance_ohm * (1.0 - corner.duty) / (2.0 * RSENSE_OHM)
    )
    esr_term = 1.0 if corner.output_esr_ohm == 0.0 else 1.0 + s / (
        2.0 * pi * corner.esr_zero_hz
    )
    plant = (
        plant_gain
        * esr_term
        * (1.0 - s / (2.0 * pi * corner.rhp_zero_hz))
        / (1.0 + s / (2.0 * pi * corner.output_pole_hz))
    )
    series_rc = corner.compensation_resistor_ohm + 1.0 / (
        s * corner.compensation_capacitor_f
    )
    compensation_impedance = 1.0 / (
        1.0 / ERROR_AMPLIFIER_OUTPUT_RESISTANCE_OHM + 1.0 / series_rc
    )
    compensator = (
        corner.transconductance_s
        * compensation_impedance
        * VREF_V
        / OUTPUT_V
    )
    return plant * compensator


def loop_phase_deg(corner: LoopCorner, frequency_hz: float) -> float:
    """Return the continuous loop phase without complex-angle wrapping."""
    esr_phase = 0.0 if corner.output_esr_ohm == 0.0 else atan(
        frequency_hz / corner.esr_zero_hz
    )
    plant_phase = (
        esr_phase
        - atan(frequency_hz / corner.rhp_zero_hz)
        - atan(frequency_hz / corner.output_pole_hz)
    )
    s = 2j * pi * frequency_hz
    series_rc = corner.compensation_resistor_ohm + 1.0 / (
        s * corner.compensation_capacitor_f
    )
    compensation_impedance = 1.0 / (
        1.0 / ERROR_AMPLIFIER_OUTPUT_RESISTANCE_OHM + 1.0 / series_rc
    )
    return degrees(plant_phase + cmath.phase(compensation_impedance))


def _log_frequency(low_hz: float, high_hz: float, fraction: float) -> float:
    exponent = log10(low_hz) + fraction * (log10(high_hz) - log10(low_hz))
    return exp(log(10.0) * exponent)


def _crossing_frequency(
    corner: LoopCorner,
    low_hz: float,
    high_hz: float,
    target: float,
    value: Callable[[LoopCorner, float], float],
) -> float:
    low_value = value(corner, low_hz) - target
    for _ in range(60):
        middle_hz = _log_frequency(low_hz, high_hz, 0.5)
        middle_value = value(corner, middle_hz) - target
        if (middle_value >= 0.0) == (low_value >= 0.0):
            low_hz = middle_hz
            low_value = middle_value
        else:
            high_hz = middle_hz
    return _log_frequency(low_hz, high_hz, 0.5)


def _magnitude(corner: LoopCorner, frequency_hz: float) -> float:
    return abs(loop_gain(corner, frequency_hz))


def _phase(corner: LoopCorner, frequency_hz: float) -> float:
    return loop_phase_deg(corner, frequency_hz)


def analyze(corner: LoopCorner) -> LoopPoint:
    frequencies = tuple(10.0 ** (-1.0 + index * 0.01) for index in range(1001))
    crossover_hz: float | None = None
    phase_crossing_hz: float | None = None
    previous_hz = frequencies[0]
    previous_magnitude = _magnitude(corner, previous_hz)
    previous_phase = _phase(corner, previous_hz)
    for frequency_hz in frequencies[1:]:
        magnitude = _magnitude(corner, frequency_hz)
        phase = _phase(corner, frequency_hz)
        if crossover_hz is None and previous_magnitude >= 1.0 > magnitude:
            crossover_hz = _crossing_frequency(
                corner, previous_hz, frequency_hz, 1.0, _magnitude
            )
        if phase_crossing_hz is None and previous_phase > -180.0 >= phase:
            phase_crossing_hz = _crossing_frequency(
                corner, previous_hz, frequency_hz, -180.0, _phase
            )
        previous_hz = frequency_hz
        previous_magnitude = magnitude
        previous_phase = phase
    if crossover_hz is None:
        raise ValueError("loop has no gain crossover between 0.1 Hz and 1 GHz")
    gain_margin_db = inf
    if phase_crossing_hz is not None:
        gain_margin_db = -20.0 * log10(_magnitude(corner, phase_crossing_hz))
    return LoopPoint(
        corner=corner,
        crossover_hz=crossover_hz,
        phase_margin_deg=180.0 + _phase(corner, crossover_hz),
        gain_margin_db=gain_margin_db,
    )


def run(compensation_capacitor_f: float = COMPENSATION_CAPACITOR_F) -> LoopResult:
    return LoopResult(tuple(analyze(corner) for corner in corners(compensation_capacitor_f)))


if __name__ == "__main__":
    result = run()
    print(f"corners analyzed: {len(result.points)}")
    print(f"minimum phase margin: {result.minimum_phase_margin_deg:.2f} degrees")
    print(f"minimum gain margin: {result.minimum_gain_margin_db:.2f} dB")
    print(f"maximum recommended-crossover ratio: {result.maximum_crossover_ratio:.3f}")
