"""One line antenna and its switch cell, on its own PCB.

Sixteen of these replace the monolithic matrix board's copper. The schematic is
deliberately not a new circuit: it instantiates the same `matrix_cell` the
matrix board validated, so the tank, the PIN switch and the bias steering are
the identical parts in the identical topology.

What the split changes is where the board boundary falls, and that was the whole
question. The cell's resonant tank (loop, 220 pF, trim pads, series diode, shunt
FET) sits entirely on this board, and the connector sits on the far side of the
100 nF DC block. So the harness adds series impedance to the shared bus, which
is a bus problem the trim pads can absorb, and not connector inductance inside
sixteen resonators, which nothing could. That distinction is the reason this
partition is buildable where an antenna-board-plus-daughterboard split was not.

Selection is one bit, arriving on the connector from the spine's shift register.
Splitting the register off the strip is what keeps the strip a single design:
all sixteen are the same board, and only the wire they are plugged into differs.
"""

from skidl import Circuit, Net, Part

from hardware.pcb.matrix import matrix_cell
from hardware.pcb.parts import PinDefinition, component


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def build_strip() -> Circuit:
    circuit = Circuit(name="strip")
    rf_bus = Net("RF_BUS", circuit=circuit)
    gnd = Net("GND", circuit=circuit)
    v33 = Net("3V3", circuit=circuit)
    sel_n = Net("SEL_N", circuit=circuit)

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

    # The same SM07B-GHS-TB the matrix board already binds, not a narrower
    # 5-pin part. Seven conductors are more than the five signals need, but
    # reusing the bound connector keeps the whole split subsystem at zero new
    # component types, which is worth more than two pins: a new unique Extended
    # part costs a 2.70 EUR feeder change and a datasheet ingest. The spares go
    # to ground, so the RF conductor runs between grounds at both ends of the
    # housing rather than beside the rail.
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
            PinDefinition("5", "SEL_N"),
            PinDefinition("6", "GND"),
            PinDefinition("7", "GND"),
        ),
        mpn="SM07B-GHS-TB(LF)(SN)",
        description="Spine link: RF bus between grounds, rail, and this line's select",
        unit_cost_eur=0.296,
    )
    _connect(gnd, connector, "1")
    _connect(rf_bus, connector, "2")
    _connect(gnd, connector, "3")
    _connect(v33, connector, "4")
    _connect(sel_n, connector, "5")
    _connect(gnd, connector, "6")
    _connect(gnd, connector, "7")

    matrix_cell(circuit, 0, rf_bus, gnd, v33, sel_n)
    # No mounting hole, and that is a decision rather than an omission. The
    # printed frame captures each strip in a channel along its full 300 mm, so a
    # screw would add nothing the channel does not already do. There is also
    # nowhere to put one: the loop spans the strip's whole width for 276 of
    # those 300 mm, the connector end is committed to the twelve cell parts, and
    # a grounded 5.4 mm pad at the far end would sit 3.2 mm from the loop and
    # load it. Retention is a print-iteration matter, which V7 moved out of the
    # gate precisely because a reprint fixes it and a respin does not.
    return circuit
