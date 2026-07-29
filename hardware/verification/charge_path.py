"""Steady-state numbers for the gated USB charge path.

These are Derived in the workflow's sense: deterministic arithmetic whose every
input is a filed data sheet value. The switch is a resistor with a current
limit, so a SPICE bench of its steady state would restate Ohm's law with more
ceremony and no more confidence. What genuinely needs simulation on this path is
the transient behaviour, and that is blocked on binding a module: inrush depends
on the module's input capacitance, which no unbound part has.
"""

from dataclasses import dataclass


# AP22811AW5-7 data sheet, Electrical Characteristics at VIN = 5 V.
SWITCH_RDSON_MAX_OHM = 0.065
SWITCH_LIMIT_MIN_A = 2.2
SWITCH_LIMIT_MAX_A = 3.2

# docs/functional/power.md: a compliant 5 V, 2 A USB source. That is everything
# the inlet can legitimately deliver, so it is what the switch has to pass
# without its protection firing.
SOURCE_MAX_A = 2.0

# J2 carries the qualified output on three of its seven contacts, each rated
# 1.0 A by the JST GH data sheet. Ground returns on the remaining four.
SUPPLY_CONTACTS = 3
CONTACT_RATING_A = 1.0


@dataclass(frozen=True)
class ChargePathBudget:
    """What the switch does at the edges of its published spread."""

    @property
    def conduction_drop_v(self) -> float:
        """Drop across the switch at the most a compliant source can deliver."""
        return SOURCE_MAX_A * SWITCH_RDSON_MAX_OHM

    @property
    def limit_headroom_a(self) -> float:
        """Margin between the guaranteed-lowest limit and the legitimate load."""
        return SWITCH_LIMIT_MIN_A - SOURCE_MAX_A

    @property
    def contact_capability_a(self) -> float:
        return SUPPLY_CONTACTS * CONTACT_RATING_A

    @property
    def fault_exceeds_contacts_by_a(self) -> float:
        """How far a worst-case fault current overshoots the harness rating.

        Positive means the switch can pass more than the connector is rated for
        while it is in limit, until its thermal protection intervenes. Contact
        ratings are continuous and this condition is not, which is why it is
        recorded for V8 measurement rather than treated as a static violation.
        """
        return SWITCH_LIMIT_MAX_A - self.contact_capability_a
