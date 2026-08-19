"""What the light-bar rail does at a current limit, and what an open cable does.

The limiter is a latch-off part, which makes its deglitch window the interesting
number in both directions. Too short and a normal power-on into the bars' bulk
capacitance latches the rail off before it has finished charging. Too long and a
real short stays energised. The window is fixed, so what has to be checked is
that the design's own startup fits inside it.

The open cable is the other half. A limiter reports overcurrent and reverse
voltage and nothing else, so an unplugged bar is invisible to it. What matters
then is only that nothing on the board is left floating, which is a property of
the schematic and is read from it.
"""

from dataclasses import dataclass
from functools import cache

from hardware.pcb.hub import build_hub
from hardware.pcb.lightbar import build_lightbar
from hardware.verification.net_capacitance import net_capacitance_f


LED_RAIL_V = 5.0

# TPS2553DBVR-1 data sheet, Electrical Characteristics. The FAULT deglitch is
# 5 ms minimum and 10 ms maximum for an overcurrent condition, and the part
# latches off when that window expires. The minimum is what a legitimate
# startup has to finish inside; the maximum is how long a real fault lasts.
DEGLITCH_MIN_MS = 5.0
DEGLITCH_MAX_MS = 10.0

# Same data sheet, section 9.5.1, with the board's 39 kOhm ILIM resistor:
#   IOSmin = 25230 / R^1.016, IOSnom = 23950 / R^0.977, IOSmax = 22980 / R^0.94
# The minimum is the pessimistic one here, because less current means the bulk
# capacitance takes longer to charge and so longer to leave current limit.
LIMIT_RESISTOR_KOHM = 39.0
LIMIT_FLOOR_A: float = 25230.0 / pow(LIMIT_RESISTOR_KOHM, 1.016) / 1000.0
LIMIT_CEILING_A: float = 22980.0 / pow(LIMIT_RESISTOR_KOHM, 0.94) / 1000.0

LIGHTBAR_COUNT = 2


@cache
def led_rail_capacitance_f() -> float:
    """Nominal capacitance the limiter has to charge, both bars included.

    Nominal rather than bias-derated, because the ceramic loses capacitance
    under bias and less capacitance leaves current limit sooner, so the full
    printed value is the one that stays in current limit longest.
    """
    return (
        net_capacitance_f(build_hub(), "LED_5V")
        + net_capacitance_f(build_lightbar(), "LED_5V") * LIGHTBAR_COUNT
    )


@dataclass(frozen=True)
class LightbarLimiterFault:
    capacitance_f: float

    @property
    def current_limit_ms(self) -> float:
        """How long a cold start sits in current limit charging the bars.

        The inrush a soft start alone would draw is well over the limiter's
        threshold, so the rail charges at the limit current instead of on the
        soft-start ramp, and this is how long that takes.
        """
        return 1e3 * self.capacitance_f * LED_RAIL_V / LIMIT_FLOOR_A

    @property
    def capacitance_ceiling_f(self) -> float:
        """Most capacitance the rail may carry before a startup latches it off."""
        return LIMIT_FLOOR_A * DEGLITCH_MIN_MS * 1e-3 / LED_RAIL_V

    @property
    def short_circuit_energy_mj(self) -> float:
        """Energy a dead short takes before the latch opens the switch."""
        return LED_RAIL_V * LIMIT_CEILING_A * DEGLITCH_MAX_MS


@cache
def floating_nets_when_a_cable_is_absent() -> tuple[str, ...]:
    """Hub nets left with no driver and no pull when a harness is unplugged.

    A net that only ever appears on two connectors is driven from the far end
    of a cable, so removing that cable leaves whatever else it reaches with a
    floating input. Read from the schematic rather than listed by hand.
    """
    circuit = build_hub()
    floating: list[str] = []
    for net in circuit.nets:
        refs = {str(pin.part.ref) for pin in net.pins}
        if len(refs) > 1 and all(ref.startswith("J") for ref in refs):
            floating.append(str(net.name))
    return tuple(sorted(floating))
