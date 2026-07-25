"""SPICE validation of the light bar against docs/hardware/criteria.yaml."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from hardware.pcb.lightbar_geometry import LED_COUNT
from hardware.sim.lightbar_supply import validate_supply
from hardware.verification.criteria import load_criterion


ROOT = Path(__file__).parent.parent.parent
BOARD = ROOT / "hardware" / "pcb" / "generated" / "lightbar" / "lightbar.kicad_pcb"
WORK_DIR = ROOT / "hardware" / "sim" / "generated" / "lightbar"


@pytest.fixture(scope="session")
def routed_board() -> Path:
    # A bare pytest run regenerates the board; `make check` has already built
    # it through the schematic and layout targets.
    if not BOARD.exists():
        subprocess.run(
            (sys.executable, "-m", "hardware.pcb.generate", "lightbar"),
            check=True,
            cwd=ROOT,
            env=os.environ,
        )
        subprocess.run(
            ("/usr/bin/python3", "-m", "hardware.pcb.lightbar_layout"),
            check=True,
            cwd=ROOT,
            env=os.environ,
        )
    return BOARD


def test_supply_loop_droop_within_criteria(routed_board: Path) -> None:
    limits = load_criterion("LB-SUPPLY-DROOP").limits
    result = validate_supply(routed_board, WORK_DIR)
    assert len(result.droops_v) == LED_COUNT
    # A solved network with zero droop would mean the extraction found no
    # copper resistance, so guard against a vacuous pass too.
    assert result.worst_droop_v > 0.0
    assert result.worst_droop_v <= limits["maximum"]
