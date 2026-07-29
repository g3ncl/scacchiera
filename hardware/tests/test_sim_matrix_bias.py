"""V3 sweep of the matrix bias current against its choke's absolute maximum."""

import pytest

from hardware.sim.matrix_bias import CHOKE_RATED_A, BiasResult, corners, run
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> BiasResult:
    return run()


def test_bias_never_reaches_the_choke_rating(result: BiasResult) -> None:
    limit = load_criterion("MATRIX-BIAS-CHOKE-RATING").limits
    assert result.highest_a * 1e3 <= limit["maximum"]
    assert result.highest_a < CHOKE_RATED_A


def test_bias_stays_inside_the_band_the_design_aims_for(result: BiasResult) -> None:
    band = load_criterion("MATRIX-BIAS-CURRENT").limits
    assert band["minimum"] <= result.lowest_a * 1e3
    assert result.highest_a * 1e3 <= band["maximum"]


def test_the_sweep_moves_the_current(result: BiasResult) -> None:
    """A bias that ignored its rail and resistor would make the sweep vacuous."""
    assert len(result.corners) == 6
    assert len(tuple(corners())) == len(result.corners)
    assert result.highest_a > result.lowest_a
