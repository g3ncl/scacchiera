"""V3 coincident worst-case load on the power module."""

from hardware.verification.criteria import load_criterion
from hardware.verification.load_budget import LIGHTBAR_A, MCU_PEAK_A, LoadBudget


def test_everything_at_once_stays_inside_the_module_obligation() -> None:
    budget = LoadBudget()
    limit = load_criterion("HUB-MODULE-LOAD-BUDGET").limits
    assert budget.module_total_a <= limit["maximum"]


def test_the_budget_is_a_sum_of_its_rails_not_a_single_load() -> None:
    """Guards the shape: the light bars sit on 5 V, everything else behind the buck."""
    budget = LoadBudget()
    assert budget.module_total_a > LIGHTBAR_A
    assert budget.rail_3v3_a > MCU_PEAK_A
    # Reflecting 3.3 V through a lossy converter draws less current than the
    # rail itself, or the conversion has been applied the wrong way round.
    assert budget.rail_3v3_reflected_a < budget.rail_3v3_a


def test_the_display_share_is_visible() -> None:
    assert 0.45 < LoadBudget().display_fraction < 0.50
