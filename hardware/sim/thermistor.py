"""Vishay R/T curve for the cell thermistor, as filed in the vault.

The NTCLE317E4103SBA data sheet publishes R25, B25/85 and R85 but no R/T table.
The coefficients below come from Vishay's own curve document for this part's
ceramic material, filed as
`Vault/Scacchiera/Datasheets/NTCLE317E4103SBA_C3154341_rt-curve.md`. They
reproduce both resistances the part data sheet does publish, so the curve is
anchored to the immutable source rather than to a single-beta approximation
(which errs by 0.8 K at 0 degrees Celsius, most of the cold cutoff's margin).
"""

from dataclasses import dataclass
from math import exp, log


R25_OHM = 10000.0
KELVIN_OFFSET = 273.15

# Sheet "dbase ceramic types" row 10, mat A. with Bn=3984K.
CURVE_A = -14.65719769
CURVE_B = 4798.842
CURVE_C = -115334.0
CURVE_D = -3730535.0

# Quick Reference Data: accuracy of the delivered temperature, not of one
# resistance reading. It already carries the R25 and B tolerances, so a corner
# sweep must not also perturb R25 or it would count the same error twice.
ACCURACY_25_TO_85_K = 0.5
ACCURACY_FULL_RANGE_K = 1.0

# Quick Reference Data: 0.8 mW/K in still air.
DISSIPATION_MW_PER_K = 0.8


@dataclass(frozen=True)
class SelfHeating:
    """Sensor error from its own bias current, at one operating point."""

    power_w: float
    rise_k: float


def resistance_ohm(celsius: float) -> float:
    kelvin = celsius + KELVIN_OFFSET
    exponent = (
        CURVE_A
        + CURVE_B / kelvin
        + CURVE_C / kelvin**2
        + CURVE_D / kelvin**3
    )
    return R25_OHM * exp(exponent)


def celsius(resistance: float) -> float:
    """Invert the curve by bisection rather than by the published inverse form.

    One curve in one direction cannot disagree with itself, and the bracket
    covers the sensor's whole published operating range.
    """
    low, high = -55.0, 150.0
    if not resistance_ohm(high) <= resistance <= resistance_ohm(low):
        raise ValueError(f"{resistance} ohm is outside the sensor's published range")
    for _ in range(200):
        middle = (low + high) / 2.0
        if resistance_ohm(middle) > resistance:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def accuracy_k(celsius_point: float) -> float:
    """Published sensor accuracy at a temperature, the tighter band where it applies."""
    if 25.0 <= celsius_point <= 85.0:
        return ACCURACY_25_TO_85_K
    return ACCURACY_FULL_RANGE_K


def self_heating(celsius_point: float, bias_v: float, series_ohm: float) -> SelfHeating:
    """Bias-current heating of the bead, which reads as a false warm offset."""
    sensor_ohm = resistance_ohm(celsius_point)
    current = bias_v / (series_ohm + sensor_ohm)
    power = current**2 * sensor_ohm
    return SelfHeating(power_w=power, rise_k=power * 1e3 / DISSIPATION_MW_PER_K)


def spice_expression(temperature_node: str) -> str:
    """The curve as an ngspice behavioral resistance driven by a temperature node.

    One volt on the node is one degree Celsius, so a DC sweep of that node is a
    temperature sweep of the sensor.
    """
    kelvin = f"(V({temperature_node})+{KELVIN_OFFSET})"
    return (
        f"{R25_OHM:.1f}*exp({CURVE_A:.8f}"
        f"+{CURVE_B:.3f}/{kelvin}"
        f"+({CURVE_C:.1f})/({kelvin}*{kelvin})"
        f"+({CURVE_D:.1f})/({kelvin}*{kelvin}*{kelvin}))"
    )
