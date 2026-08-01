"""V4 layout-derived extraction of the hub's 13.56 MHz return path."""

from pathlib import Path

import pytest

from hardware.sim.loop import loop_ac_resistance_ohm, loop_inductance_h
from hardware.sim.rf_return import FASTHENRY, PLANE_LAYER, rf_segments, return_corridor_mm


needs_fasthenry = pytest.mark.skipif(
    not Path(FASTHENRY).is_file(),
    reason=f"fasthenry not installed at {FASTHENRY}; see docs/planning.md V4",
)


@needs_fasthenry
def test_fasthenry_agrees_with_the_grover_model() -> None:
    """Validate the solver against evidence the project already trusts.

    The matrix loop has an analytical inductance from Grover's rectangle
    formula. Solving the same rectangle numerically is the check that the units,
    conductivity and discretisation in the deck are right, and it has to pass
    before any extraction the analytical model cannot do is believed.
    """
    from hardware.pcb.matrix_geometry import (
        LOOP_BREADTH,
        LOOP_LENGTH,
        LOOP_TRACE_WIDTH,
    )
    from hardware.sim.rf_return import CARRIER_HZ, COPPER_SIGMA_PER_MM, solve

    gap = 0.5
    deck = "\n".join(
        (
            "* Matrix loop, solved numerically against the Grover model.",
            ".units mm",
            f".default sigma={COPPER_SIGMA_PER_MM} nhinc=3 nwinc=5"
            f" h=0.035 w={LOOP_TRACE_WIDTH}",
            "N1 x=0 y=0 z=0",
            f"N2 x={LOOP_LENGTH} y=0 z=0",
            f"N3 x={LOOP_LENGTH} y={LOOP_BREADTH} z=0",
            f"N4 x=0 y={LOOP_BREADTH} z=0",
            f"N5 x=0 y={gap} z=0",
            "E1 N1 N2",
            "E2 N2 N3",
            "E3 N3 N4",
            "E4 N4 N5",
            ".external N1 N5",
            f".freq fmin={CARRIER_HZ} fmax={CARRIER_HZ} ndec=1",
            ".end",
            "",
        )
    )
    solved = solve(deck, "grover-crosscheck")
    assert solved.inductance_h == pytest.approx(loop_inductance_h(), rel=0.05)
    assert solved.resistance_ohm == pytest.approx(loop_ac_resistance_ohm(), rel=0.15)


def test_the_return_corridor_is_three_dielectric_thicknesses() -> None:
    # 1.0 mm board less two claddings, times three.
    assert return_corridor_mm() == pytest.approx(2.79)


def test_the_extraction_refuses_a_net_routed_on_its_own_return_layer() -> None:
    """RF_BUS is routed partly on the back layer, so it has no plane model yet.

    An earlier version of this module filtered the net to the front layer and
    extracted the remainder, which produced a confident inductance for a path
    that is not the routed path. Refusing is the honest behaviour until the
    plane is slotted where the net runs through it.
    """
    from hardware.sim.rf_return import deck

    on_plane = [s for s in rf_segments() if s.layer == PLANE_LAYER]
    assert on_plane, "expected RF_BUS to still have back-layer segments"
    with pytest.raises(NotImplementedError, match=PLANE_LAYER):
        deck(rf_segments())
