"""V3 corner and fault validation of the hub's cell-temperature charge gate."""

import pytest

from hardware.sim.hub_interlock import (
    FUNCTIONAL_CHARGE_C,
    GATE_PARTS,
    InterlockResult,
    corners,
    run,
)
from hardware.sim.thermistor import celsius, resistance_ohm
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> InterlockResult:
    return run()


def test_curve_reproduces_the_filed_datasheet_values() -> None:
    """The R/T curve is only usable evidence while it matches the part data sheet.

    Quick Reference Data gives 10 kohm at 25 degrees and 1066.1 ohm at 85, the
    only two points the immutable source publishes.
    """
    assert resistance_ohm(25.0) == pytest.approx(10000.0, abs=0.5)
    assert resistance_ohm(85.0) == pytest.approx(1066.1, abs=0.5)
    assert celsius(resistance_ohm(0.0)) == pytest.approx(0.0, abs=0.01)


def test_gate_never_permits_charging_outside_the_qualified_range(
    result: InterlockResult,
) -> None:
    cold_limit = load_criterion("POWER-CHARGE-TEMPERATURE-MIN").limits
    hot_limit = load_criterion("POWER-CHARGE-TEMPERATURE-MAX").limits
    coldest, hottest = result.widest
    assert coldest >= cold_limit["minimum"]
    assert hottest <= hot_limit["maximum"]
    # Guard against a vacuous pass: a gate stuck inhibited would also satisfy
    # both limits, so the window has to be a real window.
    assert coldest < hottest


def test_gate_still_permits_charging_across_the_functional_band(
    result: InterlockResult,
) -> None:
    cold_edge = load_criterion("HUB-INTERLOCK-BAND-COLD").limits
    hot_edge = load_criterion("HUB-INTERLOCK-BAND-HOT").limits
    tightest_cold, tightest_hot = result.narrowest
    assert tightest_cold <= cold_edge["maximum"]
    assert tightest_hot >= hot_edge["minimum"]
    assert tightest_cold < FUNCTIONAL_CHARGE_C < tightest_hot


def test_enable_pin_reaches_both_switch_logic_levels(result: InterlockResult) -> None:
    high = load_criterion("HUB-INTERLOCK-ENABLE-HIGH").limits
    low = load_criterion("HUB-INTERLOCK-ENABLE-LOW").limits
    assert result.enable_high_v >= high["minimum"]
    assert result.enable_low_v <= low["maximum"]


def test_a_lost_sensor_inhibits_charging_in_both_failure_directions(
    result: InterlockResult,
) -> None:
    limit = load_criterion("HUB-INTERLOCK-FAULT-ENABLE").limits
    assert set(result.fault_enable_v) == {"open", "short"}
    for level in result.fault_enable_v.values():
        assert level <= limit["maximum"]


def test_every_corner_of_the_tolerance_box_is_simulated(result: InterlockResult) -> None:
    """The corner set is the evidence, so its shape is worth asserting.

    Three supplies times two comparator-error directions times both extremes of
    six independent resistance groups.
    """
    assert len(result.thresholds) == 3 * 2 * 2**6
    assert len(tuple(corners())) == len(result.thresholds)
    assert GATE_PARTS == {
        "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "C17", "U2",
    }
