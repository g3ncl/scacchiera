"""Light bar placement constants, shared by the layout script and the SPICE deck.

Stdlib only: the layout generator imports this under the system interpreter
(which has pcbnew) while the simulation imports it from the venv (which does
not), so nothing here may depend on either environment.
"""

BOARD_WIDTH = 120.0
BOARD_HEIGHT = 8.5
LED_COUNT = 17
# 17 LEDs on a 6.2 mm pitch span 99.2 mm; starting at 15.8 mm leaves room for
# the connector and bulk capacitor at the left edge while the diffuser hides
# the asymmetry.
LED_START_X = 15.8
LED_PITCH = 6.2
LED_Y = 2.2
CAPACITOR_Y = 5.4
POWER_BUS_Y = 7.6
CONNECTOR_X = 4.8
CONNECTOR_Y = 4.25


def led_x(index: int) -> float:
    return LED_START_X + LED_PITCH * index
