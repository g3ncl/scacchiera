"""SPICE validation of the hub reader front end against criteria.yaml."""

from pathlib import Path

import pytest
import yaml

from hardware.sim.hub_front_end import FrontEndResult, run


CRITERIA = Path(__file__).parents[2] / "docs" / "hardware" / "criteria.yaml"


@pytest.fixture(scope="module")
def result() -> FrontEndResult:
    return run()


def test_front_end_drives_the_loaded_bus_in_band(result: FrontEndResult) -> None:
    limits = yaml.safe_load(CRITERIA.read_text(encoding="utf-8"))["hub"]
    band = limits["system_resonance_mhz"]
    assert band["min"] <= result.resonance_hz / 1e6 <= band["max"]
    assert result.coil_a * 1e3 >= limits["coil_ma_per_volt_min"]
