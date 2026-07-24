"""SPICE validation of the matrix switch cells against docs/hardware/criteria.yaml.

The antenna inductance and series resistance come from the routed loop
geometry (hardware/sim/loop.py reads the same constants the layout draws), so
this is the layout-derived validation the plan requires for this board.
"""

from pathlib import Path

import pytest
import yaml

from hardware.sim.matrix_rf import MatrixRfResult, run


CRITERIA = Path(__file__).parents[2] / "docs" / "hardware" / "criteria.yaml"


@pytest.fixture(scope="module")
def result() -> MatrixRfResult:
    return run()


@pytest.fixture(scope="module")
def limits() -> dict[str, dict[str, float] | float]:
    loaded: dict[str, dict[str, float] | float] = yaml.safe_load(
        CRITERIA.read_text(encoding="utf-8")
    )["matrix"]
    return loaded


def test_selected_cell_resonates_in_band(
    result: MatrixRfResult, limits: dict[str, dict[str, float] | float]
) -> None:
    band = limits["resonance_mhz"]
    assert isinstance(band, dict)
    assert band["min"] <= result.cell.resonance_hz / 1e6 <= band["max"]


def test_loaded_bus_resonates_in_band(
    result: MatrixRfResult, limits: dict[str, dict[str, float] | float]
) -> None:
    band = limits["bus_resonance_mhz"]
    assert isinstance(band, dict)
    assert band["min"] <= result.bus_resonance_hz / 1e6 <= band["max"]


def test_deselected_cell_is_suppressed(
    result: MatrixRfResult, limits: dict[str, dict[str, float] | float]
) -> None:
    floor = limits["off_on_suppression_db"]
    assert isinstance(floor, dict)
    assert result.cell.suppression_db >= floor["min"]


def test_steering_delivers_the_bias_current(
    result: MatrixRfResult, limits: dict[str, dict[str, float] | float]
) -> None:
    band = limits["bias_current_ma"]
    assert isinstance(band, dict)
    assert band["min"] <= result.bias_on_a * 1e3 <= band["max"]
    off_max = limits["bias_off_current_ua_max"]
    assert isinstance(off_max, float)
    assert result.bias_off_a * 1e6 <= off_max
