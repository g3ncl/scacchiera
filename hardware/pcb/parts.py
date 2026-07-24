"""Small SKiDL part helpers shared by the board schematics."""

from collections.abc import Iterable
from dataclasses import dataclass

from skidl import Circuit, Part


@dataclass(frozen=True)
class PinDefinition:
    number: str
    name: str


def component(
    circuit: Circuit,
    ref: str,
    value: str,
    footprint: str,
    pins: Iterable[PinDefinition],
    *,
    mpn: str,
    description: str,
    unit_cost_eur: float,
    fitted: bool = True,
) -> Part:
    # Generic connector symbols renamed pin by pin keep the schematic free of
    # per-device symbol libraries while still producing a correct netlist.
    pin_definitions = tuple(pins)
    part = Part(
        "Connector_Generic",
        f"Conn_01x{len(pin_definitions):02d}",
        tool="kicad9",
        circuit=circuit,
        ref=ref,
        tag=ref,
    )
    part.value = value
    part.footprint = footprint
    part.manf_num = mpn
    part.description = description
    part.unit_cost_eur = unit_cost_eur
    part.fitted = "yes" if fitted else "DNP"
    for index, pin in enumerate(pin_definitions, start=1):
        schematic_pin = part.p[str(index)]
        schematic_pin.num = pin.number
        schematic_pin.name = pin.name
    return part


def mosfet(circuit: Circuit, ref: str, mpn: str, *, unit_cost_eur: float) -> Part:
    return component(
        circuit,
        ref,
        mpn,
        "Package_TO_SOT_SMD:SOT-23",
        (PinDefinition("1", "G"), PinDefinition("2", "S"), PinDefinition("3", "D")),
        mpn=mpn,
        description="SOT-23 MOSFET",
        unit_cost_eur=unit_cost_eur,
    )


def diode(circuit: Circuit, ref: str, mpn: str, *, unit_cost_eur: float) -> Part:
    """A two-pin diode, anode on pin 1 (A) and cathode on pin 2 (K)."""
    return component(
        circuit,
        ref,
        mpn,
        "Diode_SMD:D_SOD-523",
        (PinDefinition("1", "A"), PinDefinition("2", "K")),
        mpn=mpn,
        description="Silicon PIN diode RF switch",
        unit_cost_eur=unit_cost_eur,
    )


def esp32_c3_mini_1u(circuit: Circuit, ref: str) -> Part:
    signal_pins = {
        3: "3V3", 5: "IO2", 6: "IO3", 8: "EN", 12: "IO0", 13: "IO1",
        16: "IO10", 18: "IO4", 19: "IO5", 20: "IO6", 21: "IO7", 22: "IO8",
        23: "IO9", 26: "IO18_USB_D-", 27: "IO19_USB_D+", 30: "RXD0", 31: "TXD0",
    }
    ground_pins = {1, 2, 11, 14, *range(36, 54)}
    pins: list[PinDefinition] = []
    for number in range(1, 54):
        if number in signal_pins:
            name = signal_pins[number]
        elif number in ground_pins:
            name = "GND"
        else:
            name = "NC"
        pins.append(PinDefinition(str(number), name))
    return component(
        circuit,
        ref,
        "ESP32-C3-MINI-1U-N4X",
        "Chessboard:ESP32-C3-MINI-1U",
        pins,
        mpn="ESP32-C3-MINI-1U-N4X",
        description="WiFi and BLE module with external antenna connector",
        unit_cost_eur=2.20,
    )


def tps63802(circuit: Circuit, ref: str) -> Part:
    names = ("EN", "MODE", "AGND", "FB", "PG", "VOUT", "L2", "GND", "L1", "VIN")
    return component(
        circuit,
        ref,
        "TPS63802DLAR",
        "Package_SON:Texas_S-PVSON-N10",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="TPS63802DLAR",
        description="2 A buck-boost regulator",
        unit_cost_eur=1.10,
    )


def usb_c_receptacle(circuit: Circuit, ref: str) -> Part:
    pins = (
        PinDefinition("A1", "GND"), PinDefinition("A4", "VBUS"), PinDefinition("A5", "CC1"),
        PinDefinition("A6", "D+"), PinDefinition("A7", "D-"), PinDefinition("A8", "SBU1"),
        PinDefinition("A9", "VBUS"), PinDefinition("A12", "GND"),
        PinDefinition("B1", "GND"), PinDefinition("B4", "VBUS"), PinDefinition("B5", "CC2"),
        PinDefinition("B6", "D+"), PinDefinition("B7", "D-"), PinDefinition("B8", "SBU2"),
        PinDefinition("B9", "VBUS"), PinDefinition("B12", "GND"),
        PinDefinition("S1", "SHIELD"),
    )
    return component(
        circuit,
        ref,
        "USB4105-GF-A",
        "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
        pins,
        mpn="USB4105-GF-A",
        description="USB-C USB 2.0 receptacle",
        unit_cost_eur=0.55,
    )


def two_pin(
    circuit: Circuit,
    ref: str,
    value: str,
    footprint: str,
    *,
    mpn: str,
    unit_cost_eur: float,
    fitted: bool = True,
) -> Part:
    return component(
        circuit,
        ref,
        value,
        footprint,
        (PinDefinition("1", "1"), PinDefinition("2", "2")),
        mpn=mpn,
        description=value,
        unit_cost_eur=unit_cost_eur,
        fitted=fitted,
    )
