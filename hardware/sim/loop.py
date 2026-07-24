"""Inductance and AC resistance of the single-turn line-antenna loop.

Computed from the same `matrix_geometry` constants the layout draws the copper
from, so the simulated antenna is the routed antenna, not a free parameter.
"""

from math import exp, log, pi, sqrt

from hardware.pcb.matrix_geometry import LOOP_BREADTH, LOOP_LENGTH, LOOP_TRACE_WIDTH
from hardware.sim.copper import COPPER_RESISTIVITY_OHM_M, COPPER_THICKNESS_M


MU0 = 4e-7 * pi
CARRIER_HZ = 13.56e6
# Grover's equivalent round-wire radius for a thin rectangular conductor.
_EQUIVALENT_RADIUS_M = 0.2235 * (LOOP_TRACE_WIDTH / 1000.0 + COPPER_THICKNESS_M)


def loop_inductance_h() -> float:
    """Grover's formula for a rectangular loop of sides a, b.

    The internal-inductance term is dropped: at 13.56 MHz skin effect pushes
    the current to the surface, so the external inductance is the value.
    """
    a = LOOP_LENGTH / 1000.0
    b = LOOP_BREADTH / 1000.0
    r = _EQUIVALENT_RADIUS_M
    diagonal = sqrt(a * a + b * b)
    return (MU0 / pi) * (
        a * log(2.0 * a * b / (r * (a + diagonal)))
        + b * log(2.0 * a * b / (r * (b + diagonal)))
        + 2.0 * diagonal
        - 2.0 * (a + b)
    )


def loop_ac_resistance_ohm() -> float:
    """Series resistance of the loop at the carrier, skin effect included.

    Both faces of the trace conduct, so the effective thickness saturates at
    twice the skin depth as frequency rises.
    """
    perimeter_m = 2.0 * (LOOP_LENGTH + LOOP_BREADTH) / 1000.0
    skin_depth_m = sqrt(COPPER_RESISTIVITY_OHM_M / (pi * CARRIER_HZ * MU0))
    effective_thickness_m = (
        2.0 * skin_depth_m * (1.0 - exp(-COPPER_THICKNESS_M / (2.0 * skin_depth_m)))
    )
    return COPPER_RESISTIVITY_OHM_M * perimeter_m / (
        (LOOP_TRACE_WIDTH / 1000.0) * effective_thickness_m
    )
