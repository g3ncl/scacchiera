"""SPICE validation of the light bar against docs/hardware/criteria.yaml."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from hardware.sim.lightbar_supply import validate_supply


ROOT = Path(__file__).parent.parent.parent
BOARD = ROOT / "hardware" / "pcb" / "generated" / "lightbar" / "lightbar.kicad_pcb"
CRITERIA = ROOT / "docs" / "hardware" / "criteria.yaml"
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
    limits = yaml.safe_load(CRITERIA.read_text(encoding="utf-8"))["lightbar"]
    result = validate_supply(routed_board, WORK_DIR)
    assert len(result.droops_v) == 17
    # A solved network with zero droop would mean the extraction found no
    # copper resistance, so guard against a vacuous pass too.
    assert result.worst_droop_v > 0.0
    assert result.worst_droop_v <= limits["supply_loop_droop_v_max"]
