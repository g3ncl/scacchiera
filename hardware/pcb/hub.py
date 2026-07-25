"""Hub board: power, WiFi MCU, ISO 15693 reader, and every external interface.

The power tree, MCU pin map, and peripheral rails are carried over from the
previous hub generation, which cleared ERC and review before the rebuild: USB-C
into an MCP73871 power-path charger, one protected Li-ion cell, a TPS63802
buck-boost making 3V3, and a gated TPS61023 5 V boost with a TPS2553 limiter
feeding the light bars through a 5 V data buffer.

What changed with the row-column matrix: the four quadrant harnesses and their
74HC139 decoder collapse into one 7-pin matrix link (RF bus between grounds,
3V3, and the selection registers' serial lines, shared with SPI), and the
reader is now a PN5180. ISO/IEC 15693 is what the BitwiseID whole-line reads
are proven on, and the NFC Game Board author measured the PN5180 matching the
CLRC632's inventory timings, so it is the de-risked choice. TX1 drives the
single-ended matrix bus through an EMC filter and a series match; TX2 carries
the mirrored EMC filter into ground so the push-pull driver stays balanced.
"""

from skidl import Circuit, Net, Part
from skidl.pin import pin_types

from hardware.pcb.parts import (
    PinDefinition,
    component,
    esp32_c3_mini_1u,
    tps63802,
    two_pin,
    usb_c_receptacle,
)


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def _pin_net(circuit: Circuit, name: str, part: Part, pin: str) -> Net:
    net = Net(name, circuit=circuit)
    _connect(net, part, pin)
    return net


def _no_connect(circuit: Circuit, part: Part, pins: tuple[str, ...]) -> None:
    for pin in pins:
        part[pin].func = pin_types.NOCONNECT
        circuit.NC += part[pin]


def _connector(circuit: Circuit, ref: str, names: tuple[str, ...], mpn: str, cost: float) -> Part:
    return component(
        circuit,
        ref,
        mpn,
        f"Connector_JST:JST_GH_SM{len(names):02d}B-GHS-TB_1x{len(names):02d}-1MP_P1.25mm_Horizontal",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn=mpn,
        description="Keyed service connector",
        unit_cost_eur=cost,
    )


def _rc(circuit: Circuit, ref: str, value: str, mpn: str, cost: float = 0.002) -> Part:
    footprint = (
        "Resistor_SMD:R_0603_1608Metric" if ref.startswith("R") else "Capacitor_SMD:C_0402_1005Metric"
    )
    return two_pin(circuit, ref, value, footprint, mpn=mpn, unit_cost_eur=cost)


def _charger(circuit: Circuit) -> Part:
    names = (
        "OUT", "VPCC", "SEL", "PROG2", "THERM", "PG_N", "STAT2", "STAT1_LBO", "TE_N", "VSS",
        "VSS", "PROG3", "PROG1", "VBAT", "VBAT", "VBAT_SENSE", "CE", "IN", "IN", "OUT", "VSS",
    )
    return component(
        circuit,
        "U1",
        "MCP73871T-2CCI/ML",
        "Package_DFN_QFN:QFN-20-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="MCP73871T-2CCI/ML",
        description="USB power-path Li-ion charger",
        unit_cost_eur=1.20,
    )


def _pn5180(circuit: Circuit) -> Part:
    names = (
        "NSS", "AUX2", "MOSI", "PVSS", "MISO", "PVDD", "SCK", "BUSY", "VSS", "RESET_N",
        "NC11", "VBAT", "VBAT", "NC14", "RXN", "RXP", "VMID", "TX2", "TVSS", "NC20",
        "TX1", "TVDD", "ANT1", "ANT2", "VDHF", "VBAT", "VSS", "AVDD", "VDD", "DVDD",
        "NC31", "NC32", "NC33", "NC34", "NC35", "CLK1", "CLK2", "GPO1", "IRQ", "AUX1",
    )
    return component(
        circuit,
        "U3",
        "PN5180A0HN/C3E",
        "Package_DFN_QFN:QFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="PN5180A0HN/C3E",
        description="ISO 15693 and NFC reader frontend",
        unit_cost_eur=3.80,
    )


def _led_boost(circuit: Circuit) -> Part:
    names = ("VIN", "EN", "FB", "GND", "VOUT", "SW")
    return component(
        circuit,
        "U5",
        "TPS61023DRLR",
        "Package_TO_SOT_SMD:Texas_R-PDSO-N6_DRL-6",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="TPS61023DRLR",
        description="True-disconnect 5 V LED boost",
        unit_cost_eur=0.60,
    )


def _led_limiter(circuit: Circuit) -> Part:
    names = ("IN", "GND", "EN", "FAULT_N", "ILIM", "OUT")
    return component(
        circuit,
        "U7",
        "TPS2553DBVR-1",
        "Package_TO_SOT_SMD:SOT-23-6",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="TPS2553DBVR-1",
        description="Latch-off LED rail current limiter",
        unit_cost_eur=0.50,
    )


def _io_expander(circuit: Circuit) -> Part:
    names = (
        "INT_N", "A1", "A2", "P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "GND",
        "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "A0", "SCL", "SDA", "VCC",
    )
    return component(
        circuit,
        "U6",
        "TCA9535PWR",
        "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="TCA9535PWR",
        description="Slow control expander: latch, resets, rails, button, status",
        unit_cost_eur=0.35,
    )


def _build_power(circuit: Circuit, nets: dict[str, Net]) -> None:
    usb = usb_c_receptacle(circuit, "J1")
    for pin in ("A1", "A12", "B1", "B12"):
        _connect(nets["GND"], usb, pin)
    for pin in ("A4", "A9", "B4", "B9"):
        _connect(nets["USB_VBUS_RAW"], usb, pin)
    for pin in ("A6", "B6"):
        _connect(nets["USB_D+"], usb, pin)
    for pin in ("A7", "B7"):
        _connect(nets["USB_D-"], usb, pin)
    _no_connect(circuit, usb, ("A8", "B8"))
    for index, pin in (("1", "A5"), ("2", "B5")):
        rd = _rc(circuit, f"R{index}", "5.1k", "0603WAF5101T5E")
        _connect(_pin_net(circuit, f"USB_CC{index}", usb, pin), rd, "1")
        _connect(nets["GND"], rd, "2")

    usb_fuse = two_pin(
        circuit, "F1", "500mA resettable", "Fuse:Fuse_1206_3216Metric",
        mpn="MF-MSMF050-2", unit_cost_eur=0.10,
    )
    _connect(nets["USB_VBUS_RAW"], usb_fuse, "1")
    _connect(nets["USB_VBUS"], usb_fuse, "2")
    usb_esd = component(
        circuit,
        "U9",
        "USBLC6-2SC6",
        "Package_TO_SOT_SMD:SOT-23-6",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(("D+", "GND", "D-", "D-", "VBUS", "D+"), start=1)),
        mpn="USBLC6-2SC6",
        description="Low-capacitance USB ESD protection",
        unit_cost_eur=0.15,
    )
    for pin in ("1", "6"):
        _connect(nets["USB_D+"], usb_esd, pin)
    for pin in ("3", "4"):
        _connect(nets["USB_D-"], usb_esd, pin)
    _connect(nets["GND"], usb_esd, "2")
    _connect(nets["USB_VBUS"], usb_esd, "5")
    shield_resistor = _rc(circuit, "R3", "1M", "0603WAF1004T5E")
    shield_capacitor = two_pin(
        circuit, "C12", "4.7n 1kV", "Capacitor_SMD:C_1206_3216Metric",
        mpn="CC1206KKX7RCBB472", unit_cost_eur=0.04,
    )
    shield = _pin_net(circuit, "USB_SHIELD", usb, "S1")
    for part in (shield_resistor, shield_capacitor):
        _connect(shield, part, "1")
        _connect(nets["GND"], part, "2")

    charger = _charger(circuit)
    for pin in ("1", "20"):
        _connect(nets["SYS"], charger, pin)
    for pin in ("3", "9", "10", "11", "21"):
        _connect(nets["GND"], charger, pin)
    for pin in ("14", "15", "16"):
        _connect(nets["BAT+"], charger, pin)
    for pin in ("18", "19"):
        _connect(nets["USB_VBUS"], charger, pin)
    _connect(nets["USB_500MA"], charger, "4")
    _connect(nets["3V3"], charger, "17")
    for pin, name in (("6", "CHG_PG_N"), ("7", "CHG_STAT2"), ("8", "CHG_STAT1_N")):
        _connect(nets[name], charger, pin)
    vpcc = _pin_net(circuit, "CHARGER_VPCC", charger, "2")
    vpcc_top = _rc(circuit, "R4", "330k 1%", "0603WAF3303T5E")
    vpcc_bottom = _rc(circuit, "R5", "110k 1%", "RC0603FR-07110KL")
    _connect(nets["USB_VBUS"], vpcc_top, "1")
    _connect(vpcc, vpcc_top, "2")
    _connect(vpcc, vpcc_bottom, "1")
    _connect(nets["GND"], vpcc_bottom, "2")
    for ref, pin, value, mpn in (
        ("R6", "12", "24.9k 1%", "0603WAF2492T5E"),
        ("R7", "13", "2.0k", "0603WAF2001T5E"),
    ):
        resistor = _rc(circuit, ref, value, mpn)
        _connect(_pin_net(circuit, f"CHARGER_PROG{pin}", charger, pin), resistor, "1")
        _connect(nets["GND"], resistor, "2")
    for ref, name in (("R8", "CHG_PG_N"), ("R9", "CHG_STAT2"), ("R10", "CHG_STAT1_N")):
        pullup = _rc(circuit, ref, "10k", "0603WAF1002T5E")
        _connect(nets["3V3"], pullup, "1")
        _connect(nets[name], pullup, "2")
    for ref, name, value, mpn in (
        ("C13", "USB_VBUS", "4.7u 10V", "CL21A475KAQNNNE"),
        ("C14", "SYS", "10u 10V", "CL21A106KAYNNNE"),
        ("C15", "BAT+", "4.7u 10V", "CL21A475KAQNNNE"),
    ):
        capacitor = two_pin(
            circuit, ref, value, "Capacitor_SMD:C_0805_2012Metric", mpn=mpn, unit_cost_eur=0.04
        )
        _connect(nets[name], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    battery = component(
        circuit,
        "J2",
        "B2B-PH-K-S(LF)(SN)",
        "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        (PinDefinition("1", "BAT+"), PinDefinition("2", "GND")),
        mpn="B2B-PH-K-S(LF)(SN)",
        description="Battery connector with Adafruit polarity",
        unit_cost_eur=0.15,
    )
    _connect(nets["BAT_RAW"], battery, "1")
    _connect(nets["GND"], battery, "2")
    battery_protection = component(
        circuit,
        "Q1",
        "DMP2035U-7",
        "Package_TO_SOT_SMD:SOT-23",
        (PinDefinition("1", "G"), PinDefinition("2", "S"), PinDefinition("3", "D")),
        mpn="DMP2035U-7",
        description="Battery reverse-polarity protection",
        unit_cost_eur=0.20,
    )
    _connect(nets["GND"], battery_protection, "1")
    _connect(nets["BAT+"], battery_protection, "2")
    _connect(nets["BAT_RAW"], battery_protection, "3")
    therm = component(
        circuit,
        "J3",
        "B2B-PH-K-S(LF)(SN)",
        "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        (PinDefinition("1", "THERM"), PinDefinition("2", "GND")),
        mpn="B2B-PH-K-S(LF)(SN)",
        description="External cell thermistor connector",
        unit_cost_eur=0.15,
    )
    therm_net = _pin_net(circuit, "THERM", charger, "5")
    _connect(therm_net, therm, "1")
    _connect(nets["GND"], therm, "2")

    power_switch = component(
        circuit,
        "SW1",
        "POWER",
        "Button_Switch_SMD:SW_SPDT_CK_JS102011SAQN",
        (PinDefinition("1", "POWER_EN"), PinDefinition("2", "SYS"), PinDefinition("3", "OFF")),
        mpn="JS102011SAQN",
        description="Battery operation enable switch",
        unit_cost_eur=0.25,
    )
    _connect(nets["POWER_EN"], power_switch, "1")
    _connect(nets["SYS"], power_switch, "2")
    _no_connect(circuit, power_switch, ("3",))
    power_enable_pull = _rc(circuit, "R11", "1M", "0603WAF1004T5E")
    _connect(nets["POWER_EN"], power_enable_pull, "1")
    _connect(nets["GND"], power_enable_pull, "2")
    usb_override = component(
        circuit,
        "D1",
        "BAT54H",
        "Diode_SMD:D_SOD-323",
        (PinDefinition("1", "K"), PinDefinition("2", "A")),
        mpn="BAT54H",
        description="USB power-on override",
        unit_cost_eur=0.05,
    )
    _connect(nets["POWER_EN"], usb_override, "1")
    _connect(nets["USB_VBUS"], usb_override, "2")

    regulator = tps63802(circuit, "U2")
    for pin in ("2", "3", "8"):
        _connect(nets["GND"], regulator, pin)
    _connect(nets["SYS"], regulator, "10")
    _connect(nets["POWER_EN"], regulator, "1")
    _connect(nets["3V3"], regulator, "6")
    buck_pg = _pin_net(circuit, "BUCK_PG_N", regulator, "5")
    buck_pg_pullup = _rc(circuit, "R12", "100k", "0603WAF1003T5E")
    _connect(nets["3V3"], buck_pg_pullup, "1")
    _connect(buck_pg, buck_pg_pullup, "2")
    inductor = two_pin(
        circuit, "L1", "0.47uH", "Inductor_SMD:L_Murata_DFE201610P",
        mpn="DFE201610E-R47M=P2", unit_cost_eur=0.10,
    )
    _connect(_pin_net(circuit, "BUCK_L1", regulator, "9"), inductor, "1")
    _connect(_pin_net(circuit, "BUCK_L2", regulator, "7"), inductor, "2")
    fb_top = _rc(circuit, "R13", "511k", "RC0603FR-07511KL")
    fb_bottom = _rc(circuit, "R14", "91k", "0603WAF9102T5E")
    buck_fb = _pin_net(circuit, "BUCK_FB", regulator, "4")
    _connect(nets["3V3"], fb_top, "1")
    _connect(buck_fb, fb_top, "2")
    _connect(buck_fb, fb_bottom, "1")
    _connect(nets["GND"], fb_bottom, "2")
    for ref, net, value in (("C1", "SYS", "22u"), ("C2", "3V3", "22u"), ("C3", "3V3", "22u")):
        capacitor = two_pin(
            circuit, ref, value, "Capacitor_SMD:C_0805_2012Metric",
            mpn="CL21A226MAQNNNE", unit_cost_eur=0.05,
        )
        _connect(nets[net], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")


def _build_led_rail(circuit: Circuit, nets: dict[str, Net]) -> Net:
    led_boost = _led_boost(circuit)
    _connect(nets["3V3"], led_boost, "1")
    _connect(nets["LED_EN"], led_boost, "2")
    _connect(nets["GND"], led_boost, "4")
    _connect(nets["LED_5V_RAW"], led_boost, "5")
    led_boost_sw = _pin_net(circuit, "LED_BOOST_SW", led_boost, "6")
    led_inductor = two_pin(
        circuit, "L2", "1uH", "Inductor_SMD:L_Wuerth_MAPI-3015",
        mpn="74438357010", unit_cost_eur=0.15,
    )
    _connect(nets["3V3"], led_inductor, "1")
    _connect(led_boost_sw, led_inductor, "2")
    led_fb = _pin_net(circuit, "LED_BOOST_FB", led_boost, "3")
    led_fb_top = _rc(circuit, "R15", "732k", "RC0603FR-07732KL")
    led_fb_bottom = _rc(circuit, "R16", "100k", "0603WAF1003T5E")
    _connect(nets["LED_5V_RAW"], led_fb_top, "1")
    _connect(led_fb, led_fb_top, "2")
    _connect(led_fb, led_fb_bottom, "1")
    _connect(nets["GND"], led_fb_bottom, "2")
    for ref, name, value in (
        ("C7", "3V3", "10u 10V"),
        ("C8", "LED_5V_RAW", "22u 10V"),
        ("C9", "LED_5V_RAW", "22u 10V"),
    ):
        mpn = "CL21A106KAYNNNE" if ref == "C7" else "CL21A226MAQNNNE"
        capacitor = two_pin(
            circuit, ref, value, "Capacitor_SMD:C_0805_2012Metric",
            mpn=mpn, unit_cost_eur=0.05,
        )
        _connect(nets[name], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    led_limiter = _led_limiter(circuit)
    _connect(nets["LED_5V_RAW"], led_limiter, "1")
    _connect(nets["GND"], led_limiter, "2")
    _connect(nets["LED_EN"], led_limiter, "3")
    led_fault = nets["LED_FAULT_N"]
    _connect(led_fault, led_limiter, "4")
    _connect(nets["LED_5V"], led_limiter, "6")
    led_limit_resistor = _rc(circuit, "R17", "82k 1%", "0603WAF8202T5E")
    _connect(_pin_net(circuit, "LED_ILIM", led_limiter, "5"), led_limit_resistor, "1")
    _connect(nets["GND"], led_limit_resistor, "2")
    led_fault_pullup = _rc(circuit, "R18", "100k", "0603WAF1003T5E")
    _connect(nets["3V3"], led_fault_pullup, "1")
    _connect(led_fault, led_fault_pullup, "2")
    for ref, name in (("C10", "LED_5V_RAW"), ("C11", "LED_5V")):
        capacitor = _rc(circuit, ref, "100n", "CL05B104KO5NNNC")
        _connect(nets[name], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    led_buffer = component(
        circuit,
        "U8",
        "SN74AHCT1G125DBVR",
        "Package_TO_SOT_SMD:SOT-23-5",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(("OE_N", "A", "GND", "Y", "VCC"), start=1)),
        mpn="SN74AHCT1G125DBVR",
        description="3.3 V to 5 V LED data buffer",
        unit_cost_eur=0.10,
    )
    _connect(nets["GND"], led_buffer, "1")
    _connect(nets["LED_DATA"], led_buffer, "2")
    _connect(nets["GND"], led_buffer, "3")
    led_data_5v = _pin_net(circuit, "LED_DATA_5V", led_buffer, "4")
    _connect(nets["LED_5V"], led_buffer, "5")
    led_data_pulldown = _rc(circuit, "R19", "100k", "0603WAF1003T5E")
    _connect(nets["LED_DATA"], led_data_pulldown, "1")
    _connect(nets["GND"], led_data_pulldown, "2")
    return led_data_5v


def _build_mcu(circuit: Circuit, nets: dict[str, Net]) -> None:
    mcu = esp32_c3_mini_1u(circuit, "U4")
    _connect(nets["3V3"], mcu, "3")
    for pin in ("1", "2", "11", "14", *tuple(str(number) for number in range(36, 54))):
        _connect(nets["GND"], mcu, pin)
    # IO2 (pin 5) is a boot strapping pin that must read high at reset, so it
    # carries the pulled-up chip select rather than the pulled-down LED data
    # line, which lives on IO0 (pin 12). Same reviewed map as the previous hub,
    # with the freed I2C-expander lines picking up the new slow signals.
    mcu_connections = {
        "5": "OLED2_CS_N", "6": "NFC_BUSY", "12": "LED_DATA", "13": "NFC_IRQ",
        "16": "OLED1_CS_N", "18": "SCLK", "19": "MOSI", "20": "MISO", "21": "NFC_CS_N",
        "22": "I2C_SCL", "23": "I2C_SDA", "26": "USB_D-", "27": "USB_D+",
        "30": "UART_RX", "31": "UART_TX",
    }
    for pin, name in mcu_connections.items():
        _connect(nets[name], mcu, pin)
    _no_connect(circuit, mcu, ("4", "7", "9", "10", "15", "17", "24", "25", "28", "29", "32", "33", "34", "35"))
    en_pull = _rc(circuit, "R20", "10k", "0603WAF1002T5E")
    mcu_en = _pin_net(circuit, "MCU_EN", mcu, "8")
    _connect(nets["3V3"], en_pull, "1")
    _connect(mcu_en, en_pull, "2")
    en_cap = two_pin(
        circuit, "C6", "1u", "Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10A105KB8NNNC", unit_cost_eur=0.01,
    )
    _connect(mcu_en, en_cap, "1")
    _connect(nets["GND"], en_cap, "2")
    for ref, name in (("R21", "I2C_SCL"), ("R22", "I2C_SDA")):
        pullup = _rc(circuit, ref, "4.7k", "0603WAF4701T5E")
        _connect(nets["3V3"], pullup, "1")
        _connect(nets[name], pullup, "2")
    # Holds the strapping pin high at reset and the OLED deselected until
    # firmware drives it.
    strap_pullup = _rc(circuit, "R23", "10k", "0603WAF1002T5E")
    _connect(nets["3V3"], strap_pullup, "1")
    _connect(nets["OLED2_CS_N"], strap_pullup, "2")

    expander = _io_expander(circuit)
    _no_connect(circuit, expander, ("1", "18", "19", "20"))
    for pin in ("2", "3", "12", "21"):
        _connect(nets["GND"], expander, pin)
    _connect(nets["3V3"], expander, "24")
    _connect(nets["I2C_SCL"], expander, "22")
    _connect(nets["I2C_SDA"], expander, "23")
    expander_signals = {
        "4": "SEL_RCLK", "5": "NFC_RESET_N", "6": "OLED_DC", "7": "OLED_RESET_N",
        "8": "LED_EN", "9": "USB_500MA", "10": "BUTTON_N", "11": "LED_FAULT_N",
        "13": "CHG_PG_N", "14": "CHG_STAT2", "15": "CHG_STAT1_N", "16": "SEL_SRCLR_N",
        "17": "NFC_GPO1",
    }
    for pin, name in expander_signals.items():
        _connect(nets[name], expander, pin)
    led_en_pulldown = _rc(circuit, "R24", "100k", "0603WAF1003T5E")
    _connect(nets["LED_EN"], led_en_pulldown, "1")
    _connect(nets["GND"], led_en_pulldown, "2")
    button_pullup = _rc(circuit, "R25", "10k", "0603WAF1002T5E")
    _connect(nets["3V3"], button_pullup, "1")
    _connect(nets["BUTTON_N"], button_pullup, "2")
    # The matrix registers hold random selection until the MCU clears them;
    # keep the latch output defined while the expander initializes.
    rclk_pulldown = _rc(circuit, "R26", "100k", "0603WAF1003T5E")
    _connect(nets["SEL_RCLK"], rclk_pulldown, "1")
    _connect(nets["GND"], rclk_pulldown, "2")


def _build_reader(circuit: Circuit, nets: dict[str, Net]) -> None:
    reader = _pn5180(circuit)
    _no_connect(circuit, reader, ("2", "11", "14", "20", "23", "24", "31", "32", "33", "34", "35", "40"))
    for pin in ("4", "9", "19", "27"):
        _connect(nets["GND"], reader, pin)
    for pin in ("6", "12", "13", "26"):
        _connect(nets["3V3"], reader, pin)
    _connect(nets["3V3"], reader, "22")
    reader_signals = {
        "1": "NFC_CS_N", "3": "MOSI", "5": "MISO", "7": "SCLK",
        "8": "NFC_BUSY", "10": "NFC_RESET_N", "38": "NFC_GPO1", "39": "NFC_IRQ",
    }
    for pin, name in reader_signals.items():
        _connect(nets[name], reader, pin)

    # VDD is the internal 1.8 V LDO output, tied to AVDD and DVDD per datasheet.
    core = Net("NFC_VDD", circuit=circuit)
    for pin in ("28", "29", "30"):
        _connect(core, reader, pin)
    core_cap = _rc(circuit, "C20", "1u 10V", "CL05A105KA5NQNC")
    _connect(core, core_cap, "1")
    _connect(nets["GND"], core_cap, "2")
    vmid = _pin_net(circuit, "NFC_VMID", reader, "17")
    vdhf = _pin_net(circuit, "NFC_VDHF", reader, "25")
    for ref, net in (("C21", vmid), ("C22", vdhf)):
        stabilizer = _rc(circuit, ref, "100n", "CL05B104KO5NNNC")
        _connect(net, stabilizer, "1")
        _connect(nets["GND"], stabilizer, "2")
    supply_caps = (
        ("C23", "3V3", "100n", "CL05B104KO5NNNC"),
        ("C24", "3V3", "1u 10V", "CL05A105KA5NQNC"),
        ("C26", "3V3", "100n", "CL05B104KO5NNNC"),
    )
    for ref, name, value, mpn in supply_caps:
        capacitor = _rc(circuit, ref, value, mpn)
        _connect(nets[name], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")
    reader_bulk = two_pin(
        circuit,
        "C25",
        "2.2u 16V",
        "Capacitor_SMD:C_0603_1608Metric",
        mpn="CL10A225KO8NNNC",
        unit_cost_eur=0.02,
    )
    _connect(nets["3V3"], reader_bulk, "1")
    _connect(nets["GND"], reader_bulk, "2")

    crystal = component(
        circuit,
        "Y1",
        "27.12MHz EXS00A-CS01188",
        "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(("XTI", "GND", "XTO", "GND"), start=1)),
        mpn="EXS00A-CS01188",
        description="PN5180 27.12 MHz reference crystal",
        unit_cost_eur=0.35,
    )
    clk1 = _pin_net(circuit, "NFC_CLK1", reader, "36")
    clk2 = _pin_net(circuit, "NFC_CLK2", reader, "37")
    xti = Net("NFC_XTI", circuit=circuit)
    xto = Net("NFC_XTO", circuit=circuit)
    for ref, clk_net, crystal_net in (("R27", clk1, xti), ("R28", clk2, xto)):
        series = _rc(circuit, ref, "100R", "0603WAF1000T5E")
        _connect(clk_net, series, "1")
        _connect(crystal_net, series, "2")
    _connect(xti, crystal, "1")
    _connect(xto, crystal, "3")
    for pin in ("2", "4"):
        _connect(nets["GND"], crystal, pin)
    for ref, crystal_net in (("C31", xti), ("C32", xto)):
        load_capacitor = _rc(circuit, ref, "10p C0G", "CL05C100JB5NNNC")
        _connect(crystal_net, load_capacitor, "1")
        _connect(nets["GND"], load_capacitor, "2")

    # Single-ended drive: TX1 through the EMC low-pass and a series match onto
    # the shared matrix bus; TX2 gets the mirrored EMC filter into ground so
    # the push-pull driver sees a balanced load. The matrix line's own tuning
    # makes the tank; the series match centers the loaded system, with a DNP
    # trim beside it. RX taps the bus resistively against the VMID mid-rail.
    tx_filtered = Net("NFC_TX_FILTERED", circuit=circuit)
    emc_inductor = two_pin(
        circuit, "L3", "470nH", "Inductor_SMD:L_0805_2012Metric",
        mpn="LQW2BASR47J00L", unit_cost_eur=0.15,
    )
    _connect(_pin_net(circuit, "NFC_TX1", reader, "21"), emc_inductor, "1")
    _connect(tx_filtered, emc_inductor, "2")
    emc_shunt = _rc(circuit, "C33", "220p C0G 2%", "GRM1555C1H221JA01D")
    _connect(tx_filtered, emc_shunt, "1")
    _connect(nets["GND"], emc_shunt, "2")
    # 68 pF couples the driver without re-tuning the bus: the ngspice front-end
    # bench peaks the selected loop's field at 13.86 MHz, in band, where 220 pF
    # would drag the system to 9 MHz.
    match_series = _rc(circuit, "C34", "68p C0G 2%", "GRM1555C1H680JA01D")
    match_trim = two_pin(
        circuit, "C35", "DNP C0G", "Capacitor_SMD:C_0402_1005Metric",
        mpn="", unit_cost_eur=0.0, fitted=False,
    )
    for capacitor in (match_series, match_trim):
        _connect(tx_filtered, capacitor, "1")
        _connect(nets["RF_BUS"], capacitor, "2")
    tx2_inductor = two_pin(
        circuit, "L4", "470nH", "Inductor_SMD:L_0805_2012Metric",
        mpn="LQW2BASR47J00L", unit_cost_eur=0.15,
    )
    tx2_balance = Net("NFC_TX2_BALANCE", circuit=circuit)
    _connect(_pin_net(circuit, "NFC_TX2", reader, "18"), tx2_inductor, "1")
    _connect(tx2_balance, tx2_inductor, "2")
    tx2_shunt = _rc(circuit, "C36", "220p C0G 2%", "GRM1555C1H221JA01D")
    _connect(tx2_balance, tx2_shunt, "1")
    _connect(nets["GND"], tx2_shunt, "2")

    rxp = _pin_net(circuit, "NFC_RXP", reader, "16")
    rxn = _pin_net(circuit, "NFC_RXN", reader, "15")
    rx_series_r = _rc(circuit, "R29", "1k", "0603WAF1001T5E")
    rx_series_c = _rc(circuit, "C37", "100p C0G", "0402CG101J500NT")
    rx_node = Net("NFC_RX_TAP", circuit=circuit)
    _connect(nets["RF_BUS"], rx_series_c, "1")
    _connect(rx_node, rx_series_c, "2")
    _connect(rx_node, rx_series_r, "1")
    _connect(rxp, rx_series_r, "2")
    rx_bias = _rc(circuit, "R30", "1k", "0603WAF1001T5E")
    _connect(rxn, rx_bias, "1")
    _connect(_pin_net(circuit, "NFC_VMID_TAP", reader, "17"), rx_bias, "2")


def build_hub() -> Circuit:
    circuit = Circuit(name="hub")
    net_names = (
        "GND", "USB_VBUS_RAW", "USB_VBUS", "USB_D+", "USB_D-", "BAT_RAW", "BAT+", "SYS",
        "POWER_EN", "3V3", "LED_5V_RAW", "LED_5V", "LED_FAULT_N",
        "SCLK", "MOSI", "MISO", "NFC_CS_N", "NFC_IRQ", "NFC_BUSY", "NFC_RESET_N", "NFC_GPO1",
        "I2C_SCL", "I2C_SDA", "OLED1_CS_N", "OLED2_CS_N", "OLED_DC", "OLED_RESET_N",
        "LED_DATA", "LED_RETURN", "SEL_RCLK", "SEL_SRCLR_N", "RF_BUS", "BUTTON_N",
        "UART_RX", "UART_TX", "CHG_PG_N", "CHG_STAT2", "CHG_STAT1_N", "USB_500MA", "LED_EN",
    )
    nets = {name: Net(name, circuit=circuit) for name in net_names}
    for index, name in enumerate(("GND", "3V3", "LED_5V"), start=1):
        flag = Part("power", "PWR_FLAG", tool="kicad9", circuit=circuit, ref=f"#FLG0{index}", tag=f"{name}_FLAG")
        flag.footprint = "TestPoint:TestPoint_Pad_D1.0mm"
        flag.fitted = "DNP"
        _connect(nets[name], flag, "1")

    _build_power(circuit, nets)
    led_data_5v = _build_led_rail(circuit, nets)
    _build_mcu(circuit, nets)
    _build_reader(circuit, nets)

    # Matrix link, mirroring the matrix board's J1. The registers share the
    # SPI wires; SEL_RCLK latches from the expander after a 16-bit shift.
    matrix = _connector(
        circuit, "J4",
        ("GND", "RF_BUS", "GND", "3V3", "SEL_SER", "SEL_SRCLK", "SEL_RCLK"),
        "SM07B-GHS-TB(LF)(SN)", 0.35,
    )
    for pin, net in (
        ("1", nets["GND"]), ("2", nets["RF_BUS"]), ("3", nets["GND"]), ("4", nets["3V3"]),
        ("5", nets["MOSI"]), ("6", nets["SCLK"]), ("7", nets["SEL_RCLK"]),
    ):
        _connect(net, matrix, pin)

    display_names = ("3V3", "GND", "SCLK", "MOSI", "CS_N", "DC", "RESET_N")
    for display in range(2):
        connector = _connector(
            circuit,
            f"J{display + 5}",
            display_names,
            "SM07B-GHS-TB(LF)(SN)",
            0.35,
        )
        display_nets = (
            nets["3V3"], nets["GND"], nets["SCLK"], nets["MOSI"],
            nets[f"OLED{display + 1}_CS_N"], nets["OLED_DC"], nets["OLED_RESET_N"],
        )
        for connector_pin, net in enumerate(display_nets, start=1):
            _connect(net, connector, str(connector_pin))

    for bar in range(2):
        connector = _connector(circuit, f"J{bar + 7}", ("LED_5V", "GND", "DATA_IN", "DATA_OUT"), "A1257WR-S-4P", 0.14)
        _connect(nets["LED_5V"], connector, "1")
        _connect(nets["GND"], connector, "2")
        if bar == 0:
            _connect(led_data_5v, connector, "3")
            _connect(nets["LED_RETURN"], connector, "4")
        else:
            _connect(nets["LED_RETURN"], connector, "3")
            # The second bar ends the chain; its data output stays open.
            _no_connect(circuit, connector, ("4",))

    uart = _connector(circuit, "J9", ("3V3", "GND", "UART_TX", "UART_RX"), "A1257WR-S-4P", 0.14)
    for connector_pin, name in enumerate(("3V3", "GND", "UART_TX", "UART_RX"), start=1):
        _connect(nets[name], uart, str(connector_pin))

    button = _connector(circuit, "J10", ("BUTTON_N", "GND"), "SM02B-GHS-TB(LF)(SN)", 0.20)
    _connect(nets["BUTTON_N"], button, "1")
    _connect(nets["GND"], button, "2")

    # SRCLR_N of the matrix registers is tied high on the matrix board; the
    # expander line reserved for it stays local spare until a respin frees it.
    srclr_pull = _rc(circuit, "R31", "10k", "0603WAF1002T5E")
    _connect(nets["3V3"], srclr_pull, "1")
    _connect(nets["SEL_SRCLR_N"], srclr_pull, "2")
    return circuit
