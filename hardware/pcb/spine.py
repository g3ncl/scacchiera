"""Backplane for eight line-antenna strips: RF bus, rail, and one select each.

Two of these carry the split sensing plane, one under the row strips and one
under the columns. Together they hold exactly what the monolithic matrix board
held outside its switch cells: two 74HC595s chained into sixteen one-hot active
low selections, and one shared 13.56 MHz bus fanned out to every line.

The board is deliberately dumb. It distributes, it does not process, and the
only active part is the register. That keeps the piece of the sensing plane that
could ever need a respin down to a 290 by 28 mm board.

The pair chains exactly as U1 and U2 did on the monolith: the hub drives the
first spine's link in, its QH' leaves on the link out, and the second spine
takes that as its serial in. Both links carry the same seven conductors, so the
in and out connectors are one pinout used in two directions.
"""

from skidl import Circuit, Net, Part

from hardware.pcb.matrix import shift_register
from hardware.pcb.parts import PinDefinition, component, mounting_hole, two_pin
from hardware.pcb.strip_geometry import (
    SPINE_MOUNTING_HOLES,
    SPINE_SOCKETS,
    socket_reference,
)

# QA through QH map to this spine's eight lines in socket order.
REGISTER_OUTPUTS = ("QA", "QB", "QC", "QD", "QE", "QF", "QG", "QH")


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def _link(circuit: Circuit, ref: str, serial_net_name: str, description: str) -> Part:
    """One end of the hub-to-spine-to-spine chain.

    Pin 5 is the only conductor whose meaning differs between the two ends: it
    is serial data in on the link in and the register's QH' on the link out.
    Everything else passes straight through, so a spine is electrically a tee on
    the bus and the rail.
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


def _socket(circuit: Circuit, index: int) -> Part:
    """One strip's harness socket. Pinout mirrors the strip's own J1."""
    return component(
        circuit,
        socket_reference(index),
        "SM07B-GHS-TB",
        "Connector_JST:JST_GH_SM07B-GHS-TB_1x07-1MP_P1.25mm_Horizontal",
        (
            PinDefinition("1", "GND"),
            PinDefinition("2", "RF_BUS"),
            PinDefinition("3", "GND"),
            PinDefinition("4", "3V3"),
            PinDefinition("5", f"SEL{index}_N"),
            PinDefinition("6", "GND"),
            PinDefinition("7", "GND"),
        ),
        mpn="SM07B-GHS-TB(LF)(SN)",
        description=f"Line antenna strip {index}: bus, rail, and its one select",
        unit_cost_eur=0.296,
    )


def build_spine() -> Circuit:
    circuit = Circuit(name="spine")
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

    link_in = _link(circuit, "J1", "SEL_SER", "Link in: from the hub, or from the previous spine")
    link_out = _link(circuit, "J2", "SEL_CHAIN", "Link out: bus, rail and this spine's QH'")
    for connector, serial in ((link_in, ser), (link_out, chain)):
        _connect(gnd, connector, "1")
        _connect(rf_bus, connector, "2")
        _connect(gnd, connector, "3")
        _connect(v33, connector, "4")
        _connect(serial, connector, "5")
        _connect(srclk, connector, "6")
        _connect(rclk, connector, "7")

    sel_lines = [Net(f"SEL{index}_N", circuit=circuit) for index in range(SPINE_SOCKETS)]
    for index in range(SPINE_SOCKETS):
        socket = _socket(circuit, index)
        _connect(gnd, socket, "1")
        _connect(rf_bus, socket, "2")
        _connect(gnd, socket, "3")
        _connect(v33, socket, "4")
        _connect(sel_lines[index], socket, "5")
        _connect(gnd, socket, "6")
        _connect(gnd, socket, "7")

    register = shift_register(circuit, "U1")
    for position, output in enumerate(REGISTER_OUTPUTS):
        _connect(sel_lines[position], register, output)
    _connect(ser, register, "SER")
    _connect(chain, register, "QH_SERIAL")
    _connect(srclk, register, "SRCLK")
    _connect(rclk, register, "RCLK")
    # SRCLR_N high and OE_N low, the same permanently-enabled arrangement the
    # matrix board documents. The split does not fix it and cannot: the hub's
    # seven-conductor link has no spare conductor for a clear, and the hub does
    # not route the net to its connector in the first place. Shifting a known
    # sixteen-bit pattern stays the driver's mandatory first action.
    _connect(v33, register, "SRCLR_N")
    _connect(gnd, register, "OE_N")
    _connect(v33, register, "VCC")
    _connect(gnd, register, "GND")

    decouple = two_pin(
        circuit,
        "C1",
        "100n X7R 10%",
        "Capacitor_SMD:C_0402_1005Metric",
        mpn="CL05B104KO5NNNC",
        unit_cost_eur=0.003,
    )
    _connect(v33, decouple, "1")
    _connect(gnd, decouple, "2")

    for index in range(1, len(SPINE_MOUNTING_HOLES) + 1):
        mounting_hole(circuit, f"H{index}", gnd)
    return circuit
