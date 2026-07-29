"""Waveform integrity of the buses that leave the hub on a cable.

The addressable pixel reads a self-clocked line, so it does not care how long
the edges take in the abstract. It cares that the high time it sees matches the
high time the hub sent, within the 50 ns the pixel's own timing table allows
around a 300 ns zero symbol.

A uniform delay does not threaten that: it shifts both edges equally. What does
is the buffer's asymmetry, since it sources through roughly three times the
impedance it sinks through, so a rising edge reaches the pixel's threshold later
than a falling edge leaves it. That difference is pulse-width distortion and it
is what this bounds.
"""

from dataclasses import dataclass
from math import log


# SN74AHCT1G125DBVR data sheet, Recommended Operating Conditions and Electrical
# Characteristics at VCC = 4.5 V: 8 mA of drive with VOH 3.8 V minimum and VOL
# 0.44 V maximum. Output impedance is taken as the worst-case chord to each.
BUFFER_V = 5.0
BUFFER_SOURCE_OHM = (5.0 - 3.8) / 8e-3
BUFFER_SINK_OHM = 0.44 / 8e-3

# T37K3RGB-05C000112U1930 data sheet: 30 pF maximum input capacitance, and a
# threshold band whose worst case for a rising edge is VIH 3.1 V and for a
# falling edge VIL 1.5 V.
PIXEL_INPUT_PF = 30.0
PIXEL_VIH_V = 3.1
PIXEL_VIL_V = 1.5

# Same data sheet: the zero symbol is 300 ns with 50 ns either side. That
# tolerance is the whole budget for distortion between hub and pixel.
SYMBOL_TOLERANCE_NS = 50.0

# The harness is not dimensioned anywhere in docs/, so its capacitance is a
# bound rather than a value. 150 pF is around a metre and a half of 1.25 mm
# ribbon, far longer than a cable inside one enclosure, and more capacitance
# only slows the edges, so the bound is the pessimistic direction.
CABLE_BOUND_PF = 150.0

# The hub's driver trace and the bar's entry trace, both short.
TRACE_PF = 10.0


@dataclass(frozen=True)
class LedSignalBudget:
    cable_pf: float = CABLE_BOUND_PF

    @property
    def load_f(self) -> float:
        return (PIXEL_INPUT_PF + TRACE_PF + self.cable_pf) * 1e-12

    @property
    def rise_to_threshold_s(self) -> float:
        """Time from the buffer's edge to the pixel seeing a high."""
        return BUFFER_SOURCE_OHM * self.load_f * log(
            BUFFER_V / (BUFFER_V - PIXEL_VIH_V)
        )

    @property
    def fall_to_threshold_s(self) -> float:
        """Time from the buffer's edge to the pixel seeing a low."""
        return BUFFER_SINK_OHM * self.load_f * log(BUFFER_V / PIXEL_VIL_V)

    @property
    def pulse_width_distortion_s(self) -> float:
        """How much longer or shorter the pixel's high time is than the hub's."""
        return abs(self.rise_to_threshold_s - self.fall_to_threshold_s)


# I2C pull-ups, hub side. Both are 4.7 kohm to 3.3 V (R21, R22).
I2C_PULLUP_OHM = 4700.0

# NXP I2C specification, as quoted in the TCA9535PWR data sheet's timing table:
# 1000 ns of rise time in standard mode, 300 ns in fast mode.
I2C_RISE_LIMIT_STANDARD_NS = 1000.0
I2C_RISE_LIMIT_FAST_NS = 300.0

# The bus runs to the expander on-board and out to the power module on a cable
# whose length nothing specifies, so this is a bound in the same spirit as the
# light bar's: 200 pF is the I2C specification's own ceiling for a bus.
I2C_BUS_BOUND_PF = 200.0

# The 30 to 70 percent rise of an RC through a pull-up, which is how the I2C
# specification defines its rise time.
_I2C_RISE_COEFFICIENT = 0.8473


@dataclass(frozen=True)
class I2cBusBudget:
    bus_pf: float = I2C_BUS_BOUND_PF

    @property
    def rise_time_s(self) -> float:
        return _I2C_RISE_COEFFICIENT * I2C_PULLUP_OHM * self.bus_pf * 1e-12

    @property
    def fits_standard_mode(self) -> bool:
        return self.rise_time_s * 1e9 <= I2C_RISE_LIMIT_STANDARD_NS

    @property
    def fits_fast_mode(self) -> bool:
        return self.rise_time_s * 1e9 <= I2C_RISE_LIMIT_FAST_NS


# ESP32-C6-MINI-1U-N4 data sheet: 40 mA IOH and 28 mA IOL at the default drive.
# Output impedance is the worst-case chord from the 3.3 V rail, which is the
# sink side because it drives less current.
MCU_V = 3.3
MCU_OUTPUT_OHM = MCU_V / 28e-3

# 74HC595D-118 data sheet: 3.5 pF per input. Two registers in the chain see the
# clock, one sees the serial data, and the matrix link carries both.
REGISTER_INPUT_PF = 3.5
REGISTER_COUNT = 2

# The serial link runs at a few megahertz through the GPIO matrix, which is the
# rate the reader and displays need.
SERIAL_CLOCK_HZ = 4e6

# 74HC595D-118 data sheet: maximum input transition rise and fall rate, 139 ns/V
# at VCC 4.5 V. The registers run at 3.3 V, where the table allows a slower edge
# still (625 ns/V at 2.0 V), so the 4.5 V row is the conservative choice.
REGISTER_TRANSITION_LIMIT_NS_PER_V = 139.0

# Cable to the matrix board, bounded the same way as the light bar's.
SERIAL_CABLE_BOUND_PF = 150.0


@dataclass(frozen=True)
class SerialLinkBudget:
    """Clock and data edges on the link to the matrix shift registers."""

    cable_pf: float = SERIAL_CABLE_BOUND_PF

    @property
    def load_f(self) -> float:
        return (
            REGISTER_INPUT_PF * REGISTER_COUNT + TRACE_PF + self.cable_pf
        ) * 1e-12

    @property
    def rise_time_s(self) -> float:
        """Ten to ninety percent, the usual way a logic edge is quoted."""
        return 2.2 * MCU_OUTPUT_OHM * self.load_f

    @property
    def half_period_s(self) -> float:
        return 1.0 / (2.0 * SERIAL_CLOCK_HZ)

    @property
    def edge_fraction_of_half_period(self) -> float:
        return self.rise_time_s / self.half_period_s

    @property
    def transition_rate_ns_per_v(self) -> float:
        """The edge expressed the way the receiving register specifies it.

        A ten to ninety percent rise covers eight tenths of the supply, which is
        the swing the quoted rate applies to.
        """
        return self.rise_time_s * 1e9 / (0.8 * MCU_V)
