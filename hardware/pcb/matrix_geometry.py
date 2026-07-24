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
