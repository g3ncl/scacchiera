"""What splitting the sensing plane onto two substrates does to the coupling.

The row-and-column architecture rests on rows and columns being decoupled from
each other, and on adjacent lines being decoupled enough that a tag over one
does not answer on its neighbour. `test_antenna_coupling.py` establishes both
for the monolithic board. This establishes that the split does not spend them.

Both extractions run through the same solver on the same loop path, so a
difference here is a difference in stackup and nothing else.
"""

from pathlib import Path

import pytest
import yaml

from hardware.pcb.matrix_geometry import LINE_COUNT, ROW_COUNT
from hardware.sim.antenna_coupling import Coupling
from hardware.sim.antenna_coupling import extract as extract_monolith
from hardware.sim.strip_stack import extract as extract_split
from hardware.sim.strip_stack import plane_separation_mm


CRITERIA = yaml.safe_load(
    (Path(__file__).parent.parent.parent / "docs" / "hardware" / "criteria.yaml").read_text()
)["criteria"]


def _limit(name: str, bound: str) -> float:
    return float(CRITERIA[name]["limits"][bound])


@pytest.fixture(scope="module")
def split() -> Coupling:
    return extract_split()


@pytest.fixture(scope="module")
def monolith() -> Coupling:
    return extract_monolith()


def _worst_adjacent(coupling: Coupling) -> float:
    return max(
        coupling.coupling_coefficient(index, index + 1)
        for index in range(LINE_COUNT - 1)
        if index != ROW_COUNT - 1
    )


def _worst_crossing(coupling: Coupling) -> float:
    return max(
        coupling.coupling_coefficient(row, column)
        for row in range(ROW_COUNT)
        for column in range(ROW_COUNT, LINE_COUNT)
    )


def test_the_planes_land_where_the_stackup_says() -> None:
    """TEST-STRIP-RF-001."""
    separation = plane_separation_mm()
    assert _limit("STRIP-PLANE-SEPARATION", "minimum") <= separation <= _limit(
        "STRIP-PLANE-SEPARATION", "maximum"
    )


def test_a_row_and_a_column_stay_decoupled(split: Coupling) -> None:
    """TEST-STRIP-RF-002.

    The claim the whole architecture rests on, re-established on the split
    stackup rather than inherited from the monolith's.
    """
    assert _worst_crossing(split) <= _limit("STRIP-ROW-COLUMN-COUPLING", "maximum")


def test_adjacent_lines_are_no_worse_than_the_monolith(split: Coupling, monolith: Coupling) -> None:
    """TEST-STRIP-RF-003.

    Adjacent lines share a plane, so separating the planes cannot move this.
    Asserting equality rather than a bound is what would catch the split having
    quietly changed the in-plane geometry, which is the failure that matters.
    """
    assert _worst_adjacent(split) <= _limit("STRIP-ADJACENT-LINE-COUPLING", "maximum")
    assert _worst_adjacent(split) == pytest.approx(_worst_adjacent(monolith), abs=1e-4)


def test_the_split_does_not_couple_harder_than_the_board_it_replaces(split: Coupling, monolith: Coupling) -> None:
    """The comparison the partition has to win, or at least not lose.

    Splitting onto two substrates puts the planes 1.035 mm apart against the
    monolith's 0.965, so the crossing coupling should come out slightly lower.
    If it ever came out higher, the stackup would have moved the planes closer
    and the read budget would be being spent without anyone saying so.
    """
    assert _worst_crossing(split) <= _worst_crossing(monolith)


def test_the_loops_themselves_are_untouched(split: Coupling, monolith: Coupling) -> None:
    """Same copper, same self inductance. The split moves boards, not antennas."""
    for line in range(LINE_COUNT):
        assert split.inductance_h[line] == pytest.approx(
            monolith.inductance_h[line], rel=2e-3
        )
