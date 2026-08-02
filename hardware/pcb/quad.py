"""Four line antennas, their switch cells, and one selection register.

Four of these boards are the whole sensing plane. The schematic is deliberately
not a new circuit: it instantiates the same `matrix_cell` the matrix board
validated four times, so the tank, the PIN switch and the bias steering are the
identical parts in the identical topology.

What the split changes is where the board boundary falls, and that was the whole
question. Each cell's resonant tank (loop, 220 pF, trim pads, series diode,
shunt FET) sits entirely on this board, and the connectors sit on the far side
of the 100 nF DC block. So a harness adds series impedance to the shared bus,
which is a bus problem the trim pads can absorb, and not connector inductance
inside sixteen resonators, which nothing could. That distinction is the reason
this partition is buildable where an antenna-board-plus-daughterboard split was
not.

The four boards chain: the hub drives the first link in, its QH' leaves on the
link out, and the next board takes that as its serial in. Both links carry the
same seven conductors, so one pinout serves both directions and the hub sees
exactly the interface the matrix board gave it.

The register is a 74HC595 with four of its eight outputs used. The waste is
deliberate and it is cheap (a Basic part at 0.20 EUR); the alternative is eight
lanes per board, which is 280 mm wide and back inside the size charges this
partition exists to escape. It does cost a firmware change: the selection chain
is four registers deep, so a scan shifts 32 bits with the one-hot bit landing in
the low nibble of each, where the matrix board shifts 16.
"""

from skidl import Circuit, Net, Part

from hardware.pcb.matrix import matrix_cell, shift_register
from hardware.pcb.parts import PinDefinition, component, two_pin
from hardware.pcb.quad_geometry import LANES_PER_BOARD


# QA through QD carry this board's four lanes; QE through QH are unused and the
# chain runs on through them to QH'. Pin numbers, because that is what KiCad's
# ERC exclusions are keyed on: QE to QH are pins 4 to 7 of the SOIC-16.
REGISTER_OUTPUTS = ("QA", "QB", "QC", "QD")
UNUSED_OUTPUT_PINS = ("4", "5", "6", "7")


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def _link(circuit: Circuit, ref: str, serial_net_name: str, description: str) -> Part:
    """One end of the hub-to-board-to-board chain.

    Pin 5 is the only conductor whose meaning differs between the two ends: it
    is serial data in on the link in and this board's QH' on the link out.
    Everything else passes straight through, so a board is electrically a tee on
    the bus and the rail.

    The same SM07B-GHS-TB the matrix board already binds, not a wider part with
    four selects in it. Keeping the selection serial is what keeps the hub
    interface unchanged and the whole partition at zero new component types.
    """
    return component(
        circuit,
        ref,
        "SM07B-GHS-TB",
        "Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal",
        (
            PinDefinition("1", "GND"),
            PinDefinition("2", "RF_BUS"),
            PinDefinition("3", "GND"),
            PinDefinition("4", "3V3"),
            PinDefinition("5", serial_net_name),
            PinDefinition("6", "SEL_SRCLK"),
            PinDefinition("7", "SEL_RCLK"),
        ),
        mpn="SM07B-GHS-TB(LF)(SN)",
        description=description,
        unit_cost_eur=0.296,
    )


def build_quad() -> Circuit:
    circuit = Circuit(name="quad")
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

    link_in = _link(
        circuit, "J1", "SEL_SER", "Link in: from the hub, or from the previous board"
    )
    link_out = _link(
        circuit, "J2", "SEL_CHAIN", "Link out: bus, rail and this board's QH'"
    )
    for connector, serial in ((link_in, ser), (link_out, chain)):
        _connect(gnd, connector, "1")
        _connect(rf_bus, connector, "2")
        _connect(gnd, connector, "3")
        _connect(v33, connector, "4")
        _connect(serial, connector, "5")
        _connect(srclk, connector, "6")
        _connect(rclk, connector, "7")

    sel_lines = [Net(f"SEL{lane}_N", circuit=circuit) for lane in range(LANES_PER_BOARD)]
    register = shift_register(circuit, "U1")
    for lane, output in enumerate(REGISTER_OUTPUTS):
        _connect(sel_lines[lane], register, output)
    _connect(ser, register, "SER")
    _connect(chain, register, "QH_SERIAL")
    _connect(srclk, register, "SRCLK")
    _connect(rclk, register, "RCLK")
    # SRCLR_N high and OE_N low, the same permanently-enabled arrangement the
    # matrix board documents. The split does not fix it and cannot: the hub's
    # seven-conductor link has no spare conductor for a clear, and the hub does
    # not route the net to its connector in the first place. Shifting a known
    # pattern stays the driver's mandatory first action.
    _connect(v33, register, "SRCLR_N")
    _connect(gnd, register, "OE_N")
    _connect(v33, register, "VCC")
    _connect(gnd, register, "GND")

    decouple = two_pin(
        circuit,
        "C17",
        "100n X7R 10%",
        "Capacitor_SMD:C_0402_1005Metric",
        mpn="CL05B104KO5NNNC",
        unit_cost_eur=0.003,
    )
    _connect(v33, decouple, "1")
    _connect(gnd, decouple, "2")

    for lane in range(LANES_PER_BOARD):
        matrix_cell(circuit, lane, rf_bus, gnd, v33, sel_lines[lane])
    # No mounting hole, and that is a decision rather than an omission. The
    # printed frame captures each board in a channel along its full 300 mm, so a
    # screw would add nothing the channel does not. There is also nowhere to put
    # one: the loops span the board's whole width for 276 of those 300 mm, and
    # the connector end is committed to forty-eight cell parts, the register and
    # both links. Retention is a print-iteration matter, which V7 moved out of
    # the gate precisely because a reprint fixes it and a respin does not.
    return circuit


NO_CONNECTS = {"U1": UNUSED_OUTPUT_PINS}
