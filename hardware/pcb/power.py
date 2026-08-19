"""Power board: 1S NVDC charger and regulated 5 V, 2 A output."""

from skidl import Circuit, Net, Part
from skidl.pin import pin_types

from hardware.pcb.parts import PinDefinition, component, mounting_hole, two_pin


NO_CONNECTS: dict[str, tuple[str, ...]] = {
    "U1": ("2", "3", "4", "7", "12"),
    "U2": ("13",),
    "J2": ("8",),
}


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def _pin_net(circuit: Circuit, name: str, part: Part, pin: str) -> Net:
    net = Net(name, circuit=circuit)
    net += part[pin]
    return net


def _no_connect(circuit: Circuit, part: Part, pins: tuple[str, ...]) -> None:
    for pin in pins:
        part[pin].func = pin_types.NOCONNECT
        circuit.NC += part[pin]


def _passive(
    circuit: Circuit,
    ref: str,
    value: str,
    mpn: str,
    *,
    footprint: str | None = None,
    cost: float = 0.01,
) -> Part:
    if footprint is not None:
        selected = footprint
    elif ref.startswith("R"):
        selected = "Resistor_SMD:R_0603_1608Metric"
    elif mpn.startswith(("0402", "CL05")):
        selected = "Capacitor_SMD:C_0402_1005Metric"
    elif mpn.startswith("CL10"):
        selected = "Capacitor_SMD:C_0603_1608Metric"
    elif mpn.startswith("CL21"):
        selected = "Capacitor_SMD:C_0805_2012Metric"
    else:
        raise ValueError(f"no exact footprint rule for {mpn}")
    return two_pin(circuit, ref, value, selected, mpn=mpn, unit_cost_eur=cost)


def _gh7(circuit: Circuit, ref: str) -> Part:
    names = ("CHARGE_5V", "CHARGE_5V", "CHARGE_5V", "GND", "GND", "GND", "GND")
    return component(
        circuit,
        ref,
        "SM07B-GHS-TB(LF)(SN)",
        "Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="SM07B-GHS-TB(LF)(SN)",
        description="Qualified 5 V input harness",
        unit_cost_eur=0.35,
    )


def _microfit(circuit: Circuit, ref: str, names: tuple[str, ...], mpn: str, code: str) -> Part:
    footprint = (
        f"Connector_Molex:Molex_Micro-Fit_3.0_43045-{code}_2x"
        f"{len(names) // 2:02d}_P3.00mm_Horizontal"
    )
    return component(
        circuit,
        ref,
        mpn,
        footprint,
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn=mpn,
        description="8.5 A per-contact locking power connector",
        unit_cost_eur=0.66 if len(names) == 8 else 0.40,
    )


def _charger(circuit: Circuit) -> Part:
    names = (
        "VBUS", "D+", "D-", "STAT", "SCL", "SDA", "INT", "OTG", "CE", "ILIM",
        "TS", "QON", "BAT", "BAT", "SYS", "SYS", "PGND", "PGND", "SW", "SW",
        "BTST", "REGN", "PMID", "DSEL", "EP_GND",
    )
    return component(
        circuit,
        "U1",
        "BQ25895RTWR",
        "Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="BQ25895RTWR",
        description="5 A switch-mode 1S charger with 6 A continuous NVDC battery path",
        unit_cost_eur=1.20,
    )


def _boost(circuit: Circuit) -> Part:
    names = (
        "VCC", "EN", "FSW", "SW", "SW", "SW", "SW", "BOOT", "VIN", "SS", "NC",
        "NC", "MODE", "VOUT", "VOUT", "VOUT", "FB", "COMP", "ILIM", "AGND", "PGND",
    )
    return component(
        circuit,
        "U2",
        "TPS61088RHLR",
        "Package_DFN_QFN:Texas_VQFN-RHL-20",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="TPS61088RHLR",
        description="Synchronous boost converter, regulated 5 V at 2 A",
        unit_cost_eur=1.03,
    )


def build_power() -> Circuit:
    circuit = Circuit(name="power")
    names = (
        "GND", "CHARGE_5V", "PMID", "CHARGER_SW", "SYS", "BAT_RAW", "REGN",
        "MODULE_5V", "BOOST_SW", "BOOST_FB", "BOOST_COMP", "BOOST_EN", "CELL_POS",
        "I2C_SCL", "I2C_SDA", "CHARGER_DSEL", "CHARGER_ILIM_MID",
        "BAT_REVERSE_GATE", "BAT_REVERSE_REF", "BAT_REVERSE_SENSE",
    )
    nets = {name: Net(name, circuit=circuit) for name in names}
    flag = Part("power", "PWR_FLAG", tool="kicad9", circuit=circuit, ref="#FLG01", tag="GND_FLAG")
    flag.footprint = "TestPoint:TestPoint_Pad_D1.0mm"
    flag.fitted = "DNP"
    _connect(nets["GND"], flag, "1")

    inlet = _gh7(circuit, "J1")
    for pin in range(1, 4):
        _connect(nets["CHARGE_5V"], inlet, str(pin))
    for pin in range(4, 8):
        _connect(nets["GND"], inlet, str(pin))

    outlet_names = (
        "MODULE_5V", "MODULE_5V", "GND", "GND", "I2C_SCL", "I2C_SDA", "BAT_RAW", "NC",
    )
    outlet = _microfit(circuit, "J2", outlet_names, "430450800", "0800")
    for pin_index, name in enumerate(outlet_names[:-1], start=1):
        _connect(nets[name], outlet, str(pin_index))
    _no_connect(circuit, outlet, NO_CONNECTS["J2"])

    cell = _microfit(circuit, "J3", ("CELL_POS", "GND"), "430450200", "0200")
    _connect(nets["CELL_POS"], cell, "1")
    _connect(nets["GND"], cell, "2")

    reverse_fet = component(
        circuit, "Q1", "CSD25404Q3", "Chessboard:CSD25404Q3_DQG",
        (
            PinDefinition("1", "D"), PinDefinition("2", "D"), PinDefinition("3", "D"),
            PinDefinition("4", "G"), PinDefinition("5", "S"), PinDefinition("6", "S"),
            PinDefinition("7", "S"), PinDefinition("8", "S"),
        ),
        mpn="CSD25404Q3", description="20 V P-channel reverse-cell pass MOSFET",
        unit_cost_eur=0.48,
    )
    for fet_pin in ("1", "2", "3"):
        _connect(nets["CELL_POS"], reverse_fet, fet_pin)
    _connect(nets["BAT_REVERSE_GATE"], reverse_fet, "4")
    for fet_pin in ("5", "6", "7", "8"):
        _connect(nets["BAT_RAW"], reverse_fet, fet_pin)

    reverse_comparator = component(
        circuit, "U4", "TLV7021DCKR", "Package_TO_SOT_SMD:SOT-353_SC-70-5",
        (
            PinDefinition("1", "OUT"), PinDefinition("2", "GND"),
            PinDefinition("3", "IN+"), PinDefinition("4", "IN-"),
            PinDefinition("5", "VCC"),
        ),
        mpn="TLV7021DCKR", description="Open-drain reverse-cell comparator",
        unit_cost_eur=0.20,
    )
    _connect(nets["BAT_REVERSE_GATE"], reverse_comparator, "1")
    _connect(nets["GND"], reverse_comparator, "2")
    _connect(nets["BAT_REVERSE_REF"], reverse_comparator, "3")
    _connect(nets["BAT_REVERSE_SENSE"], reverse_comparator, "4")
    _connect(nets["BAT_RAW"], reverse_comparator, "5")

    for ref, value, mpn, first, second in (
        ("R15", "100k 1%", "0603WAF1003T5E", nets["BAT_RAW"], nets["BAT_REVERSE_GATE"]),
        ("R16", "1M 1%", "0603WAF1004T5E", nets["BAT_RAW"], nets["BAT_REVERSE_REF"]),
        ("R17", "100k 1%", "0603WAF1003T5E", nets["BAT_REVERSE_REF"], nets["GND"]),
        ("R18", "1M 1%", "0603WAF1004T5E", nets["CELL_POS"], nets["BAT_REVERSE_SENSE"]),
        ("R19", "1M 1%", "0603WAF1004T5E", nets["BAT_REVERSE_SENSE"], nets["GND"]),
    ):
        resistor = _passive(circuit, ref, value, mpn)
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")
    reverse_clamp = component(
        circuit, "D1", "BAT54H", "Diode_SMD:D_SOD-323",
        (PinDefinition("1", "K"), PinDefinition("2", "A")),
        mpn="BAT54H", description="Schottky clamp for reversed-cell sense input",
        unit_cost_eur=0.02,
    )
    _connect(nets["BAT_REVERSE_SENSE"], reverse_clamp, "1")
    _connect(nets["GND"], reverse_clamp, "2")
    reverse_bypass = _passive(circuit, "C21", "100n 16V", "CL05B104KO5NNNC")
    _connect(nets["BAT_RAW"], reverse_bypass, "1")
    _connect(nets["GND"], reverse_bypass, "2")

    charger = _charger(circuit)
    _connect(nets["CHARGE_5V"], charger, "1")
    _connect(nets["I2C_SCL"], charger, "5")
    _connect(nets["I2C_SDA"], charger, "6")
    _connect(nets["GND"], charger, "8")
    _connect(nets["GND"], charger, "9")
    for charger_pin in ("13", "14"):
        _connect(nets["BAT_RAW"], charger, charger_pin)
    for charger_pin in ("15", "16"):
        _connect(nets["SYS"], charger, charger_pin)
    for charger_pin in ("17", "18", "25"):
        _connect(nets["GND"], charger, charger_pin)
    for charger_pin in ("19", "20"):
        _connect(nets["CHARGER_SW"], charger, charger_pin)
    _connect(nets["REGN"], charger, "22")
    _connect(nets["PMID"], charger, "23")
    _connect(nets["CHARGER_DSEL"], charger, "24")
    _no_connect(circuit, charger, NO_CONNECTS["U1"])

    # D+/D- are deliberately absent at this module boundary, so the charger
    # starts at its 500 mA unknown-source default. Firmware may raise IINLIM
    # only after the hub has qualified the Type-C source. The independent ILIM
    # ceiling remains below 2 A even at the data-sheet KILIM maximum.
    for ref, first, second in (
        ("R12", _pin_net(circuit, "CHARGER_ILIM", charger, "10"), nets["CHARGER_ILIM_MID"]),
        ("R13", nets["CHARGER_ILIM_MID"], nets["GND"]),
    ):
        resistor = _passive(circuit, ref, "100R 1%", "0603WAF1000T5E")
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")
    dsel_pullup = _passive(circuit, "R14", "10k 1%", "0603WAF1002T5E")
    _connect(nets["REGN"], dsel_pullup, "1")
    _connect(nets["CHARGER_DSEL"], dsel_pullup, "2")

    ts = _pin_net(circuit, "CHARGER_TS", charger, "11")
    for ref, first, second in (("R1", nets["REGN"], ts), ("R2", ts, nets["GND"])):
        resistor = _passive(circuit, ref, "10k 1%", "0603WAF1002T5E")
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")

    charge_inductor = two_pin(
        circuit, "L1", "1uH", "Chessboard:DFE252012F",
        mpn="DFE252012F-1R0M=P2", unit_cost_eur=0.07,
    )
    _connect(nets["CHARGER_SW"], charge_inductor, "1")
    _connect(nets["SYS"], charge_inductor, "2")

    # The two 100 nF series pairs implement the data sheet's 47 nF bootstrap value.
    for prefix, high, low in (("C1", _pin_net(circuit, "CHARGER_BTST", charger, "21"), nets["CHARGER_SW"]),):
        middle = Net(f"{prefix}_MID", circuit=circuit)
        for ref, first, second in ((prefix, high, middle), ("C2", middle, low)):
            capacitor = _passive(circuit, ref, "100n 16V", "CL05B104KO5NNNC")
            _connect(first, capacitor, "1")
            _connect(second, capacitor, "2")

    capacitor_specs = (
        ("C3", "CHARGE_5V", "1u 25V", "CL10A105KB8NNNC"),
        ("C4", "PMID", "4.7u 25V", "CL21A475KAQNNNE"),
        ("C5", "PMID", "4.7u 25V", "CL21A475KAQNNNE"),
        ("C14", "PMID", "4.7u 25V", "CL21A475KAQNNNE"),
        ("C6", "REGN", "4.7u 25V", "CL21A475KAQNNNE"),
        ("C7", "SYS", "22u 25V", "CL21A226MAQNNNE"),
        ("C8", "BAT_RAW", "10u 25V", "CL21A106KAYNNNE"),
    )
    for ref, net, value, mpn in capacitor_specs:
        capacitor = _passive(circuit, ref, value, mpn, cost=0.05)
        _connect(nets[net], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    supervisor = component(
        circuit, "U3", "TLV809K33DBVR", "Package_TO_SOT_SMD:SOT-23",
        (PinDefinition("1", "GND"), PinDefinition("2", "RESET_N"), PinDefinition("3", "VDD")),
        mpn="TLV809K33DBVR", description="2.93 V cell-path undervoltage supervisor",
        unit_cost_eur=0.18,
    )
    _connect(nets["GND"], supervisor, "1")
    _connect(nets["BOOST_EN"], supervisor, "2")
    _connect(nets["SYS"], supervisor, "3")
    supervisor_bypass = _passive(circuit, "C20", "100n 16V", "CL05B104KO5NNNC")
    _connect(nets["SYS"], supervisor_bypass, "1")
    _connect(nets["GND"], supervisor_bypass, "2")

    boost = _boost(circuit)
    _connect(nets["BOOST_EN"], boost, "2")
    for boost_pin in ("4", "5", "6", "7"):
        _connect(nets["BOOST_SW"], boost, boost_pin)
    _connect(nets["SYS"], boost, "9")
    for boost_pin in ("11", "12", "20", "21"):
        _connect(nets["GND"], boost, boost_pin)
    for boost_pin in ("14", "15", "16"):
        _connect(nets["MODULE_5V"], boost, boost_pin)
    _connect(nets["BOOST_FB"], boost, "17")
    _connect(nets["BOOST_COMP"], boost, "18")
    _no_connect(circuit, boost, NO_CONNECTS["U2"])

    boost_inductor = two_pin(
        circuit, "L2", "1.2uH", "Chessboard:CDMC8D28",
        mpn="CDMC8D28NP-1R2MC", unit_cost_eur=2.12,
    )
    _connect(nets["SYS"], boost_inductor, "1")
    _connect(nets["BOOST_SW"], boost_inductor, "2")

    for ref, boost_pin, destination in (("C9", "1", nets["GND"]),):
        capacitor = _passive(circuit, ref, "2.2u 16V", "CL10A225KO8NNNC")
        _connect(_pin_net(circuit, "BOOST_VCC", boost, boost_pin), capacitor, "1")
        _connect(destination, capacitor, "2")
    boot = _passive(circuit, "C10", "100n 16V", "CL05B104KO5NNNC")
    _connect(_pin_net(circuit, "BOOST_BOOT", boost, "8"), boot, "1")
    _connect(nets["BOOST_SW"], boot, "2")

    ss_mid = Net("BOOST_SS_MID", circuit=circuit)
    for ref, first, second in (("C11", _pin_net(circuit, "BOOST_SS", boost, "10"), ss_mid), ("C12", ss_mid, nets["GND"])):
        capacitor = _passive(circuit, ref, "100n 16V", "CL05B104KO5NNNC")
        _connect(first, capacitor, "1")
        _connect(second, capacitor, "2")

    fsw_mid1 = Net("BOOST_FSW_MID1", circuit=circuit)
    fsw_mid2 = Net("BOOST_FSW_MID2", circuit=circuit)
    fsw_pin = _pin_net(circuit, "BOOST_FSW", boost, "3")
    for ref, first, second, value, mpn in (
        ("R3", nets["BOOST_SW"], fsw_mid1, "100k 1%", "0603WAF1003T5E"),
        ("R4", fsw_mid1, fsw_mid2, "91k 1%", "0603WAF9102T5E"),
    ):
        resistor = _passive(circuit, ref, value, mpn)
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")
    fsw_last = _passive(circuit, "R5", "91k 1%", "0603WAF9102T5E")
    _connect(fsw_mid2, fsw_last, "1")
    _connect(fsw_pin, fsw_last, "2")

    ilim_mid = Net("BOOST_ILIM_MID", circuit=circuit)
    for ref, first, second, value, mpn in (
        ("R6", _pin_net(circuit, "BOOST_ILIM", boost, "19"), ilim_mid, "100k 1%", "0603WAF1003T5E"),
        ("R7", ilim_mid, nets["GND"], "51k 1%", "0603WAF5101T5E"),
    ):
        resistor = _passive(circuit, ref, value, mpn)
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")

    fb_mid = Net("BOOST_FB_TOP_MID", circuit=circuit)
    for ref, value, mpn, first, second in (
        ("R8", "100k 1%", "0603WAF1003T5E", nets["MODULE_5V"], fb_mid),
        ("R9", "24.9k 1%", "0603WAF2492T5E", fb_mid, nets["BOOST_FB"]),
        ("R10", "39k 1%", "0603WAF3902T5E", nets["BOOST_FB"], nets["GND"]),
    ):
        resistor = _passive(circuit, ref, value, mpn)
        _connect(first, resistor, "1")
        _connect(second, resistor, "2")

    comp_mid = Net("BOOST_COMP_MID", circuit=circuit)
    comp_resistor = _passive(circuit, "R11", "5.1k 1%", "0603WAF5101T5E")
    _connect(nets["BOOST_COMP"], comp_resistor, "1")
    _connect(comp_mid, comp_resistor, "2")
    comp_capacitor = _passive(
        circuit, "C13", "22n 50V", "0402B223K500NT", cost=0.02,
    )
    _connect(comp_mid, comp_capacitor, "1")
    _connect(nets["GND"], comp_capacitor, "2")

    for ref, net, value, mpn in (
        ("C15", "SYS", "22u 25V", "CL21A226MAQNNNE"),
        ("C16", "SYS", "100n 16V", "CL05B104KO5NNNC"),
        ("C17", "MODULE_5V", "1u 25V", "CL10A105KB8NNNC"),
        ("C18", "MODULE_5V", "22u 25V", "CL21A226MAQNNNE"),
        ("C19", "MODULE_5V", "22u 25V", "CL21A226MAQNNNE"),
        ("C22", "MODULE_5V", "22u 25V", "CL21A226MAQNNNE"),
    ):
        capacitor = _passive(circuit, ref, value, mpn, cost=0.05)
        _connect(nets[net], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    mounting_hole(circuit, "H1", nets["GND"])
    mounting_hole(circuit, "H2", nets["GND"])
    return circuit
