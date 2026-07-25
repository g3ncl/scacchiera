"""Small SKiDL part helpers shared by the board schematics."""

from collections.abc import Iterable
from dataclasses import dataclass

from skidl import Circuit, Part


JLC_PART_BY_MPN = {
    "0402CG101J500NT": "C1546",
    "0603WAF1000T5E": "C22775",
    "0603WAF1001T5E": "C21190",
    "0603WAF1002T5E": "C25804",
    "0603WAF1003T5E": "C25803",
    "0603WAF1004T5E": "C22935",
    "0603WAF2001T5E": "C22975",
    "0603WAF2492T5E": "C25962",
    "0603WAF3303T5E": "C23137",
    "0603WAF4701T5E": "C23162",
    "0603WAF5101T5E": "C23186",
    "0603WAF8202T5E": "C23254",
    "0603WAF9102T5E": "C23265",
    "74HC595D,118": "C5947",
    "A1257WR-S-4P": "C225127",
    "B2B-PH-K-S(LF)(SN)": "C131337",
    "BAT54H": "C475620",
    "CC1206KKX7RCBB472": "C107198",
    "CL32A107MQVNNNE": "C49066",
    "DFE201610E-R47M=P2": "C269773",
    "DMP2035U-7": "C110499",
    "GRM1555C1H221JA01D": "C71693",
    "GRM1555C1H680JA01D": "C76977",
    "JS102011SAQN": "C221660",
    "LQW2BASR47J00L": "C337959",
    "MCP73871T-2CCI/ML": "C511310",
    "MF-MSMF050-2": "C17313",
    "PN5180A0HN/C3E": "C1526287",
    "RC0603FR-07110KL": "C137807",
    "RC0603FR-07511KL": "C188257",
    "RC0603FR-07732KL": "C246003",
    "SN74AHCT1G125DBVR": "C7484",
    "SM02B-GHS-TB(LF)(SN)": "C189893",
    "TCA9535PWR": "C130204",
    "TPS2553DBVR-1": "C111738",
    "TPS61023DRLR": "C919459",
    "TPS63802DLAR": "C2845237",
    "USB4105-GF-A": "C3020560",
    "USBLC6-2SC6": "C2687116",
    "BAR64-02V": "C5295579",
    "BSS123": "C7420338",
    "BSS84": "C114481",
    "CC0603FRNPO9BN221": "C519500",
    "CL05B104KO5NNNC": "C1525",
    "CL05A105KA5NQNC": "C52923",
    "CL05C100JB5NNNC": "C32949",
    "CL10A105KB8NNNC": "C15849",
    "CL21A106KAYNNNE": "C15850",
    "CL21A226MAQNNNE": "C45783",
    "CL21A475KAQNNNE": "C1779",
    "CL10A225KO8NNNC": "C23630",
    "RS-03K1800FT": "C286574",
    "SDFL2012S100KTF": "C1046",
    "SM07B-GHS-TB(LF)(SN)": "C495552",
    "0603WAF150KT5E": "C22769",
}

JLC_BASIC_CODES = frozenset(
    {
        "C1046", "C1525", "C1546", "C15849", "C15850", "C1779", "C21190",
        "C22775", "C22935", "C22975", "C23137", "C23162", "C23186", "C23254",
        "C23630", "C25803", "C25804", "C32949", "C45783", "C52923", "C5947",
    }
)


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
    part.lcsc_part = JLC_PART_BY_MPN.get(mpn, "")
    if not part.lcsc_part:
        part.jlc_library = "Unbound"
    elif part.lcsc_part in JLC_BASIC_CODES:
        part.jlc_library = "Basic"
    else:
        part.jlc_library = "Extended"
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
