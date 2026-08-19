"""V3 rail sequencing: what a cross-rail signal does while its rail is down."""

import pytest

from hardware.verification.criteria import load_criterion
from hardware.verification.rail_sequencing import (
    CROSSINGS,
    Crossing,
    crossing_nets,
)


def test_every_crossing_in_the_schematic_is_classified() -> None:
    # A new signal between two differently powered parts has to be looked at
    # rather than inherited, so the schematic and the table must agree exactly.
    assert crossing_nets() == tuple(sorted(crossing.net for crossing in CROSSINGS))


@pytest.mark.parametrize("crossing", CROSSINGS, ids=lambda crossing: crossing.net)
def test_no_crossing_pushes_more_than_the_injection_ceiling(
    crossing: Crossing,
) -> None:
    limit = load_criterion("HUB-SEQUENCING-PIN-INJECTION").limits
    assert crossing.injected_current_a <= limit["maximum"]


def test_only_one_crossing_lands_on_a_pin_its_data_sheet_does_not_cover() -> None:
    # Three are rated against ground, which makes the case a non-event, and the
    # enable shares its supply with the driver. The AP22811's fault flag is the
    # one condition no filed document permits, so it is the one bounded by a
    # resistor instead.
    unbounded = tuple(
        crossing.net for crossing in CROSSINGS if crossing.injected_current_a > 0.0
    )
    assert unbounded == ("CHARGE_INPUT_FAULT_N",)


def test_a_weaker_pull_would_inject_more() -> None:
    flag = next(
        crossing
        for crossing in CROSSINGS
        if crossing.net == "CHARGE_INPUT_FAULT_N"
    )
    stronger = Crossing(
        flag.net, flag.receiver, flag.rated_against_ground, 10e3, flag.note
    )
    assert stronger.injected_current_a > flag.injected_current_a
