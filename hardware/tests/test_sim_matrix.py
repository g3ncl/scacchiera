"""SPICE validation of the matrix switch cells against docs/hardware/criteria.yaml.

The antenna inductance and series resistance come from the routed loop
geometry (hardware/sim/loop.py reads the same constants the layout draws), so
this is the layout-derived validation the plan requires for this board.
"""

import pytest

from hardware.sim.matrix_rf import MatrixRfResult, run
from hardware.verification.criteria import load_criterion


@pytest.fixture(scope="module")
def result() -> MatrixRfResult:
    return run()


def test_selected_cell_resonates_in_band(result: MatrixRfResult) -> None:
    band = load_criterion("MATRIX-CELL-RESONANCE").limits
    assert band["minimum"] <= result.cell.resonance_hz / 1e6 <= band["maximum"]


def test_loaded_bus_resonates_in_band(result: MatrixRfResult) -> None:
    band = load_criterion("MATRIX-BUS-RESONANCE").limits
    assert band["minimum"] <= result.bus_resonance_hz / 1e6 <= band["maximum"]


def test_deselected_cell_is_suppressed(result: MatrixRfResult) -> None:
    floor = load_criterion("MATRIX-OFF-ON-SUPPRESSION").limits
    assert result.cell.suppression_db >= floor["minimum"]


def test_steering_delivers_the_bias_current(result: MatrixRfResult) -> None:
    band = load_criterion("MATRIX-BIAS-CURRENT").limits
    assert band["minimum"] <= result.bias_on_a * 1e3 <= band["maximum"]
    off_limit = load_criterion("MATRIX-OFF-BIAS-CURRENT").limits
    assert result.bias_off_a * 1e6 <= off_limit["maximum"]
