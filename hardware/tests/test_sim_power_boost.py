"""V3 validation of the 10 W boost stage over published tolerances."""

import pytest

from hardware.sim.power_boost import (
    BATFET_OCP_A,
    BATFET_RMS_A,
    CAPACITANCE_MAX_F,
    CAPACITANCE_MIN_F,
    CURRENT_LIMIT_FLOOR_A,
    INDUCTOR_RMS_A,
    INDUCTOR_SAT_A,
    LOAD_A,
    OUTPUT_ESR_OHM,
    BoostResult,
    corners,
    run,
)
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> BoostResult:
    return run()


def test_full_power_stays_below_the_guaranteed_current_limit(result: BoostResult) -> None:
    limit = load_criterion("POWER-BOOST-INDUCTOR-PEAK").limits
    assert result.worst_peak_a <= limit["maximum"]
    assert result.worst_peak_a < CURRENT_LIMIT_FLOOR_A
    assert result.worst_peak_a < INDUCTOR_SAT_A
    assert result.worst_peak_a < BATFET_OCP_A


def test_rms_current_fits_the_inductor_and_charger_path(result: BoostResult) -> None:
    limit = load_criterion("POWER-BOOST-INDUCTOR-RMS").limits
    assert result.worst_rms_a <= limit["maximum"]
    assert result.worst_rms_a < INDUCTOR_RMS_A
    assert result.worst_rms_a < BATFET_RMS_A


def test_output_ripple_stays_inside_the_interface_budget(result: BoostResult) -> None:
    limit = load_criterion("POWER-BOOST-RIPPLE").limits
    assert 0.0 < result.worst_ripple_v <= limit["maximum"]


def test_assembled_output_bank_esr_limit_is_swept(result: BoostResult) -> None:
    limit = load_criterion("POWER-BOOST-OUTPUT-ESR").limits
    assert max(OUTPUT_ESR_OHM) == limit["maximum"]
    assert any(corner.output_esr_ohm == limit["maximum"] for corner in result.corners)


def test_feedback_tolerances_keep_the_output_in_range() -> None:
    limit = load_criterion("POWER-BOOST-OUTPUT-VOLTAGE").limits
    minimum = 1.186 * (1.0 + 124.9 * 0.99 / (39.0 * 1.01))
    maximum = 1.222 * (1.0 + 124.9 * 1.01 / (39.0 * 0.99))
    assert limit["minimum"] <= minimum
    assert maximum <= limit["maximum"]


def test_every_published_power_stage_corner_is_swept(result: BoostResult) -> None:
    assert len(result.corners) == 3 * 3 * 3 * 2 * len(LOAD_A)
    assert len(tuple(corners())) == len(result.corners)
    assert {corner.supply_v for corner in result.corners} == {2.87, 3.6, 4.2}
    assert {corner.inductor_scale for corner in result.corners} == {0.7, 1.0, 1.2}
    assert sorted({corner.capacitance_f for corner in result.corners}) == pytest.approx(
        sorted((CAPACITANCE_MIN_F, 67e-6, CAPACITANCE_MAX_F))
    )
    assert {corner.output_esr_ohm for corner in result.corners} == set(OUTPUT_ESR_OHM)


def test_simulation_holds_the_intended_operating_point(result: BoostResult) -> None:
    assert min(result.output_v) >= 4.90
    assert max(result.output_v) <= 5.10


def test_efficiency_bound_is_more_conservative_than_the_switching_stage(
    result: BoostResult,
) -> None:
    assert result.worst_peak_a > result.simulated_peak_a
    assert result.worst_rms_a > result.simulated_rms_a
