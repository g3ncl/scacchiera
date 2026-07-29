"""Small SKiDL part helpers shared by the board schematics."""

from collections.abc import Iterable
from dataclasses import dataclass

from skidl import Circuit, Net, Part


JLC_PART_BY_MPN = {
    "0402B223K500NT": "C1532",
    "0402CG101J500NT": "C1546",
    "0402CG150J500NT": "C1548",
    "0603WAF1000T5E": "C22775",
    "0603WAF1001T5E": "C21190",
    "0603WAF1002T5E": "C25804",
    "0603WAF1003T5E": "C25803",
    "0603WAF1004T5E": "C22935",
    "0603WAF2001T5E": "C22975",
    "0603WAF2492T5E": "C25962",
    "0603WAF3303T5E": "C23137",
    "0603WAF3902T5E": "C23153",
    "0603WAF4701T5E": "C23162",
    "0603WAF5101T5E": "C23186",
    "0603WAF8202T5E": "C23254",
    "0603WAF9102T5E": "C23265",
    "74HC595D,118": "C5947",
    "A1257WR-S-4P": "C225127",
    "AP22811AW5-7": "C3001660",
    "AP63203WU-7": "C780769",
    "B2B-PH-K-S(LF)(SN)": "C131337",
    "BQ25619RTWR": "C2864534",
    "BQ25895RTWR": "C80200",
    "CSD25404Q3": "C2865523",
    "BAT54H": "C475620",
    "CC1206KKX7RCBB472": "C107198",
    "CL32A107MQVNNNE": "C49066",
    "DFE201610E-R47M=P2": "C269773",
    "DFE252012F-1R0M=P2": "C435392",
    "DMP2035U-7": "C110499",
    "GRM1555C1H221JA01D": "C71693",
    "GRM1555C1H680JA01D": "C76977",
    "JS102011SAQN": "C221660",
    "LQW2BASR47J00L": "C337959",
    "MCP73871T-2CCI/ML": "C511310",
    "CDMC8D28NP-1R2MC": "C17268233",
    "430450200": "C122431",
    "430450800": "C122422",
    "MF-MSMF050-2": "C17313",
    "PN5180A0HN/C3E": "C1526287",
    "NR6045S4R7MT": "C42370396",
    "RC0603FR-07110KL": "C137807",
    "RC0603FR-07511KL": "C188257",
    "RC0603FR-07732KL": "C246003",
    "SN74AHCT1G125DBVR": "C7484",
    "SM02B-GHS-TB(LF)(SN)": "C189893",
    "TCA9535PWR": "C130204",
    "TLV7042DGKR": "C2760466",
    "TLV7021DCKR": "C702120",
    "TPS2553DBVR-1": "C111738",
    "TPS61023DRLR": "C919459",
    "TPS61088RHLR": "C87357",
    "TLV809K33DBVR": "C48241",
    "TPS63802DLAR": "C2845237",
    "USB4105-GF-A": "C3020560",
    "USBLC6-2SC6": "C2687116",
    "BAR64-02V": "C5295579",
    "BSS123-7-F": "C85107",
    "BSS84-7-F": "C85202",
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
    "ESP32-C6-MINI-1U-N4": "C7558096",
    "7M27100009": "C90919",
}

JLC_BASIC_CODES = frozenset(
    {
        "C1046", "C1525", "C1532", "C1546", "C1548", "C15849", "C15850", "C1779",
        "C21190", "C22775", "C22935", "C22975", "C23137", "C23153", "C23162",
        "C23186", "C23254", "C23630", "C25803", "C25804", "C32949", "C45783",
        "C52923", "C5947",
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
    supplier: str = "",
    order_code: str = "",
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
    part.supplier = supplier or ("JLCPCB" if part.lcsc_part else "")
    part.order_code = order_code or part.lcsc_part
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


def mounting_hole(circuit: Circuit, ref: str, ground: Net) -> Part:
    """Put a plated mechanical hole in both schematic and PCB netlists."""
    hole = component(
        circuit,
        ref,
        "M2.5 plated mounting hole",
        "MountingHole:MountingHole_2.7mm_M2.5_Pad",
        (PinDefinition("1", "GND"),),
        mpn="",
        description="Plated mounting hole, not a purchased component",
        unit_cost_eur=0.0,
        fitted=False,
    )
    ground += hole["1"]
    return hole


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


def esp32_c6_mini_1u(circuit: Circuit, ref: str) -> Part:
    """ESP32-C6-MINI-1U, pin names straight from datasheet v1.5 Table 3-1.

    The C6 is only pin compatible with the C3-MINI series on power, ground, EN
    and UART0. The GPIO assignments differ, and critically the native USB moves
    from IO18/IO19 (C3 pins 26/27) to IO12/IO13 on pins 17/18, while pin 21
    becomes NC. Anything reusing a C3 pin map here silently mis-wires USB.
    """
    signal_pins = {
        3: "3V3", 5: "IO2", 6: "IO3", 8: "EN", 9: "IO4", 10: "IO5",
        12: "IO0", 13: "IO1", 15: "IO6", 16: "IO7", 17: "IO12_USB_D-",
        18: "IO13_USB_D+", 19: "IO14", 20: "IO15", 22: "IO8", 23: "IO9",
        24: "IO18", 25: "IO19", 26: "IO20", 27: "IO21", 28: "IO22",
        29: "IO23", 30: "RXD0", 31: "TXD0",
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
        "ESP32-C6-MINI-1U-N4",
        "Chessboard:ESP32-C6-MINI-1U",
        pins,
        mpn="ESP32-C6-MINI-1U-N4",
        description="WiFi 6 and BLE module with external antenna connector",
        unit_cost_eur=3.89,
        supplier="DigiKey",
        order_code="1965-ESP32-C6-MINI-1U-N4CT-ND",
    )


def tps63802(circuit: Circuit, ref: str) -> Part:
    names = ("EN", "MODE", "AGND", "FB", "PG", "VOUT", "L2", "GND", "L1", "VIN", "EP_GND")
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
    part = Part(
        "Connector",
        "USB_C_Receptacle_USB2.0_16P",
        tool="kicad9",
        circuit=circuit,
        ref=ref,
        tag=ref,
    )
    part.value = "USB4105-GF-A"
    part.footprint = "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"
    part.manf_num = "USB4105-GF-A"
    part.lcsc_part = JLC_PART_BY_MPN["USB4105-GF-A"]
    part.supplier = "JLCPCB"
    part.order_code = part.lcsc_part
    part.jlc_library = "Extended"
    part.description = "USB-C USB 2.0 receptacle"
    part.unit_cost_eur = 0.55
    part.fitted = "yes"
    return part


def two_pin(
    circuit: Circuit,
    ref: str,
    value: str,
    footprint: str,
    *,
    mpn: str,
    unit_cost_eur: float,
    fitted: bool = True,
    supplier: str = "",
    order_code: str = "",
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
        supplier=supplier,
        order_code=order_code,
    )
