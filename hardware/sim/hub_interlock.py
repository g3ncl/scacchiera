"""Corner sweep of the hub's cell-temperature charge interlock in ngspice.

The gate is the only thing standing between a cold or hot cell and the
PiSugar's charger, so its trip points have to hold over every tolerance the
parts publish, not at nominal. The deck instantiates one copy of the gate per
corner from the same SKiDL objects as the netlist, hangs the filed Vishay R/T
curve on each copy's sensor port as a behavioral resistance, and sweeps that
curve's temperature control node. Each copy reports the two temperatures where
the enable pin crosses the load switch's guaranteed input high level.

Reported thresholds carry the sensor's own published accuracy on top of the
simulated circuit result: the gate can only be as right as the bead reading it.

Every reported edge is a linear interpolation between sweep points, so it is
granular to the sweep step below. The comparator transition is three orders
sharper than that step, and the step is two orders below the margin the gate
needs, so refining it would move nothing that matters.
"""

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Iterator

from skidl import Circuit, Net

from hardware.pcb.hub import build_hub
from hardware.sim.matrix_rf import _run_deck
from hardware.sim.spice import MODELS_DIR, emit_subckt
from hardware.sim.thermistor import accuracy_k, resistance_ohm, spice_expression


GENERATED_DIR = Path(__file__).parent / "generated" / "hub"

# The gate: NTC bias, both reference dividers, the wired-OR pull-up, the ADC
# tap that loads the sense node, and the comparator itself.
GATE_PARTS = frozenset(
    {"R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "C17", "U2"}
)
# Three things touch these nets from outside that set. The sensor at J11 and the
# switch enable at U1 are modelled below. The third is the MCU's ADC input on
# TEMP_SENSE_ADC, whose leakage the module data sheet does not publish: it sits
# behind R13's 1 Mohm, so even a leakage as large as the 1 uA the switch does
# publish would move the sense node about 7 mV, still inside the comparator
# error already swept.
PORT_NETS = ("USB_VBUS", "THERM_SENSE", "CHARGE_TEMP_OK", "TEMP_SENSE_ADC")

# Every gate resistor is a 1% part (0603WAF...T5E), checked in the V1 audit.
RESISTOR_TOLERANCE = 0.01

# AP22811AW5-7 data sheet, Electrical Characteristics: VIH is 1.5 V minimum and
# VIL 0.5 V maximum over its whole 2.7 to 5.5 V input range. Charging is only
# permitted where the enable pin is guaranteed to read high.
ENABLE_HIGH_V = 1.5
ENABLE_LOW_V = 0.5

# TLV7042 data sheet section 5.9: VIO 8 mV maximum plus VHYS 25 mV maximum. The
# hysteresis displaces the trip by up to its full published value depending on
# which side the input arrives from, so the worst case takes both at once.
COMPARATOR_ERROR_V = 0.033

# A conservative superset of the 5 V a USB-C source presents. The dividers are
# ratiometric, so the sweep exists to show the thresholds barely move across it
# rather than to lean on any particular bound.
SUPPLY_V = (4.5, 5.0, 5.5)

# AP22811AW5-7 data sheet: ILEAK-EN is 1 uA maximum. Drawn out of the pull-up
# node it is the worst case for the high level, and the direction that matters:
# pushed into the node it would add 0.1 mV to a 6 mV low level.
ENABLE_LEAKAGE_A = 1e-6

SWEEP_START_C = -20.0
SWEEP_STOP_C = 60.0
SWEEP_STEP_C = 0.05

# docs/functional/power.md states the charge times at 20 to 25 degrees Celsius,
# so the gate must be conducting across that band in every corner.
FUNCTIONAL_CHARGE_C = 22.5
# Cold enough to sit outside even the widest permitted window.
INHIBITED_C = -15.0

# An unplugged connector and a crushed bead are the two ends of the sensor's
# failure range. Both must leave the gate inhibited rather than charging blind.
SENSOR_FAULTS: dict[str, float] = {"open": 1e12, "short": 1e-3}


@dataclass(frozen=True)
class Corner:
    """One vertex of the tolerance box, plus the device error direction."""

    supply_v: float
    bias: float
    cold_top: float
    cold_bottom: float
    hot_top: float
    hot_bottom: float
    adc: float
    widening: bool

    @property
    def offset_v(self) -> float:
        # Positive offset delays both trips, which widens the permitted window
        # past the cell's real temperature. That is the unsafe direction.
        return COMPARATOR_ERROR_V if self.widening else -COMPARATOR_ERROR_V

    def values(self) -> dict[str, str]:
        """Value overrides for this vertex, keyed by designator.

        Series members of one divider leg move together. Each leg's extreme sum
        is a vertex of the box, and the trip condition is monotone in every
        resistance, so the extremes bound every interior combination.
        """
        offset = f"vos_a={self.offset_v:.6f} vos_b={self.offset_v:.6f}"
        return {
            "R4": f"{10e3 * self.bias:.4f}",
            "R5": f"{39e3 * self.cold_top:.4f}",
            "R6": f"{100e3 * self.cold_bottom:.4f}",
            "R7": f"{100e3 * self.hot_top:.4f}",
            "R8": f"{100e3 * self.hot_top:.4f}",
            "R9": f"{100e3 * self.hot_top:.4f}",
            "R10": f"{100e3 * self.hot_bottom:.4f}",
            "R11": f"{100e3 * self.hot_bottom:.4f}",
            "R13": f"{1e6 * self.adc:.4f}",
            "R14": f"{1e6 * self.adc:.4f}",
            "U2": offset,
        }


@dataclass(frozen=True)
class Threshold:
    """One corner's simulated window, and its edges once the bead can be wrong.

    Sensor error is signed against the question being asked. Judging whether the
    gate can permit a forbidden temperature, assume the bead reads toward the
    middle of the window; judging whether it can refuse a permitted one, assume
    the opposite. Taking one direction for both understates the risk on one side.
    """

    corner: Corner
    cold_c: float
    hot_c: float

    @property
    def cold_permissive_c(self) -> float:
        """Coldest real cell the gate might still charge, the bead reading warm."""
        return self.cold_c - accuracy_k(self.cold_c)

    @property
    def hot_permissive_c(self) -> float:
        """Hottest real cell the gate might still charge, the bead reading cool."""
        return self.hot_c + accuracy_k(self.hot_c)

    @property
    def cold_restrictive_c(self) -> float:
        """Warmest real cell the gate might still refuse, the bead reading cool."""
        return self.cold_c + accuracy_k(self.cold_c)

    @property
    def hot_restrictive_c(self) -> float:
        """Coolest real cell the gate might still refuse, the bead reading warm."""
        return self.hot_c - accuracy_k(self.hot_c)


@dataclass(frozen=True)
class InterlockResult:
    thresholds: tuple[Threshold, ...]
    enable_high_v: float
    enable_low_v: float
    fault_enable_v: dict[str, float]

    @property
    def widest(self) -> tuple[float, float]:
        """The permitted window at its worst, which must stay inside the safe range."""
        widening = [t for t in self.thresholds if t.corner.widening]
        return (
            min(t.cold_permissive_c for t in widening),
            max(t.hot_permissive_c for t in widening),
        )

    @property
    def narrowest(self) -> tuple[float, float]:
        """The permitted window at its tightest, which must still cover normal use."""
        narrowing = [t for t in self.thresholds if not t.corner.widening]
        return (
            max(t.cold_restrictive_c for t in narrowing),
            min(t.hot_restrictive_c for t in narrowing),
        )


def corners() -> Iterator[Corner]:
    extremes = (1.0 - RESISTOR_TOLERANCE, 1.0 + RESISTOR_TOLERANCE)
    for supply, widening in product(SUPPLY_V, (True, False)):
        for bias, cold_top, cold_bottom, hot_top, hot_bottom, adc in product(
            extremes, repeat=6
        ):
            yield Corner(
                supply_v=supply,
                bias=bias,
                cold_top=cold_top,
                cold_bottom=cold_bottom,
                hot_top=hot_top,
                hot_bottom=hot_bottom,
                adc=adc,
                widening=widening,
            )


def _faults() -> tuple[tuple[str, float, Corner], ...]:
    """Sensor failures, at nominal resistors and the offset that resists asserting."""
    return tuple(
        (
            name,
            ohm,
            Corner(
                supply_v=supply,
                bias=1.0,
                cold_top=1.0,
                cold_bottom=1.0,
                hot_top=1.0,
                hot_bottom=1.0,
                adc=1.0,
                widening=True,
            ),
        )
        for name, ohm in SENSOR_FAULTS.items()
        for supply in SUPPLY_V
    )


def deck(corner_list: tuple[Corner, ...], faults: tuple[tuple[str, float, Corner], ...]) -> str:
    circuit = build_hub()
    ports = tuple(
        next(net for net in circuit.get_nets() if str(net.name) == name)
        for name in PORT_NETS
    )
    lines = [
        "Hub cell-temperature charge interlock, one gate copy per tolerance corner",
        f'.include "{MODELS_DIR / "tlv7042.lib"}"',
        "Vtemp temp 0 DC 0",
    ]
    measurements: list[str] = []
    for index, corner in enumerate(corner_list):
        lines.extend(_gate_copy(circuit, ports, index, corner))
        lines.append(f"Rntc{index} sense{index} 0 R = '{spice_expression('temp')}'")
        measurements.append(f"meas dc cold{index} when v(ok{index})={ENABLE_HIGH_V} rise=1")
        measurements.append(f"meas dc hot{index} when v(ok{index})={ENABLE_HIGH_V} fall=1")
        measurements.append(f"meas dc high{index} find v(ok{index}) at={FUNCTIONAL_CHARGE_C}")
        measurements.append(f"meas dc low{index} find v(ok{index}) at={INHIBITED_C}")
    for offset, (name, ohm, corner) in enumerate(faults):
        index = len(corner_list) + offset
        lines.extend(_gate_copy(circuit, ports, index, corner))
        # A fixed sensor ignores the sweep, so any sweep point reads the same.
        lines.append(f"Rntc{index} sense{index} 0 {ohm:.6e}")
        measurements.append(
            f"meas dc fault_{name}_{offset} find v(ok{index}) at={FUNCTIONAL_CHARGE_C}"
        )
    lines.append(".control")
    lines.append(f"dc Vtemp {SWEEP_START_C} {SWEEP_STOP_C} {SWEEP_STEP_C}")
    lines.extend(measurements)
    lines.append("quit")
    lines.append(".endc")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def _gate_copy(circuit: Circuit, ports: tuple[Net, ...], index: int, corner: Corner) -> list[str]:
    block = f"GATE{index}"
    return [
        emit_subckt(circuit, block, ports, only=GATE_PARTS, values=corner.values()).rstrip("\n"),
        f"Vbus{index} vbus{index} 0 DC {corner.supply_v}",
        f"Xgate{index} vbus{index} sense{index} ok{index} adc{index} {block}",
        f"Ien{index} ok{index} 0 DC {ENABLE_LEAKAGE_A:.3e}",
    ]


def run() -> InterlockResult:
    corner_list = tuple(corners())
    faults = _faults()
    output = _run_deck(deck(corner_list, faults), GENERATED_DIR / "interlock.cir")
    measured = _parse_measurements(output)

    def required(key: str) -> float:
        value = measured.get(key)
        if value is None:
            raise RuntimeError(f"ngspice reported no measurement {key}")
        return value

    thresholds = tuple(
        Threshold(
            corner=corner,
            cold_c=required(f"cold{index}"),
            hot_c=required(f"hot{index}"),
        )
        for index, corner in enumerate(corner_list)
    )
    indices = range(len(corner_list))
    fault_enable = {
        name: max(
            required(f"fault_{name}_{offset}")
            for offset, (candidate, _, _) in enumerate(faults)
            if candidate == name
        )
        for name in SENSOR_FAULTS
    }
    return InterlockResult(
        thresholds=thresholds,
        enable_high_v=min(required(f"high{index}") for index in indices),
        enable_low_v=max(required(f"low{index}") for index in indices),
        fault_enable_v=fault_enable,
    )


def _parse_measurements(output: str) -> dict[str, float]:
    measured: dict[str, float] = {}
    for line in output.splitlines():
        name, separator, rest = line.partition("=")
        if not separator:
            continue
        key = name.strip()
        tokens = rest.split()
        if not tokens:
            continue
        try:
            measured[key] = float(tokens[0])
        except ValueError:
            continue
    return measured


if __name__ == "__main__":
    result = run()
    cold, hot = result.widest
    tight_cold, tight_hot = result.narrowest
    print(f"corners simulated: {len(result.thresholds)}")
    print(f"widest permitted window:    {cold:.2f} to {hot:.2f} C")
    print(f"narrowest permitted window: {tight_cold:.2f} to {tight_hot:.2f} C")
    print(f"enable high inside window:  {result.enable_high_v:.3f} V")
    print(f"enable low outside window:  {result.enable_low_v * 1e3:.3f} mV")
    for name, level in sorted(result.fault_enable_v.items()):
        print(f"enable with {name} sensor:    {level * 1e3:.3f} mV")
    print(f"sensor resistance at 0 C: {resistance_ohm(0.0):.1f} ohm")
