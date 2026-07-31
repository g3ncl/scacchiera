"""What the 3.3 V rail does across a warm reset and a power cycle.

`rail_budget` covers the cases that end with the rail in regulation: dropout,
soft start, and how long the capacitors hold the MCU up. This covers the two
that end with it somewhere else.

A warm reset leaves the rail alone, so nothing on it sees a power-on reset and
every peripheral keeps the state firmware left it in. A power cycle only resets
those peripherals if the rail actually reaches their power-on reset floor, and
the TCA9535 is explicit that it will not reset again until its supply has been
below VPORF. Nothing else on this board discharges 3V3: the AP63203 is the
fixed-output part, so there is no feedback divider, it has no output discharge,
and every other pull ends on a high-impedance node. Hub R36 is what makes the
decay a specified number instead of a leakage guess.
"""

from dataclasses import dataclass
from functools import cache
from math import log

from hardware.pcb.hub import build_hub
from hardware.pcb.matrix import build_matrix
from hardware.verification.net_capacitance import net_capacitance_f


# TCA9535PWR data sheet, Electrical Characteristics and section 7.4.1: the
# device holds reset until VCC reaches VPORR, and VCC must go back below VPORF
# before another power-on reset happens. VPORF is 0.75 V minimum, so that, not
# the 1 V maximum, is the level a decay has to reach to guarantee the reset.
EXPANDER_POR_FLOOR_V = 0.75

REGULATED_V = 3.30

# Hub R36, 0603WAF1002T5E at its 1 percent tolerance. The high end is the slow
# discharge and the low end is the largest standing current, so each bound is
# used where it is the pessimistic one.
BLEED_NOMINAL_OHM = 10e3
BLEED_TOLERANCE = 0.01

# Rounded-up coincident load the bleed current is judged against, the same
# figure `rail_budget` uses for the 3.3 V rail.
INTERFACE_LOAD_A = 1.34

# Neither display module publishes its input capacitance, and the harness that
# carries 3V3 to them is not bound. 20 uF each is an acceptance limit on what a
# module may present, in the same spirit as the 50 pF display SPI load bound.
# More capacitance is the slower decay, so the bound is the pessimistic side.
DISPLAY_INPUT_ALLOWANCE_F = 20e-6
DISPLAY_COUNT = 2


@cache
def rail_capacitance_f() -> float:
    """Everything hanging on 3V3, nominal, plus the unbound display allowance.

    Nominal rather than bias-derated: derating removes capacitance, which
    speeds the decay up, and the decay is the number that has to stay bounded.
    """
    return (
        net_capacitance_f(build_hub(), "3V3")
        + net_capacitance_f(build_matrix(), "3V3")
        + DISPLAY_INPUT_ALLOWANCE_F * DISPLAY_COUNT
    )


@dataclass(frozen=True)
class PowerOffDischarge:
    capacitance_f: float
    bleed_ohm: float = BLEED_NOMINAL_OHM * (1.0 + BLEED_TOLERANCE)

    @property
    def time_to_por_floor_s(self) -> float:
        """How long the rail takes to fall far enough to guarantee a reset."""
        return (
            self.bleed_ohm
            * self.capacitance_f
            * log(REGULATED_V / EXPANDER_POR_FLOOR_V)
        )

    @property
    def bleed_current_a(self) -> float:
        """Standing current, at the tolerance end that draws the most."""
        return REGULATED_V / (BLEED_NOMINAL_OHM * (1.0 - BLEED_TOLERANCE))

    @property
    def bleed_percent_of_load(self) -> float:
        return 100.0 * self.bleed_current_a / INTERFACE_LOAD_A

    def resets_after_off_time(self, off_time_s: float) -> bool:
        """Whether an interruption of this length guarantees a clean restart.

        A repeated brownout is this question asked over and over: anything
        shorter brings the expander back holding its old register contents.
        """
        return off_time_s >= self.time_to_por_floor_s


@cache
def expander_driven_nets() -> tuple[str, ...]:
    """Hub nets whose level survives an MCU reset.

    The TCA9535 has no reset pin and the rail does not move during a warm
    reset, so every P-port net comes back driven at whatever firmware last
    wrote, and the passive pulls that define these nets at cold start lose to
    the expander's push-pull driver. Enumerated from the schematic so adding a
    signal to the expander forces this case to be looked at again.
    """
    circuit = build_hub()
    expander = next(part for part in circuit.parts if str(part.ref) == "U6")
    port_pins = tuple(str(number) for number in (*range(4, 12), *range(13, 21)))
    return tuple(
        sorted(
            {
                str(expander[pin].net.name)
                for pin in port_pins
                if expander[pin].net is not None
                and not str(expander[pin].net.name).startswith("__NOCONNECT")
            }
        )
    )


@cache
def reset_domain_refs() -> tuple[str, ...]:
    """What the MCU's own reset line reaches.

    Nothing but the MCU, its pull-up and its test pad: there is no reset that
    is distributed to the peripherals, which is why a warm reset leaves them
    running.
    """
    circuit = build_hub()
    mcu = next(part for part in circuit.parts if str(part.ref) == "U4")
    return tuple(sorted({str(pin.part.ref) for pin in mcu["8"].net.pins}))
