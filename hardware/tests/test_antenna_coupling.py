"""Layout-derived antenna extraction for V4.

The row-and-column architecture assumes a tag's square is the intersection of
the one row and the one column that both read it. That rests on two physical
claims nothing had ever checked: that the sixteen lines are interchangeable,
and that a row and a column are effectively decoupled from each other.

FastHenry is validated against the Grover model in `test_rf_return.py` before
being trusted here.
"""

import pytest
import yaml

from hardware.pcb.matrix_geometry import LINE_COUNT, ROW_COUNT
from hardware.sim.antenna_coupling import Coupling, extract

from pathlib import Path


CRITERIA = yaml.safe_load(
    (Path(__file__).parent.parent.parent / "docs" / "hardware" / "criteria.yaml").read_text()
)["criteria"]


@pytest.fixture(scope="module")
def coupling() -> Coupling:
    return extract()


def _limit(name: str, bound: str) -> float:
    return float(CRITERIA[name]["limits"][bound])


def test_self_inductance_agrees_with_the_analytical_loop(coupling: Coupling) -> None:
    """`hardware/sim/loop.py` gives 590 nH from Grover on the same geometry.

    Two independent methods on one shape. Disagreement would mean the extraction
    geometry has drifted from the board, which is the failure this catches.
    """
    for line in range(LINE_COUNT):
        nanohenry = coupling.inductance_h[line] * 1e9
        assert _limit("MATRIX-ANTENNA-INDUCTANCE", "minimum") <= nanohenry <= _limit(
            "MATRIX-ANTENNA-INDUCTANCE", "maximum"
        ), f"line {line} at {nanohenry:.1f} nH"


def test_every_line_is_interchangeable(coupling: Coupling) -> None:
    """A scan treats all sixteen lines the same, so they must behave the same.

    A spread here would mean one square reads differently from its neighbour
    for reasons that have nothing to do with the piece on it.
    """
    inductances = [value * 1e9 for value in coupling.inductance_h]
    resistances = [value * 1e3 for value in coupling.resistance_ohm]
    inductance_spread = (max(inductances) - min(inductances)) / min(inductances)
    resistance_spread = (max(resistances) - min(resistances)) / min(resistances)
    assert inductance_spread <= _limit("MATRIX-ANTENNA-UNIFORMITY", "maximum")
    assert resistance_spread <= _limit("MATRIX-ANTENNA-UNIFORMITY", "maximum")


def test_a_row_and_a_column_are_decoupled(coupling: Coupling) -> None:
    """The claim the whole architecture rests on.

    Orthogonal loops should share almost no flux. They do not share none: the
    cancellation is weakest where two loops cross near their open ends, which
    is the four board corners.
    """
    worst = max(
        coupling.coupling_coefficient(row, column)
        for row in range(ROW_COUNT)
        for column in range(ROW_COUNT, LINE_COUNT)
    )
    assert worst <= _limit("MATRIX-ROW-COLUMN-COUPLING", "maximum"), (
        f"worst row-to-column coupling {worst:.4f}"
    )


def test_parallel_neighbours_are_the_dominant_coupling(coupling: Coupling) -> None:
    """Adjacent same-axis lines couple far more strongly than crossing ones.

    Recorded as a bound rather than a pass, because this is the number a tag
    reading on the wrong line would come from, and it is the one the test
    article has to confirm against a measurement.
    """
    adjacent = max(
        coupling.coupling_coefficient(line, line + 1)
        for line in range(ROW_COUNT - 1)
    )
    assert adjacent <= _limit("MATRIX-ADJACENT-LINE-COUPLING", "maximum"), (
        f"adjacent line coupling {adjacent:.4f}"
    )


def test_coupling_falls_away_with_distance(coupling: Coupling) -> None:
    """Neighbour coupling must be a local effect, not a board-wide one.

    If distant lines coupled comparably, one energised line would excite the
    whole board and the intersection would mean nothing.
    """
    adjacent = coupling.coupling_coefficient(0, 1)
    two_apart = coupling.coupling_coefficient(0, 2)
    far = coupling.coupling_coefficient(0, ROW_COUNT - 1)
    assert two_apart < adjacent / 4.0
    assert far < adjacent / 50.0


def test_the_matrix_is_reciprocal(coupling: Coupling) -> None:
    """M(i,j) must equal M(j,i) by physics, so the residual is solver error.

    Normalised against self inductance rather than against each mutual term.
    A relative check divides by near-zero couplings between distant lines and
    reports a huge error that means nothing; the first version of this test did
    exactly that and read 47 percent. Against the self-inductance scale the
    residual is 0.15 percent and does not move with mesh refinement, which is
    the solver's floor rather than a convergence failure.
    """
    scale = coupling.inductance_h[0]
    worst = max(
        abs(coupling.mutual_h[i][j] - coupling.mutual_h[j][i]) / scale
        for i in range(LINE_COUNT)
        for j in range(i + 1, LINE_COUNT)
    )
    assert worst <= 5e-3, f"reciprocity residual {worst:.2e} of self inductance"


def test_resistance_is_not_claimed_as_converged(coupling: Coupling) -> None:
    """Guards the honest gap rather than a value.

    Resistance rises monotonically with mesh density and was still rising at
    the finest mesh tried, because 17.8 um of skin depth in a 1 mm wide
    conductor needs far more filaments than the coupling does. The extraction
    therefore reports a lower bound. This test exists so that a later change
    which appears to "fix" resistance has to confront that, rather than a
    reader assuming the number is settled.
    """
    for line in range(LINE_COUNT):
        milliohm = coupling.resistance_ohm[line] * 1e3
        assert milliohm >= 400.0, f"line {line} at {milliohm:.1f} mohm is below any plausible bound"
