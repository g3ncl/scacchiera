"""Matrix board geometry constants, shared by the layout and the SPICE loop model.

Stdlib only, like `lightbar_geometry`: the layout generator runs under the
system interpreter, the simulation under the venv. The loop dimensions here are
the single source of truth for the copper the layout draws and the inductance
the simulation derives from it.
"""

BOARD_SIZE = 300.0
# The play area sits toward the top right so the left and bottom margins carry
# the switch cells, registers, and routing; the functional read budget wants
# nothing conductive but the antennas under the squares themselves.
PLAY_ORIGIN = 15.0
PLAY_SPAN = 280.0
SQUARE_PITCH = 35.0
ROW_COUNT = 8
LINE_COUNT = 16

# Each line antenna is a single-turn rectangular loop inset 2 mm inside its
# 35 mm lane. A single turn keeps rows entirely on the front copper and columns
# entirely on the back, so the two antenna sets cross without any jumper.
LOOP_INSET = 2.0
LOOP_LENGTH = PLAY_SPAN - 2.0 * LOOP_INSET
LOOP_BREADTH = SQUARE_PITCH - 2.0 * LOOP_INSET
LOOP_TRACE_WIDTH = 1.0
# Feed gap between the loop's two terminals, on the cell side of the loop.
TERMINAL_GAP = 3.0


def line_center(index: int) -> float:
    """Lane center for row or column `index` along its cross axis."""
    return PLAY_ORIGIN + SQUARE_PITCH / 2.0 + SQUARE_PITCH * index


# Mounting holes. M2.5 plated and bonded to ground, so the enclosure screws tie
# the shell to the pour instead of floating.
#
# They sit at MOUNTING_HOLE_OFFSET from the board edge, inside the 15 mm left and
# bottom margins only. Two reasons they are not on all four edges: the play area
# is offset 15 mm so the far margins are just 5 mm, too narrow for a 5.4 mm pad;
# and functional/physical.md wants nothing conductive near the sensing plane, so
# a grounded screw 0.8 mm from the outer antenna loop would load it. The far two
# edges want an enclosure ledge, or a wider outline, which is a CAD decision.
MOUNTING_HOLE_SIZE = "2.7mm_M2.5"
# 8.0 from the edge, not 4.0: the left margin reserves x 0.8 to 4.9 on front
# copper for the U1 serial verticals, and both margins carry hand-routed
# register lanes at 0.9 to 1.9. A plated hole is on every layer, so it clears
# those, and 8.0 still sits inside the 15 mm margin with the pour.
MOUNTING_HOLE_OFFSET = 8.0
MOUNTING_HOLE_PAD = 5.4
# Half-width of a switch cell's span along its margin. _cell_placements puts
# slot centers from center - 9.5 to center + 10.5, and the parts themselves reach
# about 2 mm further: a rotated 0603 is 3.4 mm tall, a SOT-23 3.5 mm. Add the
# hole pad's own radius so a band that survives this filter really does fit one.
_CELL_SPAN_LOW = 9.5 + 2.5
_CELL_SPAN_HIGH = 10.5 + 2.5


def mounting_hole_positions() -> tuple[tuple[float, float], ...]:
    """Hole centers: one past each end of the cell array.

    Only two, and this is a constraint rather than a choice. The left and bottom
    margins are 15 mm wide and already fully committed: hand-routed register
    lanes at 0.9 to 1.9, a reserved front-copper lane band out to 4.9 for the U1
    serial verticals, cell part rows at 4.4 and 10.6, and the vertical corridors
    the router needs to reach all 16 selection lines. A 5.4 mm pad dropped in
    the middle of that blocks a corridor: placing these at 8.0 mm mid-margin
    made Freerouting fail outright on SEL_CHAIN.

    So they go past the end of the cell array, where the margin carries only
    pour. The far two edges are just 5 mm wide (the play area is offset 15 mm)
    and their outer antenna loop runs 1.6 mm away, so a grounded screw there
    would load it. Supporting all four edges with screws needs a wider outline,
    which belongs with the enclosure design.
    """
    beyond_cells = line_center(ROW_COUNT - 1) + _CELL_SPAN_HIGH
    along = (beyond_cells + BOARD_SIZE) / 2.0
    return (
        (MOUNTING_HOLE_OFFSET, along),
        (along, MOUNTING_HOLE_OFFSET),
    )
