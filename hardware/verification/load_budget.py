"""Coincident worst-case load the hub presents to its power module.

The power-module interface obliges a module to supply 1.6 A. This is the
derivation, from filed manufacturer evidence,
with every part assumed to be doing its worst at the same moment: the radio
transmitting, the reader driving its field, both light bars white, and the
matrix biased.

The display supplier publishes contradictory active-current claims. The formal
electrical table's larger value is used until the supplier resolves the conflict.
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

# ER-OLEDM3.12-1 section 4.3: 320 mA maximum at 3.3 V with 100 percent
# display area on. The product page instead calls 2 mA the active maximum,
# contradicting the same data sheet's 2 mA sleep row. The larger value is the
# only safe basis while that V1 conflict is open.
DISPLAY_MAX_EACH_A = 0.320
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
            + DISPLAY_MAX_EACH_A * DISPLAY_COUNT
        )

    @property
    def rail_3v3_reflected_a(self) -> float:
        """The 3.3 V load as current drawn from the module, through the buck."""
        return self.rail_3v3_a * RAIL_3V3_V / (MODULE_V * BUCK_EFFICIENCY)

    @property
    def module_total_a(self) -> float:
        return self.rail_3v3_reflected_a + LIGHTBAR_A

    @property
    def display_fraction(self) -> float:
        """How much of the 3.3 V rail belongs to the two displays."""
        return DISPLAY_MAX_EACH_A * DISPLAY_COUNT / self.rail_3v3_a
