"""V3 derived checks on 3.3 V rail startup, dropout and hold-up."""

import pytest

from hardware.verification.criteria import load_criterion
from hardware.verification.rail_budget import INTERFACE_LOAD_A, RailBudget


def test_rail_holds_regulation_until_the_module_sags_below_the_contract() -> None:
    budget = RailBudget()
    limit = load_criterion("HUB-3V3-DROPOUT-INPUT").limits
    assert budget.dropout_input_v <= limit["maximum"]
    # Dropout has to sit below the regulated output plus something, never below
    # the output itself, or the arithmetic has lost a term.
    assert budget.dropout_input_v > 3.3


def test_soft_start_keeps_cold_start_uneventful() -> None:
    budget = RailBudget()
    limit = load_criterion("HUB-3V3-STARTUP-INRUSH").limits
    assert budget.startup_inrush_a <= limit["maximum"]


def test_dropout_worsens_with_load() -> None:
    """The margin the interface quotes is the one at its obliged load."""
    assert RailBudget(load_a=2.0).dropout_input_v > RailBudget().dropout_input_v
    assert RailBudget().load_a == INTERFACE_LOAD_A


def test_hold_up_is_too_short_to_ride_anything_out() -> None:
    """Recorded so nobody designs around capacitance that is not there.

    Five microseconds means the rail follows its input. Riding out a source
    change is the power module's job, which is why the interface demands
    uninterrupted handover and V8 measures it.
    """
    assert RailBudget().hold_up_s == pytest.approx(5e-6, rel=0.1)
