"""V3 validation of the 3.3 V buck's power stage over published tolerances."""

import pytest

from hardware.sim.hub_buck import (
    INDUCTOR_RMS_A,
    INDUCTOR_SAT_A,
    LOAD_A,
    BuckResult,
    corners,
    run,
)
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> BuckResult:
    return run()


def test_ripple_stays_inside_the_mcu_supply_budget(result: BuckResult) -> None:
    limit = load_criterion("HUB-3V3-RIPPLE").limits
    assert result.worst_ripple_v <= limit["maximum"]
    # A stage that produced no ripple would mean the switching was not being
    # simulated at all, which would make every other number here meaningless.
    assert result.worst_ripple_v > 0.0


def test_peak_current_stays_below_the_converter_current_limit(
    result: BuckResult,
) -> None:
    limit = load_criterion("HUB-3V3-INDUCTOR-PEAK").limits
    assert result.worst_peak_a <= limit["maximum"]
    # The converter's own limit binds before the inductor saturates; both hold.
    assert result.worst_peak_a < INDUCTOR_SAT_A


def test_rms_current_stays_within_the_inductor_rating(result: BuckResult) -> None:
    limit = load_criterion("HUB-3V3-INDUCTOR-RMS").limits
    assert result.worst_rms_a <= limit["maximum"]
    assert result.worst_rms_a < INDUCTOR_RMS_A


def test_peak_current_exceeds_the_load_it_carries(result: BuckResult) -> None:
    """Peak has to sit above the DC load by half the ripple current.

    Equal values would mean the inductor ripple was missing from the result.
    """
    for corner, peak in zip(result.corners, result.peak_a, strict=True):
        assert peak > corner.load_a


def test_every_published_tolerance_is_swept(result: BuckResult) -> None:
    assert len(result.corners) == 3 * 3 * 2 * len(LOAD_A)
    assert len(tuple(corners())) == len(result.corners)
    assert {corner.load_a for corner in result.corners} == set(LOAD_A)
    assert {corner.supply_v for corner in result.corners} == {4.5, 5.0, 5.5}
    # Both bounds on effective output capacitance, since the part's data sheet
    # prints only example bias curves and the low bound is the pessimistic one.
    assert {corner.capacitor_scale for corner in result.corners} == {0.5, 1.0}
