"""V3 junction-temperature bounds for every dissipating part."""

import pytest

from hardware.verification.criteria import load_criterion
from hardware.verification.junction_temperature import (
    AMBIENT_ALLOWANCE_C,
    CASES,
    POWER_BOOST,
    ThermalCase,
)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.designator)
def test_every_part_tolerates_the_ambient_allowance(case: ThermalCase) -> None:
    limit = load_criterion("THERMAL-JUNCTION-AMBIENT").limits
    assert case.maximum_ambient_c >= limit["minimum"]
    assert case.maximum_ambient_c >= AMBIENT_ALLOWANCE_C


def test_the_boost_is_the_case_that_needs_measuring() -> None:
    # Charging the whole stage's 20 percent loss floor to the controller leaves
    # it the least headroom of the five, so it is the one whose real
    # dissipation V8 has to measure rather than bound.
    assert POWER_BOOST.maximum_ambient_c == min(
        case.maximum_ambient_c for case in CASES
    )


def test_headroom_shrinks_with_dissipation() -> None:
    hotter = ThermalCase(
        POWER_BOOST.designator,
        POWER_BOOST.part,
        POWER_BOOST.dissipation_w * 1.1,
        POWER_BOOST.theta_ja_c_per_w,
        POWER_BOOST.junction_limit_c,
    )
    assert hotter.maximum_ambient_c < POWER_BOOST.maximum_ambient_c
