"""V3 temperature corners for the inductors and the conduction path they sit in."""

import pytest

from hardware.verification.criteria import load_criterion
from hardware.verification.junction_temperature import AMBIENT_ALLOWANCE_C
from hardware.verification.temperature_corners import (
    COILS,
    HUB_BUCK_COIL,
    InductorThermal,
    hot_dropout_input_v,
)


@pytest.mark.parametrize("coil", COILS, ids=lambda coil: coil.designator)
def test_every_coil_tolerates_the_ambient_allowance(coil: InductorThermal) -> None:
    limit = load_criterion("THERMAL-INDUCTOR-AMBIENT").limits
    assert coil.maximum_ambient_c >= limit["minimum"]
    assert coil.maximum_ambient_c >= AMBIENT_ALLOWANCE_C


def test_a_coil_at_its_rating_sits_exactly_at_the_rated_rise() -> None:
    # The data sheet fixes one point on the curve, so this is what says the
    # square law is anchored where the manufacturer put it and not elsewhere.
    at_rating = InductorThermal(
        HUB_BUCK_COIL.designator,
        HUB_BUCK_COIL.part,
        HUB_BUCK_COIL.rated_rms_a,
        HUB_BUCK_COIL.rated_rms_a,
        HUB_BUCK_COIL.dcr_20c_ohm,
    )
    assert at_rating.self_rise_c == pytest.approx(40.0)
    assert at_rating.maximum_ambient_c == pytest.approx(85.0)


def test_a_hot_coil_still_leaves_the_dropout_inside_the_interface_floor() -> None:
    limit = load_criterion("HUB-3V3-DROPOUT-INPUT").limits
    assert hot_dropout_input_v() <= limit["maximum"]


def test_the_coil_costs_only_millivolts_of_that_floor() -> None:
    cold = hot_dropout_input_v(ambient_c=20.0 - HUB_BUCK_COIL.self_rise_c)
    assert 0.0 < hot_dropout_input_v() - cold < 0.010
