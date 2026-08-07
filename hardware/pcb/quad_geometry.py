"""Geometry for the split sensing plane: four line antennas per board.

The monolithic matrix board puts all sixteen loops on one 300 by 300 mm
substrate, rows on the front copper and columns on the back. This splits the
same sixteen loops onto four identical 300 by 140 mm boards, stacked crosswise
in two planes, each carrying four lanes and its own selection register.

Four is the block size the fabricator's pricing and minimum order picked. A
narrow outline escapes the size charges a 300 by 300 mm one pays (measured, not
assumed: 140 mm wide prices at the same EUR per square millimetre as a 33 mm
outline did), and four boards is exactly one set where the five-piece minimum
leaves a single spare. One board per line would be more flexible per experiment and cost
thirty-six connectors to get there; four is where the curve turns.

The loop copper itself does not change. A board's long axis carries its loops at
exactly the positions `matrix_geometry` puts them at, and the lane pitch and
play-area registration are imported from there rather than restated, so the
copper this design fabricates is the copper already extracted and simulated.

Stdlib only, like `matrix_geometry`: the layout generator runs under the system
interpreter and the field solver under the venv.
"""

from hardware.pcb.matrix_geometry import (
    BOARD_SIZE,
    LINE_COUNT,
    PLAY_ORIGIN,
    PLAY_SPAN,
    SQUARE_PITCH,
)


# Four lanes per board, four boards, sixteen lines. Two boards tile each plane.
LANES_PER_BOARD = 4
BOARD_COUNT = LINE_COUNT // LANES_PER_BOARD

# The board keeps the monolith's length so the loops sit at the same place along
# the play axis and the extracted copper is the copper already validated.
QUAD_LENGTH = BOARD_SIZE
# Exactly four lanes, so two boards butt together and span the 280 mm play area
# with no cumulative error between them.
QUAD_WIDTH = SQUARE_PITCH * LANES_PER_BOARD
PLAY_CENTER = PLAY_ORIGIN + PLAY_SPAN / 2.0

# 0.6 mm rather than the monolith's 1.0: two substrates now sit where one used
# to, so the thinner stock is what keeps the far plane inside the read budget.
# Quoted and accepted at 300 mm long, which was the open risk.
QUAD_THICKNESS = 0.6
# Air gap the printed frame holds between the two planes. Rows are the lower
# plane and columns the upper, both loops on their board's top copper, so the
# columns face the pieces exactly as the monolith's front-copper rows did and
# row-to-column separation is one substrate plus this gap.
#
# This is the one knob the monolith did not have, since on a single substrate the
# plane separation is the board thickness. 0.4 spends it on reproducing the
# monolith's 1.0 mm rather than on exploiting it, which is what keeps every
# coupling figure in criteria.yaml applicable to the split board.
INTERPLANE_GAP = 0.4
PLANE_SEPARATION = QUAD_THICKNESS + INTERPLANE_GAP


def lane_center(lane: int) -> float:
    """Lane centre across the board, for lane 0 to 3 of this board's four."""
    return SQUARE_PITCH / 2.0 + SQUARE_PITCH * lane


# Everything that is not loop lives in the first 14.5 mm, which is the monolith's
# own component margin. The pour, and the router, stop here; beyond it the board
# carries antenna copper only, on the front face.
POUR_EDGE = 14.5

# Each lane's twelve cell parts, two columns of six centred on the lane. The
# 3.6 mm row pitch is not arbitrary: it holds the cluster inside 21.5 mm so the
# 13.5 mm gap left between neighbouring lanes can take a rotated connector, which
# is 11.2 mm across its mounting pads. At 4.0 mm the gaps closed to 11.5 and the
# connector no longer cleared its neighbours.
_CELL_COLUMN_X = (3.5, 9.5)
_CELL_ROW_PITCH = 3.6
_CELL_ROWS = 6
# Designators follow `matrix.matrix_cell`'s own striding, which is what lets the
# four lanes be four calls to it rather than a fourth copy of the cell.
def _bias_column(lane: int) -> tuple[str, ...]:
    """DC block, choke, bleed, isolation diode, set resistor, steering FET."""
    return (
        f"C{lane * 4 + 1}", f"L{lane * 2 + 1}", f"R{lane * 3 + 3}",
        f"D{lane * 2 + 2}", f"R{lane * 3 + 2}", f"Q{lane * 2 + 2}",
    )


def _tank_column(lane: int) -> tuple[str, ...]:
    """Damping into the loop, series switch, shunt, then the three tuning pads.

    Six consecutive parts share the match node, so placing them in one column
    makes that six-way net a single straight run.
    """
    return (
        f"R{lane * 3 + 1}", f"D{lane * 2 + 1}", f"Q{lane * 2 + 1}",
        f"C{lane * 4 + 2}", f"C{lane * 4 + 3}", f"C{lane * 4 + 4}",
    )


def antenna_reference(lane: int) -> str:
    return f"L{lane * 2 + 2}"


def cell_slots(lane: int) -> dict[str, tuple[float, float]]:
    """Where each of one lane's switch-cell parts sits, by reference."""
    first = lane_center(lane) - _CELL_ROW_PITCH * (_CELL_ROWS - 1) / 2.0
    slots: dict[str, tuple[float, float]] = {}
    for column, references in zip(_CELL_COLUMN_X, (_bias_column(lane), _tank_column(lane))):
        for row, reference in enumerate(references):
            slots[reference] = (column, first + _CELL_ROW_PITCH * row)
    return slots


# The gaps between lane clusters, which is the only place a part wider than a
# cell part fits. Three of them, and there are exactly three things to put there.
def _lane_gap_y(gap: int) -> float:
    return SQUARE_PITCH * (gap + 1)


# Link in and link out, one at each end of the board's share of the chain. Both
# are rotated so the pin row runs across the board and the cable leaves off the
# x = 0 end, under the side rail, rather than off a long edge where the
# neighbouring board of the same plane sits.
# 3.5 rather than 3.0: at 3.0 the housing's courtyard reached x = -0.24, hanging
# off the board edge.
LINK_IN = (3.5, _lane_gap_y(0))
LINK_OUT = (3.5, _lane_gap_y(2))
# The register sits in the middle gap, so its four selection runs reach two lanes
# either side rather than three on one. It is deliberately *not* rotated with the
# links: a SOIC-16 turned across the board is 10.5 mm wide and swallows the whole
# 14.5 mm zone, where upright it is 7.5 mm wide and 10.5 mm tall, which the
# 13.5 mm lane gap takes and which leaves room beside it for the decoupling.
REGISTER = (7.0, _lane_gap_y(1))
DECOUPLE = (12.8, _lane_gap_y(1))

POUR_INSET = 0.3


# --- Interconnect ----------------------------------------------------------

# Every board is cabled to the next with the same length of harness. Equal
# lengths matter more than short ones: harness inductance lands in series with
# the loop, so a common length detunes the lines it feeds together (which the
# tuning capacitor absorbs) where mixed lengths would spread them apart (which
# it cannot).
HARNESS_LENGTH_MM = 100.0
