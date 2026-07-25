"""Light bar placement constants, shared by the layout script and the SPICE deck.

Stdlib only: the layout generator imports this under the system interpreter
(which has pcbnew) while the simulation imports it from the venv (which does
not), so nothing here may depend on either environment.

Why 14 pixels and not the 17 the functional spec originally asked for. The
SK6805MINI-E's legs stick out past its body, which is what makes it iron
solderable, and that puts its courtyard at 7.30 mm against the WS2812C-2020's
2.0 mm. The 4-pin JST GH is 9.46 mm wide and 6.40 mm deep, too deep to tuck
under the LED row in an 8.5 mm tall board, so it costs length exclusively:

    120.0 board
    - 0.77 left edge margin
    - 9.46 connector
    - 0.50 gap
    = 109.27 mm for the LEDs, and 109.27 / 7.30 = 14.9

So 14 fits with clean courtyards and 6.85 mm spare. 15 is reachable only by
dropping the pitch to 7.10 mm, which leaves the pads 0.30 mm apart but lets the
courtyards overlap. 16 does not fit at any pitch that keeps the pads apart.
"""

BOARD_WIDTH = 120.0
BOARD_HEIGHT = 8.5

# No mounting holes on this board, deliberately. Two reasons, and both would
# still hold if a pixel were removed to make room:
#
# 1. There is no room. J1 occupies x 0.77 to 10.23, the pixel array 10.95 to
#    113.15, the bulk capacitor 114.15 to 117.85. That leaves 2.15 mm, against
#    the 5.40 mm an M2 pad plus its clearance needs.
# 2. Even if it fitted, an M2 pad is 4.4 mm across on an 8.5 mm board, so a
#    screw would leave 2.05 mm of material either side of it. That is a tear-out
#    waiting to happen on a 1.0 mm substrate.
#
# The bar is a thin strip behind a diffuser, so it is retained by the diffuser
# channel or by adhesive, which is how LED strips of this shape are normally
# held. See docs/hardware/lightbar.md.
LED_COUNT = 14
# 7.30 mm is the SK6805MINI-E courtyard, so adjacent parts just touch and their
# 6.80 mm pad spans stay 0.50 mm apart.
LED_PITCH = 7.30
LED_START_X = 14.6
LED_Y = 2.3
# The 5 V bus runs below the connector's two mounting pads, which occupy y 4.25
# to 6.95 and block the otherwise-obvious band under the LED row. Every other
# full-length band is only ~0.7 mm tall between pad rows, too tight for a bus
# plus clearance, so 7.5 is the one place a 0.8 mm bus fits: it spans 7.1 to
# 7.9 and keeps 0.6 mm to the board edge.
CAPACITOR_Y = 5.6
POWER_BUS_Y = 7.5
CONNECTOR_X = 5.5
CONNECTOR_Y = 4.25
# The 1210 bulk capacitor goes in the spare copper to the right of the last
# pixel rather than in the crowded connector end.
BULK_X = 116.0
BULK_Y = 6.3  # sits beside the bus in the spare right-hand copper
# The back-copper ground pour is inset so its copper keeps the 0.5 mm
# board-edge clearance. The SPICE deck also reads this to size the plane.
POUR_INSET = 0.6
# The chain's return leg crosses on back copper above the ground vias.
DATA_RETURN_Y = 0.9
# DATA_IN ducks under the connector's signal pads to reach the first pixel.
DATA_IN_Y = 3.7


def led_x(index: int) -> float:
    return LED_START_X + LED_PITCH * index
