"""Coincident worst-case load the hub presents to its power module.

The power-module interface obliges a module to supply 1.3 A. That number was an
estimate when it was written. This is the derivation, from filed data sheets,
with every part assumed to be doing its worst at the same moment: the radio
transmitting, the reader driving its field, both light bars white, and the
matrix biased.

One input is not sourced. The two display modules are fixed by the functional
specification but have no filed data sheet and no V1 record, so their current is
an allowance rather than a value, marked below and generous on purpose.
"""

from dataclasses import dataclass


# ESP32-C6-MINI-1U-N4 data sheet, Table 6-4: 382 mA transmitting 802.11b at
# 1 Mbps DSSS and 20.5 dBm, the largest figure in the table.
MCU_PEAK_A = 0.382

# PN5180 data sheet, Table 128 Current consumption. TVDD is the transmit driver
# at its 250 mA maximum, PVDD the host interface, VBAT the core.
READER_TVDD_A = 0.250
READER_PVDD_A = 0.020
READER_VBAT_A = 0.020

# docs/hardware/criteria.yaml, MATRIX-BIAS-CURRENT: 14 mA at its upper limit,
# plus an allowance for the two 74HC595 registers, whose data sheet quiescent
# current is 160 uA and whose switching current flows only while shifting.
MATRIX_BIAS_A = 0.014
MATRIX_LOGIC_A = 0.005

# ASSUMED. The ER-OLEDM3.12-1W modules are purchased accessories with no filed
# data sheet, so this is an allowance, not a datum: 100 mA each is generous for
# a 256 by 64 monochrome panel and is used only to make the total pessimistic.
# Filing their data sheet is an open V1 action and would replace this.
DISPLAY_ALLOWANCE_EACH_A = 0.100
DISPLAY_COUNT = 2

# docs/hardware/lightbar.md: 14 pixels at 16 mA per bar, both bars white. This
# sits on the module's 5 V directly, not behind the buck.
LIGHTBAR_A = 0.448

RAIL_3V3_V = 3.3
MODULE_V = 5.0

# Conservative bound rather than a curve reading. The AP63203 data sheet plots
# efficiency above 90 percent across this range; 85 percent is used because a
# lower number raises the input current, which is the pessimistic direction.
BUCK_EFFICIENCY = 0.85


@dataclass(frozen=True)
class LoadBudget:
    """Everything drawing at once, referred to the module's output."""

    @property
    def rail_3v3_a(self) -> float:
        return (
            MCU_PEAK_A
            + READER_TVDD_A
            + READER_PVDD_A
            + READER_VBAT_A
            + MATRIX_BIAS_A
            + MATRIX_LOGIC_A
            + DISPLAY_ALLOWANCE_EACH_A * DISPLAY_COUNT
        )

    @property
    def rail_3v3_reflected_a(self) -> float:
        """The 3.3 V load as current drawn from the module, through the buck."""
        return self.rail_3v3_a * RAIL_3V3_V / (MODULE_V * BUCK_EFFICIENCY)

    @property
    def module_total_a(self) -> float:
        return self.rail_3v3_reflected_a + LIGHTBAR_A

    @property
    def assumed_fraction(self) -> float:
        """How much of the 3.3 V rail rests on the unsourced display allowance."""
        return DISPLAY_ALLOWANCE_EACH_A * DISPLAY_COUNT / self.rail_3v3_a
