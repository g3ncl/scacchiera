"""Geometry for the split sensing plane: one PCB per line antenna, plus a spine.

The monolithic matrix board puts all sixteen loops on one 300 by 300 mm
substrate, rows on the front copper and columns on the back. This splits the
same sixteen loops onto sixteen identical strips, stacked crosswise in two
planes and cabled to two spine boards.

The loop copper itself does not change. A strip's long axis carries the loop at
exactly the position `matrix_geometry` puts it at, and the lane pitch and
play-area registration are imported from there rather than restated, so the
copper this design fabricates is the copper already extracted and simulated.
What is new here is the strip outline around it, the two-plane stackup that
replaces one substrate's two faces, and the spine.

Stdlib only, like `matrix_geometry`: the layout generators run under the system
interpreter and the field solver under the venv.
"""

from hardware.pcb.matrix_geometry import (
    BOARD_SIZE,
    PLAY_ORIGIN,
    PLAY_SPAN,
    ROW_COUNT,
    SQUARE_PITCH,
    line_center,
)


# The strip keeps the monolith's length so the loop sits at the same place along
# the play axis and the extracted copper is the copper already validated.
STRIP_LENGTH = BOARD_SIZE
# 33.0 inside a 35 mm lane: the 31 mm loop plus 0.5 mm of copper-to-edge either
# side (the board rule is 0.2), leaving a 2.0 mm air gap between neighbouring
# strips for the printed frame's rib. Widening the strip would not widen the
# loop, it would only close that rib up.
STRIP_WIDTH = 33.0
LOOP_CENTER_ACROSS = STRIP_WIDTH / 2.0
PLAY_CENTER = PLAY_ORIGIN + PLAY_SPAN / 2.0

# 0.6 mm rather than the monolith's 1.0: two substrates now sit where one used
# to, so the thinner stock is what keeps the far plane inside the read budget.
# 0.6 is a no-premium JLCPCB two-layer thickness; 0.4 is not.
STRIP_THICKNESS = 0.6
# Air gap the printed frame holds between the two planes. Rows are the lower
# plane and columns the upper, both loops on their strip's top copper, so the
# columns face the pieces exactly as the monolith's front-copper rows did and
# row-to-column separation is one substrate plus this gap.
#
# This is the one knob the monolith did not have, since on a single substrate the
# plane separation is the board thickness. 0.4 spends it on reproducing the
# monolith's 1.0 mm rather than on exploiting it, which is what keeps every
# coupling figure in criteria.yaml applicable to the split board.
INTERPLANE_GAP = 0.4
PLANE_SEPARATION = STRIP_THICKNESS + INTERPLANE_GAP


# Two columns of six, ordered along the signal chain so every net joins parts
# that are physically adjacent. The tank column sits nearest the loop terminals
# and the bias column behind it, which is the monolith's own RF-in-front,
# bias-behind arrangement turned ninety degrees into a narrower, taller zone.
_COLUMN_X = (3.0, 9.0)
_ROW_Y = (12.0, 15.4, 18.8, 22.2, 25.6, 29.0)
# Bias chain, in the order current flows: DC block, choke, bleed, isolation
# diode, set resistor, steering FET.
BIAS_COLUMN = ("C1", "L1", "R3", "D2", "R2", "Q2")
# Tank chain: damping into the loop, then the series switch, the shunt, and the
# three tuning positions. Six consecutive parts share the match node, so placing
# them in one column makes that six-way net a single straight run.
TANK_COLUMN = ("R1", "D1", "Q1", "C2", "C3", "C4")


def strip_component_slots() -> dict[str, tuple[float, float]]:
    """Where each switch-cell part sits in the component zone."""
    slots: dict[str, tuple[float, float]] = {}
    for column, references in zip(_COLUMN_X, (BIAS_COLUMN, TANK_COLUMN)):
        for reference, row in zip(references, _ROW_Y):
            slots[reference] = (column, row)
    return slots


# The spine link. Its cable exits off the end of the strip, under the plane, so
# nothing stands above the top face and the controlled air gap stays flat.
# 6.5 rather than the zone's midpoint: the GH housing's two mounting pads reach
# 5.6 mm either side of centre, and at 6.25 the left one sat 0.15 mm from the
# board edge against a 0.2 mm rule.
STRIP_CONNECTOR = (6.5, 6.0)
# The pour, and the router, stop here. Beyond it the strip carries antenna
# copper only, on the front face, exactly as the monolith's play area does.
STRIP_POUR_EDGE = 14.5


# --- Spine -----------------------------------------------------------------

# One spine design, built twice: one under the row plane's connector ends, one
# under the column plane's. Each carries eight strip sockets on the 35 mm lane
# pitch, one 74HC595 for its eight lines, and a pass-through link so the pair
# chains exactly as the monolith's U1 and U2 did.
SPINE_SOCKETS = ROW_COUNT
# Sockets sit at their lane's centre less this, so socket i lands under strip i.
SPINE_ORIGIN = PLAY_ORIGIN - 5.0
SPINE_LENGTH = 2.0 * (line_center(0) - SPINE_ORIGIN) + SQUARE_PITCH * (SPINE_SOCKETS - 1)
# Four bands across the width: sockets facing the strips, the wide RF bus
# behind them, a clear channel, then the register. 28 rather than 24 because at
# 24 the channel was 2.3 mm and the router could not fit the eighth selection
# run through it. Spine area is a rounding error against sixteen strips, so
# buying the channel is the cheap fix.
SPINE_WIDTH = 28.0
SPINE_SOCKET_Y = 5.0
SPINE_RF_Y = 9.5
SPINE_PART_Y = 21.0


def spine_socket_x(index: int) -> float:
    """Socket centre for strip `index` of this spine's eight."""
    return line_center(index) - SPINE_ORIGIN


# Socket designators start at J3: J1 is the link in and J2 the link out. The
# schematic and the layout both need this, and the layout runs under the system
# interpreter with no SKiDL, so it lives here rather than in `spine`.
SOCKET_REF_BASE = 3


def socket_reference(index: int) -> str:
    return f"J{SOCKET_REF_BASE + index}"


# The register sits between sockets 3 and 4 so its eight selection runs fan out
# symmetrically and none of them has to cross the whole board.
SPINE_REGISTER_X = (spine_socket_x(3) + spine_socket_x(4)) / 2.0
SPINE_DECOUPLE_X = SPINE_REGISTER_X + 8.5
# The links go at the two ends, in the socket row, so the pair chains left to
# right and every cable leaves the same edge.
SPINE_LINK_IN_X = 7.0
SPINE_LINK_OUT_X = SPINE_LENGTH - 7.0
SPINE_MOUNTING_HOLES = (
    (SPINE_LINK_IN_X, SPINE_PART_Y),
    (SPINE_LINK_OUT_X, SPINE_PART_Y),
)
SPINE_POUR_INSET = 0.3

# The RF bus runs the spine as a wide microstrip over a solid back-copper
# ground, which is what keeps its inductance a small fraction of a loop's. The
# router picks every other width; this one is drawn by the layout because the
# simulation reads its inductance back off the geometry.
SPINE_RF_WIDTH = 3.0
# The bus taps a connector's pin 2, and pin 4 of seven on a 1.25 mm pitch is the
# housing's centre, so the tap sits 2.5 mm from the placement position. It
# matters because J2 is rotated, which puts its tap on the far side of its
# centre and makes the drawn bus 5 mm longer than a centre-to-centre reading
# would say. `hardware/sim/strip_rf.py` models the drawn length, and
# `test_sim_strip.py` checks the two against the routed board.
SPINE_RF_PIN_OFFSET = 2.5


def spine_bus_tap_x(index: int) -> float:
    """Where socket `index` taps the bus, in the spine's own frame."""
    return spine_socket_x(index) - SPINE_RF_PIN_OFFSET


def spine_bus_span_mm() -> float:
    """Drawn length of the bus, link tap to link tap.

    Not `SPINE_LENGTH` less two margins: the two links face opposite ways, so
    their taps sit on opposite sides of their placement positions.
    """
    return (SPINE_LINK_OUT_X + SPINE_RF_PIN_OFFSET) - (
        SPINE_LINK_IN_X - SPINE_RF_PIN_OFFSET
    )


# --- Interconnect ----------------------------------------------------------

# Every strip is cabled to its spine with the same length of harness. Equal
# lengths matter more than short ones: harness inductance lands in series with
# the loop, so a common length detunes all sixteen lines together (which the
# tuning capacitor absorbs) where mixed lengths would spread them apart (which
# it cannot).
HARNESS_LENGTH_MM = 60.0
# Hub to the first spine, and first spine to second. Longer than a strip
# harness because it crosses the body rather than reaching the strip above it.
SPINE_LINK_LENGTH_MM = 100.0
