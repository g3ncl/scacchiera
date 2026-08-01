"""Extract the sixteen line antennas and their mutual coupling with FastHenry.

This answers the question the whole sensing architecture rests on. Rows run on
the front copper and columns on the back, crossing at right angles, and a
tag's square is the intersection of the one row and the one column that both
read it. That only works if a row and a column are effectively decoupled from
each other, and if adjacent parallel lines are decoupled enough that a tag
over one does not answer on its neighbour.

Nothing in the project has ever checked that. The prior art supports it and
`docs/hardware/matrix.md` asserts it, but the copper here has never been
solved. `hardware/sim/loop.py` gives a single loop's inductance from Grover's
formula, which says nothing about pairs.

The solver is FastHenry, already validated against that same Grover model in
`hardware/tests/test_rf_return.py` to 2 percent on inductance. At 13.56 MHz the
board is 0.014 of a wavelength across, so this is magnetoquasistatic and
FastHenry is the right tool.

**Inductance and coupling are converged; resistance is not.** A mesh study over
nhinc 1 to 7 and nwinc 9 to 13 moves self inductance by 0.04 percent and leaves
every coupling coefficient identical to four figures, so those are evidence.
Resistance climbs monotonically across that same sweep, 525 to 563 milliohms,
and was still rising at the finest mesh tried: at 13.56 MHz the skin depth in
copper is 17.8 um against a 1 mm wide, 35 um thick conductor, so resolving the
current crowding needs far more filaments than the coupling does. Resistance
from here is a lower bound, and loaded Q, being omega L over R, cannot be
stated at all. Capacitance needs a different solver. V8 measures both.

Geometry comes from `hardware/pcb/matrix_geometry.py`, the same constants the
footprint generator and the layout use, so this cannot drift from the board.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from hardware.pcb.matrix_geometry import (
    LINE_COUNT,
    LOOP_BREADTH,
    LOOP_LENGTH,
    LOOP_TRACE_WIDTH,
    PLAY_ORIGIN,
    PLAY_SPAN,
    ROW_COUNT,
    line_center,
)
from hardware.sim.copper import COPPER_THICKNESS_M


FASTHENRY = os.environ.get("FASTHENRY", str(Path.home() / ".local" / "bin" / "fasthenry"))
GENERATED_DIR = Path(__file__).parent / "generated" / "matrix" / "antennas"

CARRIER_HZ = 13.56e6
COPPER_THICKNESS_MM = COPPER_THICKNESS_M * 1e3
COPPER_SIGMA_PER_MM = 5.8e4

# Rows sit on the front copper and columns on the back, so the two sets are
# separated by the board less both claddings.
BOARD_THICKNESS_MM = 1.0
FRONT_Z_MM = BOARD_THICKNESS_MM - COPPER_THICKNESS_MM
BACK_Z_MM = 0.0

PLAY_CENTER = PLAY_ORIGIN + PLAY_SPAN / 2.0

# The feed gap at one end of each loop. The loop is otherwise closed.
TERMINAL_GAP = 3.0


@dataclass(frozen=True)
class Coupling:
    """The solved matrix at the carrier."""

    inductance_h: tuple[float, ...]
    resistance_ohm: tuple[float, ...]
    # mutual_h[i][j] is the mutual inductance between line i and line j.
    mutual_h: tuple[tuple[float, ...], ...]

    def coupling_coefficient(self, i: int, j: int) -> float:
        """k = M / sqrt(Li Lj), the fraction of one line's flux the other sees."""
        if i == j:
            return 1.0
        denominator = (self.inductance_h[i] * self.inductance_h[j]) ** 0.5
        return abs(self.mutual_h[i][j]) / denominator if denominator else 0.0


def loop_path(line: int) -> tuple[tuple[float, float, float], ...]:
    """The rectangular conductor of one line, as it sits on the board.

    Lines 0 to 7 are rows on the front copper, running along x at their lane's
    y centre. Lines 8 to 15 are columns on the back, the same shape rotated a
    quarter turn. The path starts and ends either side of the feed gap.
    """
    half_length = LOOP_LENGTH / 2.0
    half_breadth = LOOP_BREADTH / 2.0
    half_gap = TERMINAL_GAP / 2.0

    # In the footprint's own frame: open at the left, around the lane, back.
    flat = (
        (-half_length, -half_gap),
        (-half_length, -half_breadth),
        (half_length, -half_breadth),
        (half_length, half_breadth),
        (-half_length, half_breadth),
        (-half_length, half_gap),
    )

    if line < ROW_COUNT:
        z = FRONT_Z_MM
        cx, cy = PLAY_CENTER, line_center(line)
        return tuple((cx + x, cy + y, z) for x, y in flat)

    z = BACK_Z_MM
    cx, cy = line_center(line - ROW_COUNT), PLAY_CENTER
    # Rotated a quarter turn: the footprint's x runs along the board's y.
    return tuple((cx - y, cy + x, z) for x, y in flat)


def deck() -> str:
    """A FastHenry input holding all sixteen loops at once.

    All of them together, not one at a time, because the mutual terms are the
    point. FastHenry returns the full port-to-port impedance matrix in one
    solve.
    """
    # nwinc 9 with a single filament through the thickness. The mesh study in
    # the module docstring shows inductance and coupling converged there, and
    # refining further only moves resistance, which this extraction does not
    # claim. Meshing for the quantity actually being extracted keeps the solve
    # at a couple of seconds instead of four minutes.
    lines = [
        "* Sixteen matrix line antennas: eight rows on front copper, eight",
        "* columns on back, from hardware/pcb/matrix_geometry.py.",
        ".units mm",
        f".default sigma={COPPER_SIGMA_PER_MM} nhinc=1 nwinc=9 h={COPPER_THICKNESS_MM}",
        "",
    ]
    for line in range(LINE_COUNT):
        path = loop_path(line)
        lines.append(f"* line {line} ({'row' if line < ROW_COUNT else 'column'})")
        for index, (x, y, z) in enumerate(path):
            lines.append(f"N{line}_{index} x={x:.4f} y={y:.4f} z={z:.4f}")
        for index in range(len(path) - 1):
            lines.append(
                f"E{line}_{index} N{line}_{index} N{line}_{index + 1}"
                f" w={LOOP_TRACE_WIDTH} h={COPPER_THICKNESS_MM}"
            )
        # The feed gap: the port sits across the two open ends.
        lines.append(f".external N{line}_0 N{line}_{len(path) - 1}")
        lines.append("")

    lines += [
        f".freq fmin={CARRIER_HZ} fmax={CARRIER_HZ} ndec=1",
        ".end",
        "",
    ]
    return "\n".join(lines)


_COMPLEX = re.compile(r"([-\d.eE+]+)\s+([-\d.eE+]+)j")


def solve(text: str, name: str = "antennas") -> Coupling:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    deck_path = GENERATED_DIR / f"{name}.inp"
    deck_path.write_text(text, encoding="utf-8")
    if not Path(FASTHENRY).is_file():
        raise FileNotFoundError(
            f"fasthenry not found at {FASTHENRY}; set FASTHENRY to its path"
        )
    subprocess.run(
        (FASTHENRY, deck_path.name),
        cwd=GENERATED_DIR,
        check=True,
        capture_output=True,
    )

    matrix_text = (GENERATED_DIR / "Zc.mat").read_text(encoding="utf-8")
    rows: list[list[complex]] = []
    for raw in matrix_text.splitlines():
        found = _COMPLEX.findall(raw)
        if len(found) == LINE_COUNT:
            rows.append([complex(float(re_), float(im)) for re_, im in found])
    if len(rows) != LINE_COUNT:
        raise ValueError(
            f"expected a {LINE_COUNT} by {LINE_COUNT} impedance matrix, read {len(rows)} rows"
        )

    omega = 2.0 * 3.141592653589793 * CARRIER_HZ
    inductance = tuple(rows[i][i].imag / omega for i in range(LINE_COUNT))
    resistance = tuple(rows[i][i].real for i in range(LINE_COUNT))
    mutual = tuple(
        tuple(rows[i][j].imag / omega for j in range(LINE_COUNT))
        for i in range(LINE_COUNT)
    )
    return Coupling(inductance_h=inductance, resistance_ohm=resistance, mutual_h=mutual)


def extract() -> Coupling:
    return solve(deck())
