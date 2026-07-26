"""Hub board: protected power input, WiFi MCU, ISO 15693 reader, and interfaces.

The product USB-C input passes through an independent cell-temperature gate to
the PiSugar 3 Plus. That purchased subsystem owns the lithium cell, charging,
protection, UPS transfer, and battery telemetry. Its managed 5 V output returns
to this board, where one fixed-output buck makes 3V3 and a TPS2553 protects the
light bars.

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
    esp32_c6_mini_1u,
    mounting_hole,
    two_pin,
    usb_c_receptacle,
)


NO_CONNECTS: dict[str, tuple[str, ...]] = {
    "J1": ("A6", "A7", "A8", "B6", "B7", "B8"),
    "J8": ("4",),
    "U3": ("2", "11", "14", "20", "23", "24", "31", "32", "33", "34", "35", "40"),
    "U4": ("4", "7", "9", "10", "15", "16", "17", "18", "19", "20", "21", "32", "33", "34", "35"),
    "U6": ("1", "13", "14", "15", "18", "19", "20"),
}


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


def _charge_input_switch(circuit: Circuit) -> Part:
    return component(
        circuit,
        "U1",
        "AP22811AW5-7",
        "Package_TO_SOT_SMD:SOT-23-5",
        tuple(
            PinDefinition(str(index), name)
            for index, name in enumerate(("OUT", "GND", "FLG_N", "EN", "IN"), start=1)
        ),
        mpn="AP22811AW5-7",
        description="Temperature-gated, current-limited PiSugar input switch",
        unit_cost_eur=0.20,
    )


def _temperature_comparator(circuit: Circuit) -> Part:
    return component(
        circuit,
        "U2",
        "TLV7042DGKR",
        "Chessboard:TLV7042_DGK",
        tuple(
            PinDefinition(str(index), name)
            for index, name in enumerate(
                ("OUTA", "INA-", "INA+", "GND", "INB+", "INB-", "OUTB", "VCC"),
                start=1,
            )
        ),
        mpn="TLV7042DGKR",
        description="Fail-safe cold and hot cell-temperature window",
        unit_cost_eur=0.35,
    )


def _buck(circuit: Circuit) -> Part:
    return component(
        circuit,
        "U5",
        "AP63203WU-7",
        "Package_TO_SOT_SMD:SOT-23-6",
        tuple(
            PinDefinition(str(index), name)
            for index, name in enumerate(("FB", "EN", "VIN", "GND", "SW", "BST"), start=1)
        ),
        mpn="AP63203WU-7",
        description="Fixed 3.3 V, 2 A synchronous buck converter",
        unit_cost_eur=0.35,
    )


def _pn5180(circuit: Circuit) -> Part:
    names = (
        "NSS", "AUX2", "MOSI", "PVSS", "MISO", "PVDD", "SCK", "BUSY", "VSS", "RESET_N",
        "NC11", "VBAT", "VBAT", "NC14", "RXN", "RXP", "VMID", "TX2", "TVSS", "NC20",
        "TX1", "TVDD", "ANT1", "ANT2", "VDHF", "VBAT", "VSS", "AVDD", "VDD", "DVDD",
        "NC31", "NC32", "NC33", "NC34", "NC35", "CLK1", "CLK2", "GPO1", "IRQ", "AUX1", "EP_GND",
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
        _connect(nets["USB_VBUS"], usb, pin)
    _no_connect(circuit, usb, NO_CONNECTS["J1"])
    for index, pin in (("1", "A5"), ("2", "B5")):
        rd = _rc(circuit, f"R{index}", "5.1k", "0603WAF5101T5E")
        _connect(_pin_net(circuit, f"USB_CC{index}", usb, pin), rd, "1")
        _connect(nets["GND"], rd, "2")

    shield_resistor = _rc(circuit, "R3", "1M", "0603WAF1004T5E")
    shield_capacitor = two_pin(
        circuit, "C12", "4.7n 1kV", "Capacitor_SMD:C_1206_3216Metric",
        mpn="CC1206KKX7RCBB472", unit_cost_eur=0.04,
    )
    shield = _pin_net(circuit, "USB_SHIELD", usb, "SH")
    for part in (shield_resistor, shield_capacitor):
        _connect(shield, part, "1")
        _connect(nets["GND"], part, "2")

    # The NTC divider rises when the sensor is cold. Comparator A asserts low
    # above the 8 C reference; comparator B asserts low below the 35 C reference.
    # Their wired open-drain output is therefore high only inside the window.
    comparator = _temperature_comparator(circuit)
    _connect(nets["THERM_SENSE"], comparator, "2")
    _connect(nets["THERM_COLD_REF"], comparator, "3")
    _connect(nets["GND"], comparator, "4")
    _connect(nets["THERM_SENSE"], comparator, "5")
    _connect(nets["THERM_HOT_REF"], comparator, "6")
    for pin in ("1", "7"):
        _connect(nets["CHARGE_TEMP_OK"], comparator, pin)
    _connect(nets["USB_VBUS"], comparator, "8")

    therm_pullup = _rc(circuit, "R4", "10k", "0603WAF1002T5E")
    _connect(nets["USB_VBUS"], therm_pullup, "1")
    _connect(nets["THERM_SENSE"], therm_pullup, "2")
    cold_top = _rc(circuit, "R5", "39k 1%", "0603WAF3902T5E")
    cold_bottom = _rc(circuit, "R6", "100k 1%", "0603WAF1003T5E")
    _connect(nets["USB_VBUS"], cold_top, "1")
    _connect(nets["THERM_COLD_REF"], cold_top, "2")
    _connect(nets["THERM_COLD_REF"], cold_bottom, "1")
    _connect(nets["GND"], cold_bottom, "2")

    hot_nodes = [Net(f"THERM_HOT_TOP_{index}", circuit=circuit) for index in (1, 2)]
    hot_top_nets = (nets["USB_VBUS"], *hot_nodes, nets["THERM_HOT_REF"])
    for hot_index in range(3):
        resistor = _rc(circuit, f"R{hot_index + 7}", "100k 1%", "0603WAF1003T5E")
        _connect(hot_top_nets[hot_index], resistor, "1")
        _connect(hot_top_nets[hot_index + 1], resistor, "2")
    hot_mid = Net("THERM_HOT_BOTTOM_MID", circuit=circuit)
    for ref, first, second in (
        ("R10", nets["THERM_HOT_REF"], hot_mid),
        ("R11", hot_mid, nets["GND"]),
    ):
        resistor = _rc(circuit, ref, "100k 1%", "0603WAF1003T5E")
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")

    gate_pullup = _rc(circuit, "R12", "100k", "0603WAF1003T5E")
    _connect(nets["USB_VBUS"], gate_pullup, "1")
    _connect(nets["CHARGE_TEMP_OK"], gate_pullup, "2")
    switch = _charge_input_switch(circuit)
    _connect(nets["CHARGE_5V"], switch, "1")
    _connect(nets["GND"], switch, "2")
    _connect(nets["CHARGE_INPUT_FAULT_N"], switch, "3")
    _connect(nets["CHARGE_TEMP_OK"], switch, "4")
    _connect(nets["USB_VBUS"], switch, "5")

    for ref, name, value, footprint, mpn in (
        ("C13", "USB_VBUS", "1u 10V", "Capacitor_SMD:C_0603_1608Metric", "CL10A105KB8NNNC"),
        ("C14", "CHARGE_5V", "10u 10V", "Capacitor_SMD:C_0805_2012Metric", "CL21A106KAYNNNE"),
        ("C15", "CHARGE_5V", "100n", "Capacitor_SMD:C_0402_1005Metric", "CL05B104KO5NNNC"),
        ("C16", "USB_VBUS", "100n", "Capacitor_SMD:C_0402_1005Metric", "CL05B104KO5NNNC"),
    ):
        capacitor = two_pin(circuit, ref, value, footprint, mpn=mpn, unit_cost_eur=0.04)
        _connect(nets[name], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    adc_top = _rc(circuit, "R13", "1M", "0603WAF1004T5E")
    adc_bottom = _rc(circuit, "R14", "1M", "0603WAF1004T5E")
    _connect(nets["THERM_SENSE"], adc_top, "1")
    _connect(nets["TEMP_SENSE_ADC"], adc_top, "2")
    _connect(nets["TEMP_SENSE_ADC"], adc_bottom, "1")
    _connect(nets["GND"], adc_bottom, "2")
    adc_cap = _rc(circuit, "C17", "100n", "CL05B104KO5NNNC")
    _connect(nets["TEMP_SENSE_ADC"], adc_cap, "1")
    _connect(nets["GND"], adc_cap, "2")
    fault_pullup = _rc(circuit, "R15", "100k", "0603WAF1003T5E")
    _connect(nets["3V3"], fault_pullup, "1")
    _connect(nets["CHARGE_INPUT_FAULT_N"], fault_pullup, "2")

    regulator = _buck(circuit)
    _connect(nets["3V3"], regulator, "1")
    _connect(nets["PISUGAR_5V"], regulator, "2")
    _connect(nets["PISUGAR_5V"], regulator, "3")
    _connect(nets["GND"], regulator, "4")
    buck_sw = _pin_net(circuit, "BUCK_SW", regulator, "5")
    buck_bst = _pin_net(circuit, "BUCK_BST", regulator, "6")
    inductor = two_pin(
        circuit, "L1", "4.7uH", "Chessboard:NR6045S",
        mpn="NR6045S4R7MT", unit_cost_eur=0.06,
    )
    _connect(buck_sw, inductor, "1")
    _connect(nets["3V3"], inductor, "2")
    bootstrap = _rc(circuit, "C1", "100n", "CL05B104KO5NNNC")
    _connect(buck_bst, bootstrap, "1")
    _connect(buck_sw, bootstrap, "2")
    for ref, net, value, mpn in (
        ("C2", "PISUGAR_5V", "10u 10V", "CL21A106KAYNNNE"),
        ("C3", "3V3", "22u 10V", "CL21A226MAQNNNE"),
        ("C4", "3V3", "22u 10V", "CL21A226MAQNNNE"),
    ):
        capacitor = two_pin(
            circuit, ref, value, "Capacitor_SMD:C_0805_2012Metric", mpn=mpn, unit_cost_eur=0.05,
        )
        _connect(nets[net], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")


def _build_led_rail(circuit: Circuit, nets: dict[str, Net]) -> Net:
    led_limiter = _led_limiter(circuit)
    _connect(nets["PISUGAR_5V"], led_limiter, "1")
    _connect(nets["GND"], led_limiter, "2")
    _connect(nets["LED_EN"], led_limiter, "3")
    led_fault = nets["LED_FAULT_N"]
    _connect(led_fault, led_limiter, "4")
    _connect(nets["LED_5V"], led_limiter, "6")
    # 39k, not 82k. TPS2553 datasheet section 9.5.1 gives the trip current as
    #   IOSmin = 25230 / R^1.016, IOSnom = 23950 / R^0.977, IOSmax = 22980 / R^0.94
    # with R in kohm, valid from 15k to 232k. 82k trips at 287/323/365 mA, below
    # the 448 mA the two light bars draw (14 pixels x 16 mA x 2 bars), so the
    # rail would have latched off on any bright cue. 39k gives 609/667/734 mA,
    # 1.36x the load at the minimum trip. The worst-case 734 mA fault current
    # is contained on PiSugar's managed 5 V output, away from the 3V3 rail.
    led_limit_resistor = _rc(circuit, "R17", "39k 1%", "0603WAF3902T5E")
    _connect(_pin_net(circuit, "LED_ILIM", led_limiter, "5"), led_limit_resistor, "1")
    _connect(nets["GND"], led_limit_resistor, "2")
    led_fault_pullup = _rc(circuit, "R18", "100k", "0603WAF1003T5E")
    _connect(nets["3V3"], led_fault_pullup, "1")
    _connect(led_fault, led_fault_pullup, "2")
    for ref, name in (("C10", "PISUGAR_5V"), ("C11", "LED_5V")):
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
    mcu = esp32_c6_mini_1u(circuit, "U4")
    _connect(nets["3V3"], mcu, "3")
    for pin in ("1", "2", "11", "14", *tuple(str(number) for number in range(36, 54))):
        _connect(nets["GND"], mcu, pin)
    # Datasheet v1.5 Table 3-1 pin numbers, not the C3 map: native USB is
    # IO12/IO13 on pins 17/18, so reusing the C3 map would put SCLK on USB_D+
    # and the reader's chip select on a no-connect.
    #
    # SPI and both chip selects sit on pins 24 to 29, the module's bottom-right
    # and right edges, because the reader is placed to the right of the module.
    # The FSPI-native pins (IO2, IO6, IO7) are all on the left and bottom-left,
    # so aligning to them put MISO the long way round the module and the router
    # could not close it. At a display's and a reader's few MHz the GPIO matrix
    # costs nothing, so proximity wins.
    #
    # I2C keeps pins 22/23 because IO8 and IO9 are the C6 boot strapping pins
    # and the 4.7k bus pullups are what hold them high for SPI boot (Table 4-3),
    # which also makes IO9 the download-mode recovery pin.
    mcu_connections = {
        "5": "TEMP_SENSE_ADC", "6": "NFC_BUSY", "12": "LED_DATA", "13": "NFC_IRQ",
        "22": "I2C_SCL", "23": "I2C_SDA",
        "24": "OLED2_CS_N", "25": "SCLK", "26": "MOSI", "27": "MISO",
        "28": "NFC_CS_N", "29": "OLED1_CS_N", "30": "UART_RX", "31": "UART_TX",
    }
    for pin, name in mcu_connections.items():
        _connect(nets[name], mcu, pin)
    # Pins 4, 7, 21 and 32 to 35 are datasheet NC. Native USB pins 17 and 18
    # stay open because J1 is power-only. IO15 (pin 20) stays unused because it
    # is the JTAG-source strapping pin. IO2 pin 5 is ADC1_CH2 per Table 3-1.
    _no_connect(circuit, mcu, NO_CONNECTS["U4"])
    # Espressif requires bulk plus high-frequency decoupling at the module's
    # 3V3 pin. The regulator's own output caps are centimetres away, and WiFi
    # TX bursts brown the module out without local charge.
    for ref, value, mpn, footprint in (
        ("C27", "10u 10V", "CL21A106KAYNNNE", "Capacitor_SMD:C_0805_2012Metric"),
        ("C28", "100n", "CL05B104KO5NNNC", "Capacitor_SMD:C_0402_1005Metric"),
    ):
        local_cap = two_pin(circuit, ref, value, footprint, mpn=mpn, unit_cost_eur=0.05)
        _connect(nets["3V3"], local_cap, "1")
        _connect(nets["GND"], local_cap, "2")
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
    # IO18 is not a C6 strapping pin, so this is no longer a boot requirement.
    # It stays because the OLED must read deselected until firmware drives it.
    strap_pullup = _rc(circuit, "R23", "10k", "0603WAF1002T5E")
    _connect(nets["3V3"], strap_pullup, "1")
    _connect(nets["OLED2_CS_N"], strap_pullup, "2")

    # Recovery pads. Flashing is normally USB-Serial-JTAG over USB-C, but the
    # only button sits behind the polled expander and cannot hold IO9 low at
    # reset. Shorting TP1 to TP3 and pulsing TP2 forces joint download boot
    # (datasheet Table 4-3) if firmware ever breaks the USB peripheral.
    for ref, net_name in (("TP1", "I2C_SDA"), ("TP2", "MCU_EN"), ("TP3", "GND")):
        pad = Part(
            "Connector_Generic", "Conn_01x01", tool="kicad9", circuit=circuit,
            ref=ref, tag=ref,
        )
        pad.value = "RECOVERY"
        pad.footprint = "TestPoint:TestPoint_Pad_D1.0mm"
        pad.fitted = "DNP"
        pad.jlc_library = "Unbound"
        pad.manf_num = ""
        pad.lcsc_part = ""
        pad.description = "Bare copper recovery pad, not a purchased part"
        pad.unit_cost_eur = 0.0
        _connect(mcu_en if net_name == "MCU_EN" else nets[net_name], pad, "1")

    expander = _io_expander(circuit)
    _no_connect(circuit, expander, NO_CONNECTS["U6"])
    for pin in ("2", "3", "12", "21"):
        _connect(nets["GND"], expander, pin)
    _connect(nets["3V3"], expander, "24")
    _connect(nets["I2C_SCL"], expander, "22")
    _connect(nets["I2C_SDA"], expander, "23")
    expander_signals = {
        "4": "SEL_RCLK", "5": "NFC_RESET_N", "6": "OLED_DC", "7": "OLED_RESET_N",
        "8": "LED_EN", "9": "CHARGE_INPUT_FAULT_N", "10": "BUTTON_N", "11": "LED_FAULT_N",
        "16": "SEL_SRCLR_N",
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
    _no_connect(circuit, reader, NO_CONNECTS["U3"])
    for pin in ("4", "9", "19", "27", "41"):
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

    # TXC 7M27100009 against PN5180 Table 142 (crystal requirements for
    # ISO/IEC14443 compliant operation): 10 pF load against the required 10 pF
    # typ, 60 ohm ESR against 100 ohm max, +/-10 ppm tolerance and +/-15 ppm
    # stability against +/-100 ppm, 100 uW typical drive against the 100 uW
    # ceiling. The 3225 package replaced a 2016 part that JLCPCB could not
    # stock, and its larger pads are also reworkable by hand.
    crystal = component(
        circuit,
        "Y1",
        "27.12MHz 7M27100009",
        "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(("XTI", "GND", "XTO", "GND"), start=1)),
        mpn="7M27100009",
        description="PN5180 27.12 MHz reference crystal",
        unit_cost_eur=0.17,
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
    # Two equal caps present CL = C/2 + Cstray to the crystal. The part wants
    # 10 pF, and with 2 to 4 pF of trace and CLK pin stray, 15 pF lands at
    # about 10.5 pF, roughly 10 ppm of pull. The previous 10 pF pair presented
    # only 8 pF, which pulled about 41 ppm and spent most of the PN5180's
    # +/-100 ppm budget before the crystal's own tolerance was counted.
    for ref, crystal_net in (("C31", xti), ("C32", xto)):
        load_capacitor = _rc(circuit, ref, "15p C0G", "0402CG150J500NT")
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
        "GND", "USB_VBUS", "CHARGE_5V", "PISUGAR_5V", "3V3", "LED_5V", "LED_FAULT_N",
        "THERM_SENSE", "THERM_COLD_REF", "THERM_HOT_REF", "CHARGE_TEMP_OK",
        "CHARGE_INPUT_FAULT_N", "TEMP_SENSE_ADC",
        "SCLK", "MOSI", "MISO", "NFC_CS_N", "NFC_IRQ", "NFC_BUSY", "NFC_RESET_N", "NFC_GPO1",
        "I2C_SCL", "I2C_SDA", "OLED1_CS_N", "OLED2_CS_N", "OLED_DC", "OLED_RESET_N",
        "LED_DATA", "LED_RETURN", "SEL_RCLK", "SEL_SRCLR_N", "RF_BUS", "BUTTON_N",
        "UART_RX", "UART_TX", "LED_EN",
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

    charge_output = _connector(circuit, "J2", ("CHARGE_5V", "GND"), "SM02B-GHS-TB(LF)(SN)", 0.20)
    _connect(nets["CHARGE_5V"], charge_output, "1")
    _connect(nets["GND"], charge_output, "2")
    pisugar_return = _connector(
        circuit, "J3", ("PISUGAR_5V", "GND", "I2C_SCL", "I2C_SDA"), "A1257WR-S-4P", 0.14,
    )
    for connector_pin, name in enumerate(("PISUGAR_5V", "GND", "I2C_SCL", "I2C_SDA"), start=1):
        _connect(nets[name], pisugar_return, str(connector_pin))

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
            _no_connect(circuit, connector, NO_CONNECTS["J8"])

    uart = _connector(circuit, "J9", ("3V3", "GND", "UART_TX", "UART_RX"), "A1257WR-S-4P", 0.14)
    for connector_pin, name in enumerate(("3V3", "GND", "UART_TX", "UART_RX"), start=1):
        _connect(nets[name], uart, str(connector_pin))

    button = _connector(circuit, "J10", ("BUTTON_N", "GND"), "SM02B-GHS-TB(LF)(SN)", 0.20)
    _connect(nets["BUTTON_N"], button, "1")
    _connect(nets["GND"], button, "2")

    thermistor = _connector(circuit, "J11", ("THERM_SENSE", "GND"), "SM02B-GHS-TB(LF)(SN)", 0.20)
    _connect(nets["THERM_SENSE"], thermistor, "1")
    _connect(nets["GND"], thermistor, "2")

    # SRCLR_N of the matrix registers is tied high on the matrix board; the
    # expander line reserved for it stays local spare until a respin frees it.
    srclr_pull = _rc(circuit, "R31", "10k", "0603WAF1002T5E")
    _connect(nets["3V3"], srclr_pull, "1")
    _connect(nets["SEL_SRCLR_N"], srclr_pull, "2")
    for index in range(1, 5):
        mounting_hole(circuit, f"H{index}", nets["GND"])
    return circuit
