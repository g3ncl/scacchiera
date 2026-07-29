"""V3 validation of the light-bar rail's current limit on TI's own model."""

import pytest

from hardware.sim.hub_led_rail import BAR_LOAD_A, RailResult, corners, run
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> RailResult:
    return run()


def test_rail_carries_both_bars_without_tripping(result: RailResult) -> None:
    """A bright cue is not a fault. The limiter has to pass the real load."""
    floor = load_criterion("HUB-LED-RAIL-TRIP-FLOOR").limits
    assert result.lowest_limit_a >= floor["minimum"]
    assert result.lowest_limit_a > BAR_LOAD_A
    # Both bars white must actually reach the bars, not a limited fraction.
    for current in result.normal_a:
        assert current == pytest.approx(BAR_LOAD_A, rel=0.05)


def test_a_shorted_bar_harness_stays_inside_the_contact_rating(
    result: RailResult,
) -> None:
    ceiling = load_criterion("HUB-LED-RAIL-FAULT-CEILING").limits
    assert result.highest_limit_a <= ceiling["maximum"]


def test_the_rail_reaches_the_bars_at_the_lowest_module_output(
    result: RailResult,
) -> None:
    """The switch drop comes off the bottom of the module's output range."""
    assert result.worst_rail_v >= 4.4


def test_both_resistor_extremes_and_the_supply_range_are_simulated(
    result: RailResult,
) -> None:
    assert len(result.corners) == 6
    assert len(tuple(corners())) == len(result.corners)
    assert {corner.supply_v for corner in result.corners} == {4.5, 5.0, 5.5}
    # A limit that did not move with its programming resistor would mean the
    # model was ignoring it, which would make the whole bench vacuous.
    assert result.highest_limit_a > result.lowest_limit_a
