"""V3 polarity and loss checks for the power-board cell input."""

import pytest

from hardware.sim.reverse_battery import (
    PASS_FET_HOT_RDS_OHM,
    ReverseBatteryCase,
    hot_pass_fet_loss_w,
    minimum_correct_polarity_margin_v,
    run_case,
)


@pytest.mark.parametrize("cell_v", (2.87, 3.6, 4.2))
def test_correct_cell_has_large_worst_case_comparator_margin(cell_v: float) -> None:
    assert minimum_correct_polarity_margin_v(cell_v) > 1.1


@pytest.mark.parametrize("adapter_present", (False, True))
def test_correct_cell_bootstraps_and_enables_pass_fet(adapter_present: bool) -> None:
    result = run_case(ReverseBatteryCase(f"correct_{adapter_present}", 2.87, adapter_present))
    assert result.gate_control_final_v > 0.9
    assert result.raw_final_v > 2.7


@pytest.mark.parametrize("adapter_present", (False, True))
def test_reversed_cell_never_enables_pass_fet(adapter_present: bool) -> None:
    result = run_case(ReverseBatteryCase(f"reversed_{adapter_present}", -4.2, adapter_present))
    assert result.gate_control_final_v < 0.1
    if adapter_present:
        assert result.raw_min_v > 4.0
        assert result.cell_final_v < -4.0
    else:
        assert result.raw_max_v < 0.01


def test_hot_pass_fet_loss_is_below_half_a_watt() -> None:
    assert PASS_FET_HOT_RDS_OHM < 0.017
    assert hot_pass_fet_loss_w() < 0.35
