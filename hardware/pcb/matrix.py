"""Sensing matrix board: 8 row plus 8 column line antennas on one shared RF bus.

The row-column architecture from the research wiki: a tag's square is the
intersection of the row line and column line that both read its UID, so 16
antennas cover 64 squares. Exactly one line couples to the bus at a time
through its switch cell; the hub's reader drives the bus and two 74HC595
registers hold the one-hot active-low selection.

Each cell is the single-ended half of the hybrid PIN switch validated on the
previous 64-antenna design (its differential twin needed two of everything
because the reader drove both antenna ends; a line loop returns to ground, so
one side suffices):

- a series BAP64-02 between bus and tank. Forward biased (about 10 mA) it is a
  3 ohm switch; reverse it is sub-pF, so 15 deselected cells leave the bus tank
  in band where an analog switch's parallel off-capacitance would collapse it.
- a shunt BSS123 grounding the tank when deselected, raising off/on suppression
  far past what series isolation alone gives. Gate on SEL_N directly: high
  (deselected) shunts, low (selected) releases. No static current.
- bias steering: a high-side BSS84 from the 3V3 rail through R_set and an
  isolation BAP64-02 into the bias choke. The forward current returns through
  the loop antenna's own ground end, so a single leg biases the cell, and the
  isolation diode's off state keeps the steering parts off the bus when
  deselected.

Reference designators stride per cell (D and Q by 2, C by 4, R by 3, L by 2)
so the sixteen cells compose without collisions; board-level parts sit above
the cell ranges.
"""

from skidl import Circuit, Net, Part

from hardware.pcb.matrix_geometry import LINE_COUNT
from hardware.pcb.parts import PinDefinition, component, diode, mosfet, two_pin


COIL_FOOTPRINT = "Chessboard:Antenna_Line"
R_SET = "180R 1%"
R_BLEED = "100k 1%"


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def matrix_cell(
    circuit: Circuit,
    index: int,
    rf_bus: Net,
    gnd: Net,
    v33: Net,
    sel_n: Net,
) -> None:
    bus = Net(f"LINE{index}_BUS", circuit=circuit)
    match = Net(f"LINE{index}_MATCH", circuit=circuit)
    coil = Net(f"LINE{index}_COIL", circuit=circuit)
    steer = Net(f"LINE{index}_STEER", circuit=circuit)
    mid = Net(f"LINE{index}_MID", circuit=circuit)
    inject = Net(f"LINE{index}_INJECT", circuit=circuit)

    # DC block: the shared bus carries no DC, the local bias node does.
    c_block = two_pin(
        circuit,
        f"C{index * 4 + 1}",
        "100n X7R 10%",
        "Capacitor_SMD:C_0402_1005Metric",
        mpn="CL05B104KO5NNNC",
        unit_cost_eur=0.003,
    )
    _connect(rf_bus, c_block, "1")
    _connect(bus, c_block, "2")

    d_series = diode(circuit, f"D{index * 2 + 1}", "BAP64-02", unit_cost_eur=0.10)
    _connect(bus, d_series, "A")
    _connect(match, d_series, "K")

    q_shunt = mosfet(circuit, f"Q{index * 2 + 1}", "BSS123", unit_cost_eur=0.03)
    _connect(sel_n, q_shunt, "G")
    _connect(match, q_shunt, "D")
    _connect(gnd, q_shunt, "S")

    # 220 pF against the 0.59 uH single-turn loop leaves the untrimmed
    # resonance at the top of the band; the DNP trims only add capacitance, so
    # the assembled-board measurement pulls it down onto 13.56 MHz.
    nominal = two_pin(
        circuit,
        f"C{index * 4 + 2}",
        "220p C0G 2%",
        "Capacitor_SMD:C_0603_1608Metric",
        mpn="GRM1885C1H221JA01D",
        unit_cost_eur=0.02,
    )
    fine = two_pin(
        circuit,
        f"C{index * 4 + 3}",
        "DNP 1p-33p C0G",
        "Capacitor_SMD:C_0603_1608Metric",
        mpn="",
        unit_cost_eur=0.0,
        fitted=False,
    )
    coarse = two_pin(
        circuit,
        f"C{index * 4 + 4}",
        "DNP 33p-100p C0G",
        "Capacitor_SMD:C_0603_1608Metric",
        mpn="",
        unit_cost_eur=0.0,
        fitted=False,
    )
    for capacitor in (nominal, fine, coarse):
        _connect(match, capacitor, "1")
        _connect(gnd, capacitor, "2")

    # The bare loop's Q is near 90; 1.5 ohm brings the loaded Q to about 20 so
    # the line reads its whole lane through tolerance and detuning.
    damping = two_pin(
        circuit,
        f"R{index * 3 + 1}",
        "1.5R 1%",
        "Resistor_SMD:R_0603_1608Metric",
        mpn="RC0603FR-071R5L",
        unit_cost_eur=0.002,
    )
    _connect(match, damping, "1")
    _connect(coil, damping, "2")

    antenna = two_pin(
        circuit,
        f"L{index * 2 + 2}",
        "PCB_LOOP_0.59uH",
        COIL_FOOTPRINT,
        mpn="PCB_COPPER",
        unit_cost_eur=0.0,
    )
    _connect(coil, antenna, "1")
    _connect(gnd, antenna, "2")

    # Bias steering: 3V3 -> Q_steer -> R_set -> D_iso -> choke -> bus node,
    # returning to ground through the loop itself.
    q_steer = mosfet(circuit, f"Q{index * 2 + 2}", "BSS84", unit_cost_eur=0.05)
    _connect(v33, q_steer, "S")
    _connect(sel_n, q_steer, "G")
    _connect(steer, q_steer, "D")

    r_set = two_pin(
        circuit,
        f"R{index * 3 + 2}",
        R_SET,
        "Resistor_SMD:R_0603_1608Metric",
        mpn="RC0603FR-07180RL",
        unit_cost_eur=0.002,
    )
    _connect(steer, r_set, "1")
    _connect(mid, r_set, "2")

    d_iso = diode(circuit, f"D{index * 2 + 2}", "BAP64-02", unit_cost_eur=0.10)
    _connect(mid, d_iso, "A")
    _connect(inject, d_iso, "K")

    l_choke = two_pin(
        circuit,
        f"L{index * 2 + 1}",
        "10uH",
        "Inductor_SMD:L_0805_2012Metric",
        mpn="LQM21FN100M70L",
        unit_cost_eur=0.03,
    )
    _connect(inject, l_choke, "1")
    _connect(bus, l_choke, "2")

    r_bleed = two_pin(
        circuit,
        f"R{index * 3 + 3}",
        R_BLEED,
        "Resistor_SMD:R_0603_1608Metric",
        mpn="RC0603FR-07100KL",
        unit_cost_eur=0.002,
    )
    _connect(inject, r_bleed, "1")
    _connect(gnd, r_bleed, "2")


def _shift_register(circuit: Circuit, ref: str) -> Part:
    names = (
        "QB", "QC", "QD", "QE", "QF", "QG", "QH", "GND",
        "QH_SERIAL", "SRCLR_N", "SRCLK", "RCLK", "OE_N", "SER", "QA", "VCC",
    )
    return component(
        circuit,
        ref,
        "SN74HC595PW",
        "Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
        tuple(PinDefinition(str(number), name) for number, name in enumerate(names, start=1)),
        mpn="SN74HC595PWR",
        description="8-bit shift register holding the one-hot line selection",
        unit_cost_eur=0.12,
    )


def build_matrix() -> Circuit:
    circuit = Circuit(name="matrix")
    rf_bus = Net("RF_BUS", circuit=circuit)
    gnd = Net("GND", circuit=circuit)
    v33 = Net("3V3", circuit=circuit)
    ser = Net("SEL_SER", circuit=circuit)
    srclk = Net("SEL_SRCLK", circuit=circuit)
    rclk = Net("SEL_RCLK", circuit=circuit)
    chain = Net("SEL_CHAIN", circuit=circuit)

    for net in (gnd, v33):
        flag = Part(
            "power",
            "PWR_FLAG",
            tool="kicad9",
            circuit=circuit,
            ref=f"#FLG0{1 if net is gnd else 2}",
            tag=f"{net.name}_FLAG",
        )
        flag.footprint = "TestPoint:TestPoint_Pad_D1.0mm"
        flag.fitted = "DNP"
        _connect(net, flag, "1")

    connector = component(
        circuit,
        "J1",
        "SM07B-GHS-TB",
        "Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal",
        (
            PinDefinition("1", "GND"),
            PinDefinition("2", "RF_BUS"),
            PinDefinition("3", "GND"),
            PinDefinition("4", "3V3"),
            PinDefinition("5", "SEL_SER"),
            PinDefinition("6", "SEL_SRCLK"),
            PinDefinition("7", "SEL_RCLK"),
        ),
        mpn="SM07B-GHS-TB",
        description="Hub link: RF bus between grounds, rail, and selection serial",
        unit_cost_eur=0.35,
    )
    _connect(gnd, connector, "1")
    _connect(rf_bus, connector, "2")
    _connect(gnd, connector, "3")
    _connect(v33, connector, "4")
    _connect(ser, connector, "5")
    _connect(srclk, connector, "6")
    _connect(rclk, connector, "7")

    sel_lines = [Net(f"SEL{index}_N", circuit=circuit) for index in range(LINE_COUNT)]
    for bank, register_ref in ((0, "U1"), (1, "U2")):
        register = _shift_register(circuit, register_ref)
        outputs = ("QA", "QB", "QC", "QD", "QE", "QF", "QG", "QH")
        for position, output in enumerate(outputs):
            _connect(sel_lines[bank * 8 + position], register, output)
        _connect(ser if bank == 0 else chain, register, "SER")
        if bank == 0:
            _connect(chain, register, "QH_SERIAL")
        _connect(srclk, register, "SRCLK")
        _connect(rclk, register, "RCLK")
        _connect(v33, register, "SRCLR_N")
        _connect(gnd, register, "OE_N")
        _connect(v33, register, "VCC")
        _connect(gnd, register, "GND")
        decouple = two_pin(
            circuit,
            f"C{LINE_COUNT * 4 + 1 + bank}",
            "100n X7R 10%",
            "Capacitor_SMD:C_0402_1005Metric",
            mpn="CL05B104KO5NNNC",
            unit_cost_eur=0.003,
        )
        _connect(v33, decouple, "1")
        _connect(gnd, decouple, "2")

    # Lines 0-7 are rows, 8-15 are columns; the layout gives the two banks
    # their orientation, the schematic only fixes the order.
    for index in range(LINE_COUNT):
        matrix_cell(circuit, index, rf_bus, gnd, v33, sel_lines[index])
    return circuit
