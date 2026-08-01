"""Signals that cross between rails, and what happens when one rail is late.

Rails do not come up together. The module's 5 V arrives first, the buck's 3.3 V
follows its own soft start, and the light-bar rail waits for firmware to enable
its limiter. USB's 5 V may never arrive at all. So any signal that leaves a part
on one rail and lands on a part on another spends real time being driven while
its destination is unpowered.

Whether that matters is a property of the receiving pin, and data sheets split
into three kinds. Most rate their logic pins against ground, which makes the
case a non-event. Some rate them against their own supply, which makes it a
violation unless the driver shares that supply. A few say nothing at all, and
then the only honest defence is that the current reaching the pin is bounded by
a resistor rather than by a promise.

The crossings are read from the schematic so a new one has to be classified
rather than quietly inherited.
"""

from dataclasses import dataclass

from functools import cache

from skidl import Circuit

from hardware.pcb.hub import build_hub


HUB_RAILS = frozenset(
    {"3V3", "LED_5V", "MODULE_5V", "USB_VBUS", "CHARGE_5V", "BAT_RAW"}
)


def _supply_rails(circuit: Circuit) -> dict[str, frozenset[str]]:
    """Which rails each integrated circuit is powered from."""
    supplies: dict[str, frozenset[str]] = {}
    for part in circuit.parts:
        reference = str(part.ref)
        if not reference.startswith("U"):
            continue
        rails = {
            str(pin.net.name)
            for pin in part.pins
            if pin.net is not None and str(pin.net.name) in HUB_RAILS
        }
        if rails:
            supplies[reference] = frozenset(rails)
    return supplies


@cache
def crossing_nets() -> tuple[str, ...]:
    """Signals joining two integrated circuits that do not share a supply.

    Two devices are needed, not one: a converter's switching node and a
    programming resistor also touch two rails, but both ends of those belong to
    the same part and neither is a signal one rail can start without.
    """
    circuit = build_hub()
    supplies = _supply_rails(circuit)
    crossings: list[str] = []
    for net in circuit.nets:
        name = str(net.name)
        if name in HUB_RAILS or name == "GND" or name.startswith("__"):
            continue
        devices = {
            str(pin.part.ref) for pin in net.pins if str(pin.part.ref) in supplies
        }
        if len(devices) < 2:
            continue
        rails: set[str] = set()
        for device in devices:
            rails |= supplies[device]
        if len(rails) > 1:
            crossings.append(name)
    return tuple(sorted(crossings))


@dataclass(frozen=True)
class Crossing:
    """One cross-rail signal and the basis its receiving pin is rated on."""

    net: str
    receiver: str
    rated_against_ground: bool
    pull_ohm: float | None
    note: str

    @property
    def injected_current_a(self) -> float:
        """Worst current into the receiving pin while its own rail is down.

        Zero when the pin is rated against ground, because then nothing is out
        of specification and there is no injection to bound.
        """
        if self.rated_against_ground or self.pull_ohm is None:
            return 0.0
        return PULL_SUPPLY_V / self.pull_ohm


PULL_SUPPLY_V = 3.30

CROSSINGS = (
    Crossing(
        net="LED_DATA",
        receiver="U8 SN74AHCT1G125DBVR pin 2",
        rated_against_ground=True,
        pull_ohm=None,
        note=(
            "Absolute Maximum Ratings give the input voltage range as -0.5 to 7 V "
            "and the recommended range as 0 to 5.5 V, neither referred to VCC, so "
            "the MCU may drive this before the light-bar rail exists."
        ),
    ),
    Crossing(
        net="LED_EN",
        receiver="U7 TPS2553DBVR-1 pin 3",
        rated_against_ground=True,
        pull_ohm=None,
        note=(
            "Absolute Maximum Ratings cover IN, OUT, EN, ILIM and FAULT together "
            "at -0.3 to 7 V, with a note that voltages are referenced to GND."
        ),
    ),
    Crossing(
        net="LED_FAULT_N",
        receiver="U7 TPS2553DBVR-1 pin 4",
        rated_against_ground=True,
        pull_ohm=None,
        note="Same ground-referenced -0.3 to 7 V row as EN.",
    ),
    Crossing(
        net="CHARGE_TEMP_OK",
        receiver="U1 AP22811AW5-7 pin 4",
        rated_against_ground=False,
        pull_ohm=None,
        note=(
            "Enable is rated -0.3 V to VIN + 0.3 V, so it is not ground "
            "referenced. It is safe by construction instead: R12 pulls it to "
            "USB_VBUS and the comparator driving it runs from USB_VBUS, so the "
            "pin cannot exceed its own supply."
        ),
    ),
    Crossing(
        net="CHARGE_INPUT_FAULT_N",
        receiver="U1 AP22811AW5-7 pin 3",
        rated_against_ground=False,
        pull_ohm=100e3,
        note=(
            "Diodes lists VIN, VOUT and VEN in the Absolute Maximum table and no "
            "row at all for the fault flag, while the enable it does list is "
            "supply referenced. On battery with USB absent this pin sits at 3.3 V "
            "with VIN at zero, which is therefore an unspecified condition rather "
            "than a permitted one. What bounds it is R15: the pin cannot draw "
            "more than 3.3 V across 100 kOhm."
        ),
    ),
)

# Nothing may push more than this into a pin whose rating does not cover the
# condition. Well under the leakage currents the same data sheets specify, so a
# clamp conducting it dissipates microwatts.
INJECTION_CEILING_A = 100e-6
