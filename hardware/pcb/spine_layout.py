"""Place and route one 290 by 28 mm strip spine.

Four bands across the width. The eight strip sockets and the two chain links
face the strips; the shared RF bus runs the length behind them as a wide
microstrip over solid back-copper ground; the register and its decoupling sit
behind that, with a clear channel between the bus and the register for the
eight selection runs.

The RF bus is drawn here rather than handed to Freerouting, for two reasons. It
wants to be 3 mm wide and the router will not make it so, and its inductance is
the one thing the split adds to the shared bus that the monolith did not have:
a value that has to come from a drawn geometry the simulation can read back,
not from wherever an autorouter happened to put it.
"""

import os
import subprocess
import sys
from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.netlist import read_netlist
from hardware.pcb.ses_import import apply_session

from hardware.pcb.strip_geometry import (
    SPINE_DECOUPLE_X,
    SPINE_LENGTH,
    SPINE_LINK_IN_X,
    SPINE_LINK_OUT_X,
    SPINE_MOUNTING_HOLES,
    SPINE_PART_Y,
    SPINE_POUR_INSET,
    SPINE_REGISTER_X,
    SPINE_RF_WIDTH,
    SPINE_RF_Y,
    SPINE_SOCKETS,
    SPINE_SOCKET_Y,
    SPINE_WIDTH,
    socket_reference,
    spine_socket_x,
)


OUTPUT = Path(__file__).parent / "generated" / "spine"
REVIEWED_SESSION = Path(__file__).parent / "routes" / "spine.ses"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/tmp/freerouting-2.2.4.jar")
FREEROUTING_PASSES = int(os.environ.get("FREEROUTING_PASSES", "15"))

# Half-height of the band the router is kept out of, either side of the bus
# centre line: the 3 mm bus plus a comfortable clearance.
_RF_KEEPOUT_HALF = SPINE_RF_WIDTH / 2.0 + 0.5
BUS_STUB_WIDTH = 0.8


def _placements() -> dict[str, Placement]:
    placements: dict[str, Placement] = {
        "J1": Placement(Position(SPINE_LINK_IN_X, SPINE_SOCKET_Y)),
        "J2": Placement(Position(SPINE_LINK_OUT_X, SPINE_SOCKET_Y), rotation=180.0),
        "U1": Placement(Position(SPINE_REGISTER_X, SPINE_PART_Y)),
        "C1": Placement(Position(SPINE_DECOUPLE_X, SPINE_PART_Y), rotation=90.0),
    }
    for index in range(SPINE_SOCKETS):
        placements[socket_reference(index)] = Placement(
            Position(spine_socket_x(index), SPINE_SOCKET_Y)
        )
    for index, (x, y) in enumerate(SPINE_MOUNTING_HOLES, start=1):
        placements[f"H{index}"] = Placement(Position(x, y))
    return placements


def _route_rf_bus(builder: BoardBuilder) -> None:
    """Draw the shared bus and drop a stub onto every pin that taps it.

    One straight run at a fixed y, so the inductance each socket sees is a
    function of its own position and nothing else. That is what lets
    `hardware/sim/strip_rf.py` model the bus as a ladder with a segment per
    socket instead of guessing at a routed length.
    """
    taps = [("J1", "2"), ("J2", "2")]
    taps += [(socket_reference(index), "2") for index in range(SPINE_SOCKETS)]
    xs = [builder.pad_position(reference, pad).x for reference, pad in taps]
    builder.add_track(
        "RF_BUS",
        (Position(min(xs), SPINE_RF_Y), Position(max(xs), SPINE_RF_Y)),
        width=SPINE_RF_WIDTH,
    )
    for reference, pad in taps:
        position = builder.pad_position(reference, pad)
        builder.add_track(
            "RF_BUS",
            (position, Position(position.x, SPINE_RF_Y)),
            width=BUS_STUB_WIDTH,
        )


def _add_rf_keepout(builder: BoardBuilder) -> None:
    """Reserve the bus band on the front face.

    Only the front: the back is the bus's ground return and has to stay a solid
    plane under it, which the pour gives, while the router is free to use back
    copper elsewhere on the board.
    """
    zone = pcbnew.ZONE(builder.board)
    zone.SetIsRuleArea(True)
    zone.SetDoNotAllowTracks(True)
    zone.SetDoNotAllowVias(True)
    zone.SetLayer(builder.board.GetLayerID("F.Cu"))
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in (
        (0.0, SPINE_RF_Y - _RF_KEEPOUT_HALF),
        (SPINE_LENGTH, SPINE_RF_Y - _RF_KEEPOUT_HALF),
        (SPINE_LENGTH, SPINE_RF_Y + _RF_KEEPOUT_HALF),
        (0.0, SPINE_RF_Y + _RF_KEEPOUT_HALF),
    ):
        point = pcbnew.VECTOR2I_MM(x, y)
        outline.Append(point.x, point.y)
    builder.board.Add(zone)


def _add_ground_pour(board: pcbnew.BOARD) -> None:
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(board.FindNet("GND"))
        zone.SetLocalClearance(pcbnew.FromMM(0.2))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in (
            (SPINE_POUR_INSET, SPINE_POUR_INSET),
            (SPINE_LENGTH - SPINE_POUR_INSET, SPINE_POUR_INSET),
            (SPINE_LENGTH - SPINE_POUR_INSET, SPINE_WIDTH - SPINE_POUR_INSET),
            (SPINE_POUR_INSET, SPINE_WIDTH - SPINE_POUR_INSET),
        ):
            point = pcbnew.VECTOR2I_MM(x, y)
            outline.Append(point.x, point.y)
        board.Add(zone)


def _remove_rule_areas(board: pcbnew.BOARD) -> None:
    for zone in list(board.Zones()):
        if zone.GetIsRuleArea():
            board.Remove(zone)


def generate_board(output: Path = OUTPUT / "spine.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "spine.net")
    builder = BoardBuilder(netlist, board_thickness_mm=1.0)
    settings = builder.board.GetDesignSettings()
    settings.m_CopperEdgeClearance = pcbnew.FromMM(0.2)
    settings.m_ViasMinSize = pcbnew.FromMM(0.4)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.2)
    settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.1)
    builder.add_outline(SPINE_LENGTH, SPINE_WIDTH)
    placements = _placements()
    for component in netlist.components:
        placement = placements.get(component.reference)
        if placement is not None:
            builder.add_component(component, placement)
    _route_rf_bus(builder)
    _add_rf_keepout(builder)
    builder.save(output)


def _finalize_ground(board_path: Path) -> None:
    board = pcbnew.LoadBoard(str(board_path))
    if not board.Zones():
        _add_ground_pour(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


def route_board(
    board_path: Path = OUTPUT / "spine.kicad_pcb",
    *,
    reroute: bool = False,
) -> None:
    dsn = board_path.with_suffix(".dsn")
    session_path = REVIEWED_SESSION
    if reroute:
        session_path = board_path.with_suffix(".ses")
        board = pcbnew.LoadBoard(str(board_path))
        if not pcbnew.ExportSpecctraDSN(board, str(dsn)):
            raise OSError(f"Specctra DSN export failed for {board_path}")
        if not Path(FREEROUTING_JAR).is_file():
            raise FileNotFoundError(
                f"Freerouting jar not found at {FREEROUTING_JAR}; set FREEROUTING_JAR"
            )
        subprocess.run(
            (
                "java", "-Djava.awt.headless=true", "-jar", FREEROUTING_JAR,
                "-de", str(dsn), "-do", str(session_path), "-mp", str(FREEROUTING_PASSES),
            ),
            check=True,
        )
    board = pcbnew.LoadBoard(str(board_path))
    apply_session(board, session_path.read_text(encoding="utf-8"), frozenset({"RF_BUS"}))
    _remove_rule_areas(board)
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save routed board {board_path}")
    _finalize_ground(board_path)


if __name__ == "__main__":
    generate_board()
    route_board(reroute="--reroute" in sys.argv)
