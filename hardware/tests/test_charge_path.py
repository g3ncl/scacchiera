"""V3 steady-state checks on the gated USB charge path."""

import pytest

from hardware.verification.charge_path import (
    SOURCE_MAX_A,
    SWITCH_LIMIT_MAX_A,
    ChargePathBudget,
)
from hardware.verification.criteria import load_criterion


def test_switch_drop_leaves_the_module_its_supply() -> None:
    budget = ChargePathBudget()
    limit = load_criterion("HUB-CHARGE-SWITCH-DROP").limits
    assert budget.conduction_drop_v <= limit["maximum"]


def test_protection_never_fires_on_a_legitimate_load() -> None:
    budget = ChargePathBudget()
    limit = load_criterion("HUB-CHARGE-SWITCH-LIMIT-FLOOR").limits
    assert SOURCE_MAX_A <= limit["minimum"]
    assert budget.limit_headroom_a > 0.0


def test_a_worst_case_fault_is_recorded_as_exceeding_the_harness() -> None:
    """This one asserts the finding, not a pass.

    At the top of its published spread the switch passes more than the three
    contacts carrying it are rated for. Contact ratings are continuous and a
    fault in limit is not, so this is a V8 measurement rather than a static
    violation, and the test exists so the overshoot cannot quietly change size.
    """
    budget = ChargePathBudget()
    assert budget.contact_capability_a == 3.0
    assert SWITCH_LIMIT_MAX_A == 3.2
    assert budget.fault_exceeds_contacts_by_a == pytest.approx(0.2)
