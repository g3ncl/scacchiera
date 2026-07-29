"""What the 3.3 V rail does when its input sags, starts, or disappears.

The transient cases V3 asks for split three ways on this board. Handover and
source insertion belong to the power module and are measured at V8. Transient
response and stability belong to a compensation network the buck's manufacturer
does not publish, so no honest model can produce them. What is left is bounded
by conduction and charge, and reduces to arithmetic on filed data sheet values,
which the workflow recognises as Derived evidence.

Deriving it is not busywork: the dropout figure is what tells the power-module
interface how far a module's output may sag, and that number was missing from
the contract.
"""

from dataclasses import dataclass


# AP63203WU-7 data sheet, Electrical Characteristics.
HIGH_SIDE_RDSON_OHM = 0.125
SOFT_START_S = 4e-3
REGULATED_V = 3.30

# NR6045S4R7MT data sheet, the higher of its two published DC resistances.
INDUCTOR_DCR_OHM = 0.034

# ESP32-C6-MINI-1U-N4 data sheet, Recommended Operating Conditions.
MCU_SUPPLY_MIN_V = 3.0

# Two 22 uF output capacitors, at the same conservative half-of-nominal bound
# the ripple bench uses, since the part's data sheet prints only example bias
# curves. Less capacitance means both less inrush and less hold-up, so the bound
# is pessimistic for hold-up and optimistic for inrush; inrush is reported
# against the nominal value for that reason.
OUTPUT_CAPACITANCE_F = 44e-6
OUTPUT_CAPACITANCE_BOUND_F = 22e-6

# The load the power-module interface obliges a module to supply.
INTERFACE_LOAD_A = 1.3


@dataclass(frozen=True)
class RailBudget:
    load_a: float = INTERFACE_LOAD_A

    @property
    def dropout_input_v(self) -> float:
        """Lowest module output that still holds 3.3 V.

        In dropout the converter stops switching and holds the high-side switch
        on, so the input has to cover the output plus the drops across that
        switch and the inductor's resistance.
        """
        return REGULATED_V + self.load_a * (HIGH_SIDE_RDSON_OHM + INDUCTOR_DCR_OHM)

    @property
    def startup_inrush_a(self) -> float:
        """Current the output capacitors draw while the soft start ramps them."""
        return OUTPUT_CAPACITANCE_F * REGULATED_V / SOFT_START_S

    @property
    def hold_up_s(self) -> float:
        """How long the rail stays above the MCU's minimum with the input gone.

        The output capacitors are all that is left, so this is the time they
        take to fall from regulation to the MCU's floor at the stated load.
        """
        return (
            OUTPUT_CAPACITANCE_BOUND_F
            * (REGULATED_V - MCU_SUPPLY_MIN_V)
            / self.load_a
        )
