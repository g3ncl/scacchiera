"""SPICE validation of the hub reader front end against criteria.yaml."""

import pytest

from hardware.sim.hub_front_end import FrontEndResult, run
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> FrontEndResult:
    return run()


def test_front_end_drives_the_loaded_bus_in_band(result: FrontEndResult) -> None:
    band = load_criterion("HUB-SYSTEM-RESONANCE").limits
    current = load_criterion("HUB-COIL-CURRENT-PER-VOLT").limits
    assert band["minimum"] <= result.resonance_hz / 1e6 <= band["maximum"]
    assert result.coil_a * 1e3 >= current["minimum"]
