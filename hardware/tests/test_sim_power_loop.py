"""Preliminary TPS61088 loop-compensation sensitivity checks."""

from math import isinf

import pytest

from hardware.sim.power_loop import (
    COMPENSATION_CAPACITOR_F,
    LoopResult,
    corners,
    run,
)
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> LoopResult:
    return run()


def test_loop_sensitivity_covers_every_declared_corner(result: LoopResult) -> None:
    assert len(result.points) == 3 * 3 * 3 * 3 * 2 * 3 * 3 * 3
    assert len(tuple(corners())) == len(result.points)


def test_compensation_meets_the_phase_margin_target(result: LoopResult) -> None:
    minimum = load_criterion("POWER-BOOST-PHASE-MARGIN").limits["minimum"]
    assert result.minimum_phase_margin_deg > minimum


def test_compensation_meets_the_gain_margin_target(result: LoopResult) -> None:
    minimum = load_criterion("POWER-BOOST-GAIN-MARGIN").limits["minimum"]
    assert result.minimum_gain_margin_db > minimum or isinf(result.minimum_gain_margin_db)


def test_every_crossover_respects_ti_frequency_guidance(result: LoopResult) -> None:
    assert result.maximum_crossover_ratio < 1.0


def test_previous_compensation_value_has_a_low_margin_corner() -> None:
    old_result = run(4.7e-9)
    assert old_result.minimum_phase_margin_deg < 45.0
    assert COMPENSATION_CAPACITOR_F == 22e-9
