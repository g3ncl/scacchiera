"""Generate the routed 120 mm player light-bar PCB."""

from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.lightbar_geometry import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    CAPACITOR_Y,
    CONNECTOR_X,
    CONNECTOR_Y,
    LED_COUNT,
    LED_Y,
    POWER_BUS_Y,
    led_x,
)
from hardware.pcb.netlist import read_netlist


OUTPUT = Path(__file__).parent / "generated" / "lightbar"


def _placements() -> dict[str, Placement]:
    placements = {
        "J1": Placement(Position(CONNECTOR_X, CONNECTOR_Y)),
        f"C{LED_COUNT + 1}": Placement(Position(12.0, CAPACITOR_Y)),
    }
    for index in range(LED_COUNT):
        x = led_x(index)
        placements[f"D{index + 1}"] = Placement(Position(x, LED_Y), rotation=180.0)
        placements[f"C{index + 1}"] = Placement(Position(x, CAPACITOR_Y))
    return placements


def _route_led_chain(builder: BoardBuilder) -> None:
    for index in range(1, LED_COUNT):
        output = builder.pad_position(f"D{index}", "1")
        following_input = builder.pad_position(f"D{index + 1}", "3")
        builder.add_track(f"LED_DATA_{index}", (output, following_input), width=0.2)


def _route_power(builder: BoardBuilder) -> None:
    connector_power = builder.pad_position("J1", "1")
    last_capacitor_power = builder.pad_position(f"C{LED_COUNT}", "1")
    builder.add_track(
        "LED_5V",
        (
            connector_power,
            Position(2.4, connector_power.y),
            Position(2.4, POWER_BUS_Y),
            Position(last_capacitor_power.x, POWER_BUS_Y),
        ),
        width=0.8,
    )
    for index in range(1, LED_COUNT + 1):
        led_power = builder.pad_position(f"D{index}", "4")
        capacitor_power = builder.pad_position(f"C{index}", "1")
        builder.add_track(
            "LED_5V",
            (
                led_power,
                Position(led_power.x, 3.8),
                capacitor_power,
                Position(capacitor_power.x, POWER_BUS_Y),
            ),
            width=0.35,
        )
    bulk_power = builder.pad_position(f"C{LED_COUNT + 1}", "1")
    builder.add_track("LED_5V", (bulk_power, Position(bulk_power.x, POWER_BUS_Y)), width=0.8)


def _route_ground(builder: BoardBuilder) -> None:
    connector_ground = builder.pad_position("J1", "2")
    led_bus_start = Position(connector_ground.x, 0.9)
    last_led_ground = builder.pad_position(f"D{LED_COUNT}", "2")
    led_bus_end = Position(last_led_ground.x, 0.9)
    capacitor_bus_start = Position(connector_ground.x, 6.5)
    last_capacitor_ground = builder.pad_position(f"C{LED_COUNT}", "2")
    capacitor_bus_end = Position(last_capacitor_ground.x, 6.5)
    ground_junction = Position(connector_ground.x, 4.6)
    builder.add_track(
        "GND",
        (ground_junction, led_bus_start, led_bus_end),
        width=0.6,
        layer=pcbnew.B_Cu,
    )
    builder.add_track(
        "GND",
        (ground_junction, capacitor_bus_start, capacitor_bus_end),
        width=0.6,
        layer=pcbnew.B_Cu,
    )
    for index in range(1, LED_COUNT + 1):
        led_ground = builder.pad_position(f"D{index}", "2")
        led_via = Position(led_ground.x, led_bus_start.y)
        builder.add_track("GND", (led_ground, led_via), width=0.35)
        builder.add_via("GND", led_via)
        capacitor_ground = builder.pad_position(f"C{index}", "2")
        capacitor_via = Position(capacitor_ground.x, capacitor_bus_start.y)
        builder.add_track("GND", (capacitor_ground, capacitor_via), width=0.35)
        builder.add_via("GND", capacitor_via)
    bulk_ground = builder.pad_position(f"C{LED_COUNT + 1}", "2")
    bulk_via = Position(bulk_ground.x, capacitor_bus_start.y)
    builder.add_track("GND", (bulk_ground, bulk_via), width=0.8)
    builder.add_via("GND", bulk_via, diameter=0.8, drill=0.4)
    builder.add_track("GND", (connector_ground, ground_junction), width=0.6)
    builder.add_via("GND", ground_junction, diameter=0.8, drill=0.4)


def _route_external_data(builder: BoardBuilder) -> None:
    connector_input = builder.pad_position("J1", "3")
    first_input = builder.pad_position("D1", "3")
    builder.add_track(
        "DATA_IN",
        (
            connector_input,
            Position(connector_input.x, 0.7),
            Position(9.0, 0.7),
            Position(9.0, first_input.y),
            first_input,
        ),
        width=0.2,
    )

    connector_output = builder.pad_position("J1", "4")
    last_output = builder.pad_position(f"D{LED_COUNT}", "1")
    output_via = Position(119.0, 3.5)
    connector_via = Position(10.0, 2.4)
    builder.add_track("DATA_OUT", (last_output, output_via), width=0.2)
    builder.add_via("DATA_OUT", output_via)
    builder.add_track(
        "DATA_OUT",
        (output_via, Position(output_via.x, 4.2), Position(connector_via.x, 4.2), connector_via),
        width=0.2,
        layer=pcbnew.B_Cu,
    )
    builder.add_via("DATA_OUT", connector_via)
    builder.add_track(
        "DATA_OUT",
        (connector_via, Position(connector_output.x, connector_via.y), connector_output),
        width=0.2,
    )


def generate_board(output: Path = OUTPUT / "lightbar.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "lightbar.net")
    # 1.0 mm substrate keeps the bar thin behind the diffuser.
    builder = BoardBuilder(netlist, board_thickness_mm=1.0)
    builder.add_outline(BOARD_WIDTH, BOARD_HEIGHT)
    placements = _placements()
    for component in netlist.components:
        placement = placements.get(component.reference)
        if placement is not None:
            builder.add_component(component, placement)
    _route_led_chain(builder)
    _route_power(builder)
    _route_ground(builder)
    _route_external_data(builder)
    builder.save(output)


if __name__ == "__main__":
    generate_board()
