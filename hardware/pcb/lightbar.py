"""Player light bar: 14 addressable pixels behind the rail diffuser.

docs/functional/interface.md fixes the envelope: 120 x 8.5 mm, low-current
LEDs, every component on the front face behind a replaceable diffuser. One
addressable pixel per position is the cheapest circuit that still covers the
feedback semantics (the red illegal-position flash plus move, result, WiFi,
and countdown cues need more than one color), because the controller is inside
the LED: the whole bar is LEDs, decoupling, and a connector, and the hub drives
it over a single data line.

The pixel is an SK6805MINI-E rather than the WS2812C-2020 this replaced.
JLCPCB cannot assemble a 120 x 8.5 mm outline, so the bar is populated by hand,
and the WS2812C's pads sit under its body where an iron cannot reach them. The
SK6805's legs extend past the body instead. It keeps the same 5 mA per channel
class, so the 5 V rail budget is unchanged, but it is far wider, which is what
sets the pixel count at 14 (see lightbar_geometry).
"""

from skidl import Circuit, Net, Part

from hardware.pcb.lightbar_geometry import LED_COUNT
from hardware.pcb.parts import PinDefinition, component, two_pin


def _connect(net: Net, part: Part, pin: str) -> None:
    net += part[pin]


def build_lightbar() -> Circuit:
    circuit = Circuit(name="lightbar")
    power = Net("LED_5V", circuit=circuit)
    ground = Net("GND", circuit=circuit)
    data = Net("DATA_IN", circuit=circuit)
    # The schematic generator emits a GND power symbol; ERC wants that net
    # driven, so flag it. DNP: the flag exists only on paper.
    ground_flag = Part("power", "PWR_FLAG", tool="kicad9", circuit=circuit, ref="#FLG01", tag="GND_FLAG")
    ground_flag.footprint = "TestPoint:TestPoint_Pad_D1.0mm"
    ground_flag.fitted = "DNP"
    _connect(ground, ground_flag, "1")
    connector = component(
        circuit,
        "J1",
        "A1257WR-S-4P",
        "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal",
        (
            PinDefinition("1", "LED_5V"),
            PinDefinition("2", "GND"),
            PinDefinition("3", "DATA_IN"),
            PinDefinition("4", "DATA_OUT"),
        ),
        mpn="A1257WR-S-4P",
        description="Light bar input and daisy-chain output",
        unit_cost_eur=0.30,
    )
    _connect(power, connector, "1")
    _connect(ground, connector, "2")
    _connect(data, connector, "3")

    for index in range(LED_COUNT):
        output = Net("DATA_OUT" if index == LED_COUNT - 1 else f"LED_DATA_{index + 1}", circuit=circuit)
        led = component(
            circuit,
            f"D{index + 1}",
            "SK6805MINI-E",
            "Chessboard:SK6805MINI-E",
            (
                PinDefinition("1", "VDD"),
                PinDefinition("2", "DOUT"),
                PinDefinition("3", "GND"),
                PinDefinition("4", "DIN"),
            ),
            mpn="SK6805MINI-E",
            description="5 mA per channel addressable RGB LED, iron solderable",
            unit_cost_eur=0.10,
        )
        _connect(power, led, "1")
        _connect(output, led, "2")
        _connect(ground, led, "3")
        _connect(data, led, "4")
        data = output
        capacitor = two_pin(
            circuit,
            f"C{index + 1}",
            "100n",
            "Capacitor_SMD:C_0402_1005Metric",
            mpn="CL05B104KO5NNNC",
            unit_cost_eur=0.003,
        )
        _connect(power, capacitor, "1")
        _connect(ground, capacitor, "2")
    _connect(data, connector, "4")
    bulk = two_pin(
        circuit,
        f"C{LED_COUNT + 1}",
        "100u 6.3V",
        "Capacitor_SMD:C_1210_3225Metric",
        mpn="CL32A107MQVNNNE",
        unit_cost_eur=0.09,
    )
    _connect(power, bulk, "1")
    _connect(ground, bulk, "2")
    return circuit
