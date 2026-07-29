"""V3 checks for the hub's passive 5 V Type-C current recognition."""

import pytest

from hardware.verification.criteria import load_criterion
from hardware.verification.typec_current import TypeCCurrent, advertised_current


@pytest.mark.parametrize(
    ("cc1_v", "cc2_v", "expected"),
    (
        (0.0, 0.0, TypeCCurrent.DETACHED),
        (0.25, 0.0, TypeCCurrent.DEFAULT),
        (0.61, 0.0, TypeCCurrent.DEFAULT),
        (0.69, 0.0, TypeCCurrent.A1_5),
        (1.16, 0.0, TypeCCurrent.A1_5),
        (1.30, 0.0, TypeCCurrent.A3_0),
        (2.04, 0.0, TypeCCurrent.A3_0),
        (0.0, 1.30, TypeCCurrent.A3_0),
        (2.05, 0.0, TypeCCurrent.DETACHED),
    ),
)
def test_current_classes_are_conservative(
    cc1_v: float, cc2_v: float, expected: TypeCCurrent,
) -> None:
    assert advertised_current(cc1_v, cc2_v) is expected


def test_undefined_voltage_gaps_resolve_to_the_lower_current() -> None:
    assert advertised_current(0.65, 0.0) is TypeCCurrent.DEFAULT
    assert advertised_current(1.20, 0.0) is TypeCCurrent.A1_5


def test_thresholds_match_the_recorded_standard_evidence() -> None:
    limits = load_criterion("HUB-TYPEC-CURRENT-ADVERTISEMENT").limits
    assert limits == {
        "connect_minimum": 0.25,
        "default_maximum": 0.66,
        "current_1_5_maximum": 1.23,
        "connected_maximum": 2.04,
    }
