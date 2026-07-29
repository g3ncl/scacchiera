"""Power board: cell, charger, power path and 5 V boost, on a snap-off panel.

This board implements the contract in docs/hardware/power-module-interface.md
rather than defining its own boundary, so the hub does not change and a
purchased module could still replace it. Qualified 5 V arrives from the hub's
temperature-gated output, the cell hangs off this board, and regulated 5 V goes
back. The hub keeps the cell-temperature interlock and measures cell voltage on
its own ADC, so nothing here has to be trusted for safety or telemetry.

MCP73871 is back. It was rejected from the first design for charging at 500 mA,
which made a recharge take as long as a session; the relaxed 240-minute limit
lets it run at its full 1 A and clears that limit with 30 minutes to spare. Its
power path is what buys uninterrupted output: the system runs from the input
while the cell charges independently, and switches to the cell without a gap.

The boost is what the light bars and the hub's buck actually see. Between a
3.0 V depleted cell and a 4.2 V full one the system rail has to stay at 5 V, so
the converter runs from the charger's system terminal rather than from the cell
directly, and therefore keeps regulating while an adapter is connected.
"""

from skidl import Circuit, Net, Part
from skidl.pin import pin_types

from hardware.pcb.parts import PinDefinition, component, mounting_hole, two_pin


# Deliberately open, each traced to the part's data sheet.
NO_CONNECTS: dict[str, tuple[str, ...]] = {
    "U1": ("6", "7", "8"),
    "J2": ("5", "6"),
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


def _rc(circuit: Circuit, ref: str, value: str, mpn: str, cost: float = 0.002) -> Part:
    footprint = (
        "Resistor_SMD:R_0603_1608Metric"
        if ref.startswith("R")
        else "Capacitor_SMD:C_0805_2012Metric"
    )
    return two_pin(circuit, ref, value, footprint, mpn=mpn, unit_cost_eur=cost)


def _connector(circuit: Circuit, ref: str, names: tuple[str, ...], mpn: str, cost: float) -> Part:
    return component(
        circuit,
        ref,
        mpn,
        f"Connector_JST:JST_GH_SM{len(names):02d}B-GHS-TB_1x{len(names):02d}-1MP_P1.25mm_Horizontal",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn=mpn,
        description="Keyed power harness connector",
        unit_cost_eur=cost,
    )


def _charger(circuit: Circuit) -> Part:
    names = (
        "OUT", "VPCC", "SEL", "PROG2", "THERM", "PG", "STAT2", "STAT1", "TE", "VSS",
        "VSS11", "PROG3", "PROG1", "VBAT", "VBAT15", "VBAT_SENSE", "CE", "IN", "IN19",
        "OUT20", "EP",
    )
    return component(
        circuit,
        "U1",
        "MCP73871T-2CCI/ML",
        "Package_DFN_QFN:QFN-20-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="MCP73871T-2CCI/ML",
        description="1 A single-cell charger with power-path management",
        unit_cost_eur=1.20,
    )


def _boost(circuit: Circuit) -> Part:
    names = ("FB", "EN", "VIN", "GND", "SW", "VOUT")
    return component(
        circuit,
        "U2",
        "TPS61023DRLR",
        "Chessboard:SOT-563_DRL",
        tuple(PinDefinition(str(index), name) for index, name in enumerate(names, start=1)),
        mpn="TPS61023DRLR",
        description="Boost converter, system rail to 5 V",
        unit_cost_eur=0.60,
    )


def build_power() -> Circuit:
    circuit = Circuit(name="power")
    nets = {
        name: Net(name, circuit=circuit)
        for name in ("GND", "CHARGE_5V", "SYS", "BAT_RAW", "MODULE_5V", "BOOST_SW", "BOOST_FB")
    }
    ground_flag = Part(
        "power", "PWR_FLAG", tool="kicad9", circuit=circuit, ref="#FLG01", tag="GND_FLAG"
    )
    ground_flag.footprint = "TestPoint:TestPoint_Pad_D1.0mm"
    ground_flag.fitted = "DNP"
    _connect(nets["GND"], ground_flag, "1")

    # Qualified 5 V in, on the same seven-way shape the hub sends it: three
    # supply contacts because this harness carries charge and system current
    # together, and every contact in the family is rated 1.0 A.
    inlet_pins = ("CHARGE_5V", "CHARGE_5V", "CHARGE_5V", "GND", "GND", "GND", "GND")
    inlet = _connector(circuit, "J1", inlet_pins, "SM07B-GHS-TB(LF)(SN)", 0.35)
    for contact, name in enumerate(inlet_pins, start=1):
        _connect(nets[name], inlet, str(contact))

    # Regulated 5 V back, and the cell terminal the hub divides into its ADC.
    # Pins 5 and 6 are the contract's optional I2C, which this board does not
    # implement, so they are deliberately open at this end.
    outlet_pins = (
        "MODULE_5V", "MODULE_5V", "GND", "GND", "I2C_SCL", "I2C_SDA", "BAT_RAW",
    )
    outlet = _connector(circuit, "J2", outlet_pins, "SM07B-GHS-TB(LF)(SN)", 0.35)
    for contact, name in enumerate(outlet_pins, start=1):
        if name.startswith("I2C"):
            continue
        _connect(nets[name], outlet, str(contact))
    _no_connect(circuit, outlet, NO_CONNECTS["J2"])

    cell = component(
        circuit,
        "J3",
        "B2B-PH-K-S(LF)(SN)",
        "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        (PinDefinition("1", "BAT_RAW"), PinDefinition("2", "GND")),
        mpn="B2B-PH-K-S(LF)(SN)",
        description="Cell connector, protected pouch with its own PCM",
        unit_cost_eur=0.15,
    )
    _connect(nets["BAT_RAW"], cell, "1")
    _connect(nets["GND"], cell, "2")

    charger = _charger(circuit)
    for pin in ("18", "19"):
        _connect(nets["CHARGE_5V"], charger, pin)
    for pin in ("1", "20"):
        _connect(nets["SYS"], charger, pin)
    for pin in ("14", "15", "16"):
        _connect(nets["BAT_RAW"], charger, pin)
    for pin in ("10", "11", "21"):
        _connect(nets["GND"], charger, pin)
    # SEL high selects adapter mode, where PROG1 sets the fast-charge current
    # rather than the 100 or 500 mA a USB port would allow. The input is a
    # qualified 5 V 2 A adapter, already gated for cell temperature by the hub.
    _connect(nets["CHARGE_5V"], charger, "3")
    _connect(nets["CHARGE_5V"], charger, "17")
    # PROG2 only acts in USB mode, and the data sheet forbids floating inputs.
    _connect(nets["GND"], charger, "4")
    # TE is active low and enables the safety timer, which is worth having.
    _connect(nets["GND"], charger, "9")
    _no_connect(circuit, charger, NO_CONNECTS["U1"])

    # IREG is 1000 mA divided by PROG1 in kohm, so 1.0 k is the part's full 1 A
    # and the smallest resistance its 1 k to 20 k range allows.
    prog1 = _rc(circuit, "R1", "1k 1%", "0603WAF1001T5E")
    _connect(_pin_net(circuit, "PROG1", charger, "13"), prog1, "1")
    _connect(nets["GND"], prog1, "2")
    # Termination is the same relation on PROG3: 10 k terminates at 100 mA,
    # a fiftieth of the cell, comfortably inside its 5 k to 100 k range.
    prog3 = _rc(circuit, "R2", "10k 1%", "0603WAF1002T5E")
    _connect(_pin_net(circuit, "PROG3", charger, "12"), prog3, "1")
    _connect(nets["GND"], prog3, "2")
    # The charger's own thermistor input is neutralised: its 50 uA source across
    # 10 k sits at 0.5 V, inside the 0.25 to 1.24 V window it suspends outside.
    # Cell temperature is the hub's job, on a bead the hub's own analog window
    # watches, and one bead cannot bias two monitors without them interacting.
    therm = _rc(circuit, "R3", "10k 1%", "0603WAF1002T5E")
    _connect(_pin_net(circuit, "THERM", charger, "5"), therm, "1")
    _connect(nets["GND"], therm, "2")

    # VPCC reduces charge current when the input droops, which is how the board
    # keeps from loading a source past its rating. 100 k over 39 k puts the
    # 1.23 V threshold at a 4.38 V input, below anything a compliant adapter
    # should sag to and well above the charger's own dropout.
    vpcc = _pin_net(circuit, "VPCC", charger, "2")
    top = _rc(circuit, "R4", "100k 1%", "0603WAF1003T5E")
    bottom = _rc(circuit, "R5", "39k 1%", "0603WAF3902T5E")
    _connect(nets["CHARGE_5V"], top, "1")
    _connect(vpcc, top, "2")
    _connect(vpcc, bottom, "1")
    _connect(nets["GND"], bottom, "2")

    for ref, net_name, value, mpn in (
        ("C1", "CHARGE_5V", "10u 25V", "CL21A106KAYNNNE"),
        ("C2", "SYS", "10u 25V", "CL21A106KAYNNNE"),
        ("C3", "BAT_RAW", "10u 25V", "CL21A106KAYNNNE"),
        ("C4", "MODULE_5V", "22u 25V", "CL21A226MAQNNNE"),
    ):
        capacitor = _rc(circuit, ref, value, mpn, cost=0.05)
        _connect(nets[net_name], capacitor, "1")
        _connect(nets["GND"], capacitor, "2")

    boost = _boost(circuit)
    _connect(nets["SYS"], boost, "3")
    # Enabled whenever the system rail exists. Nothing switches this board off:
    # the hub sleeps, it does not power down, and a converter that stopped below
    # some load would take the board with it.
    _connect(nets["SYS"], boost, "2")
    _connect(nets["GND"], boost, "4")
    _connect(nets["BOOST_SW"], boost, "5")
    _connect(nets["MODULE_5V"], boost, "6")
    _connect(nets["BOOST_FB"], boost, "1")
    # Murata's exact 1 uH part is stocked under C435392. Its 20 percent
    # tolerance stays inside the boost's 0.37 to 2.9 uH effective range. The
    # 4.7 A saturation and 3.3 A temperature-rise limits must be checked again
    # when the inadequate boost converter is replaced.
    inductor = two_pin(
        circuit, "L1", "1uH", "Chessboard:DFE252012F",
        mpn="DFE252012F-1R0M=P2", unit_cost_eur=0.07,
    )
    _connect(nets["SYS"], inductor, "1")
    _connect(nets["BOOST_SW"], inductor, "2")
    # 0.6 V reference over 330 k and 44.1 k gives 5.09 V, inside the hub's
    # 4.5 to 5.5 V acceptance and under the converter's own 5.5 V minimum
    # over-voltage threshold. The lower leg is two resistors because the exact
    # ratio needs a value this design does not already carry, and a series pair
    # of bound parts beats a new part number whose order code the catalogue
    # reports two ways.
    feedback_top = _rc(circuit, "R6", "330k 1%", "0603WAF3303T5E")
    feedback_upper = _rc(circuit, "R7", "39k 1%", "0603WAF3902T5E")
    feedback_lower = _rc(circuit, "R8", "5.1k 1%", "0603WAF5101T5E")
    feedback_mid = Net("BOOST_FB_MID", circuit=circuit)
    _connect(nets["MODULE_5V"], feedback_top, "1")
    _connect(nets["BOOST_FB"], feedback_top, "2")
    _connect(nets["BOOST_FB"], feedback_upper, "1")
    _connect(feedback_mid, feedback_upper, "2")
    _connect(feedback_mid, feedback_lower, "1")
    _connect(nets["GND"], feedback_lower, "2")

    return circuit
