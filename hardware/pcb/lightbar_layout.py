"""Generate the routed 120 mm player light-bar PCB."""

from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.lightbar_geometry import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    BULK_X,
    BULK_Y,
    CAPACITOR_Y,
    CONNECTOR_X,
    CONNECTOR_Y,
    DATA_IN_Y,
    DATA_RETURN_Y,
    LED_COUNT,
    LED_Y,
    POUR_INSET,
    POWER_BUS_Y,
    led_x,
)
from hardware.pcb.netlist import read_netlist


OUTPUT = Path(__file__).parent / "generated" / "lightbar"

# Harvatek datasheet page 5: 1 DOUT, 2 GND, 3 DIN, 4 VDD.
LED_DOUT, LED_GND, LED_DIN, LED_VDD = "1", "2", "3", "4"


def _placements() -> dict[str, Placement]:
    placements = {
        "J1": Placement(Position(CONNECTOR_X, CONNECTOR_Y)),
        f"C{LED_COUNT + 1}": Placement(Position(BULK_X, BULK_Y)),
    }
    for index in range(LED_COUNT):
        x = led_x(index)
        # 180 degrees puts DOUT on the trailing edge and DIN on the leading
        # edge, so each data hop is a short diagonal across the pixel gap
        # instead of a track doubling back under two LEDs.
        placements[f"D{index + 1}"] = Placement(Position(x, LED_Y), rotation=180.0)
        # 90 puts terminal 1 on the bus side (below) and terminal 2 above it,
        # so neither stub crosses the other terminal. 270 mirrors them and the
        # 5 V stub then runs straight through the ground pad.
        placements[f"C{index + 1}"] = Placement(Position(x, CAPACITOR_Y), rotation=90.0)
    return placements


def _route_led_chain(builder: BoardBuilder) -> None:
    for index in range(1, LED_COUNT):
        output = builder.pad_position(f"D{index}", LED_DOUT)
        following_input = builder.pad_position(f"D{index + 1}", LED_DIN)
        builder.add_track(f"LED_DATA_{index}", (output, following_input), width=0.2)


def _route_power(builder: BoardBuilder) -> None:
    connector_power = builder.pad_position("J1", "1")
    last_led_power = builder.pad_position(f"D{LED_COUNT}", LED_VDD)
    bulk_power = builder.pad_position(f"C{LED_COUNT + 1}", "1")
    bus_end_x = max(last_led_power.x, bulk_power.x)
    builder.add_track(
        "LED_5V",
        (
            connector_power,
            Position(connector_power.x, POWER_BUS_Y),
            Position(bus_end_x, POWER_BUS_Y),
        ),
        # 0.6 mm carries the 14-pixel bus (224 mA all white) with wide margin
        # and keeps 0.25 mm to the connector's mounting pad, where 0.8 mm left
        # only 0.15 mm.
        width=0.6,
    )
    for index in range(1, LED_COUNT + 1):
        led_power = builder.pad_position(f"D{index}", LED_VDD)
        builder.add_track(
            "LED_5V",
            (led_power, Position(led_power.x, POWER_BUS_Y)),
            width=0.35,
        )
        capacitor_power = builder.pad_position(f"C{index}", "1")
        builder.add_track(
            "LED_5V",
            (capacitor_power, Position(capacitor_power.x, POWER_BUS_Y)),
            width=0.35,
        )
    builder.add_track(
        "LED_5V",
        (bulk_power, Position(bulk_power.x, POWER_BUS_Y)),
        width=0.6,
    )


def _route_ground(builder: BoardBuilder) -> None:
    """Drop a via at every ground pad; _finalize_ground pours around them."""
    grounds = [("J1", "2"), (f"C{LED_COUNT + 1}", "2")]
    grounds += [(f"D{index}", LED_GND) for index in range(1, LED_COUNT + 1)]
    grounds += [(f"C{index}", "2") for index in range(1, LED_COUNT + 1)]
    for reference, pad in grounds:
        position = builder.pad_position(reference, pad)
        builder.add_via("GND", position)


def _route_external_data(builder: BoardBuilder) -> None:
    connector_input = builder.pad_position("J1", "3")
    first_input = builder.pad_position("D1", LED_DIN)
    builder.add_track(
        "DATA_IN",
        (
            connector_input,
            Position(connector_input.x, DATA_IN_Y),
            Position(first_input.x, DATA_IN_Y),
            first_input,
        ),
        width=0.2,
    )

    # The chain ends at the far right, so its return leg crosses the whole bar
    # on back copper, above the ground vias and inside the pour's clearance.
    connector_output = builder.pad_position("J1", "4")
    last_output = builder.pad_position(f"D{LED_COUNT}", LED_DOUT)
    far_via = Position(last_output.x + 1.5, DATA_RETURN_Y)
    near_via = connector_output
    builder.add_track(
        "DATA_OUT",
        (last_output, Position(far_via.x, last_output.y), far_via),
        width=0.2,
    )
    builder.add_via("DATA_OUT", far_via)
    builder.add_track("DATA_OUT", (far_via, near_via), width=0.2, layer=pcbnew.B_Cu)
    builder.add_via("DATA_OUT", near_via)


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
    # Same block as every board, on the right; one line because the bar is
    # 8.5 mm tall. Mirrored so it reads from the back.
    builder.add_title(
        "SCACCHIERA · LIGHTBAR · rev 1.0 · 2026 · Claudio Genovese",
        Position(78.0, 4.25),
        height=0.9,
        back=True,
    )
    builder.save(output)
    _finalize_ground(output)


def _finalize_ground(board_path: Path) -> None:
    """Pour and fill back-copper ground on a reloaded board.

    ZONE_FILLER segfaults against a board still being built, so this follows
    the same save-reload-fill order the hub and matrix layouts use.
    """
    board = pcbnew.LoadBoard(str(board_path))
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(board.FindNet("GND"))
    zone.SetLocalClearance(pcbnew.FromMM(0.2))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in (
        (POUR_INSET, POUR_INSET),
        (BOARD_WIDTH - POUR_INSET, POUR_INSET),
        (BOARD_WIDTH - POUR_INSET, BOARD_HEIGHT - POUR_INSET),
        (POUR_INSET, BOARD_HEIGHT - POUR_INSET),
    ):
        point = pcbnew.VECTOR2I_MM(x, y)
        outline.Append(point.x, point.y)
    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


if __name__ == "__main__":
    generate_board()
