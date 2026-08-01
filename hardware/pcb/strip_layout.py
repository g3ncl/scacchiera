"""Place and route one 300 by 33 mm line-antenna strip.

The loop is front copper and every component is on the back, which is the
monolith's rule and the reason it exists: the top face has to stay flat against
the controlled air gap. Nothing but antenna copper goes past
`STRIP_POUR_EDGE`, enforced with a keepout rather than left to the router's
judgement, so the 276 mm of loop can never acquire a signal track crossing it.

Placement is deterministic; the twelve-part component zone is delegated to
Freerouting exactly as the matrix board's margins are, and verified by the real
KiCad DRC afterwards.
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
    LOOP_CENTER_ACROSS,
    PLAY_CENTER,
    STRIP_CONNECTOR,
    STRIP_LENGTH,
    STRIP_POUR_EDGE,
    STRIP_THICKNESS,
    STRIP_WIDTH,
    strip_component_slots,
)


OUTPUT = Path(__file__).parent / "generated" / "strip"
REVIEWED_SESSION = Path(__file__).parent / "routes" / "strip.ses"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/tmp/freerouting-2.2.4.jar")
FREEROUTING_PASSES = int(os.environ.get("FREEROUTING_PASSES", "10"))

POUR_EDGE_INSET = 0.3


def _placements() -> dict[str, Placement]:
    placements: dict[str, Placement] = {
        # The loop keeps the monolith's position along the play axis, so the
        # copper this board carries is the copper already extracted and
        # simulated rather than a new shape.
        "L2": Placement(Position(PLAY_CENTER, LOOP_CENTER_ACROSS)),
        "J1": Placement(Position(*STRIP_CONNECTOR), rotation=180.0, back=True),
    }
    for reference, (x, y) in strip_component_slots().items():
        # Rotation 0 puts a two-pin part's terminals on the x axis, which is
        # across the columns: each net then joins a pad to the pad of the part
        # beside or above it instead of reaching around a body.
        placements[reference] = Placement(Position(x, y), back=True)
    return placements


def _add_antenna_keepout(builder: BoardBuilder) -> None:
    """Forbid tracks and vias over the loop, on both faces.

    The router has no reason to go there and every reason not to: a track under
    the antenna is a shorted turn, and a via through it puts copper in the play
    area the read budget reserves. Stating it as a rule area is cheaper than
    discovering it in a DRC report.
    """
    for layer_name in ("F.Cu", "B.Cu"):
        zone = pcbnew.ZONE(builder.board)
        zone.SetIsRuleArea(True)
        zone.SetDoNotAllowTracks(True)
        zone.SetDoNotAllowVias(True)
        zone.SetLayer(builder.board.GetLayerID(layer_name))
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in (
            (STRIP_POUR_EDGE, 0.0),
            (STRIP_LENGTH, 0.0),
            (STRIP_LENGTH, STRIP_WIDTH),
            (STRIP_POUR_EDGE, STRIP_WIDTH),
        ):
            point = pcbnew.VECTOR2I_MM(x, y)
            outline.Append(point.x, point.y)
        builder.board.Add(zone)


def _add_ground_pour(board: pcbnew.BOARD) -> None:
    """Both faces of the component zone, and nothing beyond it.

    The front pour is the RF return for the cell; the back pour bonds the
    component-side ground pads. Neither may reach under the loop, so both stop
    at the same edge the monolith's margin pour stops at.
    """
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
            (POUR_EDGE_INSET, POUR_EDGE_INSET),
            (STRIP_POUR_EDGE, POUR_EDGE_INSET),
            (STRIP_POUR_EDGE, STRIP_WIDTH - POUR_EDGE_INSET),
            (POUR_EDGE_INSET, STRIP_WIDTH - POUR_EDGE_INSET),
        ):
            point = pcbnew.VECTOR2I_MM(x, y)
            outline.Append(point.x, point.y)
        board.Add(zone)


def _remove_rule_areas(board: pcbnew.BOARD) -> None:
    for zone in list(board.Zones()):
        if zone.GetIsRuleArea():
            board.Remove(zone)


def generate_board(output: Path = OUTPUT / "strip.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "strip.net")
    builder = BoardBuilder(netlist, board_thickness_mm=STRIP_THICKNESS)
    settings = builder.board.GetDesignSettings()
    settings.m_CopperEdgeClearance = pcbnew.FromMM(0.2)
    settings.m_ViasMinSize = pcbnew.FromMM(0.4)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.2)
    settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.1)
    builder.add_outline(STRIP_LENGTH, STRIP_WIDTH)
    placements = _placements()
    for component in netlist.components:
        placement = placements.get(component.reference)
        if placement is not None:
            builder.add_component(component, placement)
    _check_loop_terminals(builder)
    _add_antenna_keepout(builder)
    builder.save(output)


def _check_loop_terminals(builder: BoardBuilder) -> None:
    """The loop's two terminals must land inside the component zone.

    The footprint puts them on tails at one end, and which end that is depends
    on the placement rotation. Verify rather than trust it: a terminal past the
    pour edge is a pad the router cannot reach and a pad the pour cannot bond.
    """
    for number in ("1", "2"):
        terminal = builder.pad_position("L2", number)
        if terminal.x > STRIP_POUR_EDGE:
            raise ValueError(
                f"L2 terminal {number} landed at x={terminal.x:.2f}, "
                f"past the {STRIP_POUR_EDGE} mm pour edge"
            )


def _finalize_ground(board_path: Path) -> None:
    board = pcbnew.LoadBoard(str(board_path))
    if not board.Zones():
        _add_ground_pour(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


def route_board(
    board_path: Path = OUTPUT / "strip.kicad_pcb",
    *,
    reroute: bool = False,
) -> None:
    """Import the reviewed route, or explicitly replace it with Freerouting."""
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
    apply_session(board, session_path.read_text(encoding="utf-8"), frozenset())
    _remove_rule_areas(board)
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save routed board {board_path}")
    _finalize_ground(board_path)


if __name__ == "__main__":
    generate_board()
    route_board(reroute="--reroute" in sys.argv)
