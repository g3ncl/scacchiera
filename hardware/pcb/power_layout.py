"""Place the power board and autoroute it with Freerouting.

Small, two-layer and shaped to share a panel with the two light bars, so its
outline is fixed by that panel rather than by the parts. Placement follows the
current: qualified 5 V in at one edge, charger and cell in the middle, boost and
regulated 5 V out at the other, with the cell connector on the edge the harness
reaches. The switching loop of the boost is kept tight and away from the charger
sense pins, which is the one arrangement here that matters electrically.
"""

import os
import subprocess
import sys
from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.netlist import read_netlist
from hardware.pcb.ses_import import apply_session


OUTPUT = Path(__file__).parent / "generated" / "power"
REVIEWED_SESSION = Path(__file__).parent / "routes" / "power.ses"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/tmp/freerouting-2.2.4.jar")
FREEROUTING_PASSES = int(os.environ.get("FREEROUTING_PASSES", "40"))

# Sized to sit under one light bar on the shared panel: the bars are 120 mm
# long, so anything up to that width costs the panel nothing in either
# dimension it does not already spend.
BOARD_WIDTH = 90.0
BOARD_HEIGHT = 32.0

MOUNTING_HOLE_SIZE = "2.7mm_M2.5"


def _placements() -> dict[str, Placement]:
    return {
        # Qualified 5 V enters here and leaves regulated at the far edge, so the
        # two harnesses cannot be confused during assembly.
        "J1": Placement(Position(8.0, 27.0)),
        "J2": Placement(Position(81.0, 22.0), rotation=180.0),
        # Cell lead on the long edge, away from both harness connectors.
        "J3": Placement(Position(8.0, 4.0), rotation=180.0),
        # Charger with its programming resistors around it and the input and
        # system bulk capacitors either side.
        "U1": Placement(Position(15.0, 17.0)),
        "L1": Placement(Position(22.0, 17.0)),
        "C1": Placement(Position(17.0, 12.0)),
        "C2": Placement(Position(21.0, 12.0)),
        "C3": Placement(Position(8.0, 21.0), rotation=90.0),
        "C4": Placement(Position(11.0, 22.0), rotation=90.0),
        "C5": Placement(Position(14.0, 22.0), rotation=90.0),
        "C14": Placement(Position(11.0, 18.5), rotation=90.0),
        "C6": Placement(Position(18.0, 22.0), rotation=90.0),
        "C7": Placement(Position(24.5, 20.0), rotation=90.0),
        "C8": Placement(Position(15.0, 7.0), rotation=90.0),
        "R1": Placement(Position(16.5, 27.0)),
        "R2": Placement(Position(19.6, 27.0)),
        "R12": Placement(Position(22.7, 27.0)),
        "R13": Placement(Position(25.8, 27.0)),
        "R14": Placement(Position(17.5, 24.5)),
        # Boost: inductor beside the switch pin, output capacitor beside the
        # output pin, feedback divider behind them so the sense node stays short
        # and away from the switching node.
        "U2": Placement(Position(52.0, 17.0)),
        "L2": Placement(Position(58.0, 7.0), rotation=180.0),
        "U3": Placement(Position(43.0, 7.0)),
        "C20": Placement(Position(40.0, 7.0)),
        "C9": Placement(Position(51.25, 12.5), rotation=90.0),
        "C10": Placement(Position(47.0, 20.5)),
        "C11": Placement(Position(51.0, 21.0)),
        "C12": Placement(Position(51.0, 24.0)),
        "C13": Placement(Position(65.0, 16.0)),
        "C15": Placement(Position(40.0, 19.0), rotation=90.0),
        "C16": Placement(Position(43.0, 19.0)),
        "C17": Placement(Position(58.0, 23.0)),
        "C18": Placement(Position(62.0, 24.0), rotation=90.0),
        "C19": Placement(Position(66.0, 24.0), rotation=90.0),
        "R3": Placement(Position(47.0, 17.0)),
        "R4": Placement(Position(44.0, 15.0)),
        "R5": Placement(Position(48.2, 15.5)),
        "R6": Placement(Position(57.0, 15.0)),
        "R7": Placement(Position(60.0, 15.0)),
        "R8": Placement(Position(68.0, 10.0)),
        "R9": Placement(Position(68.0, 8.0)),
        "R10": Placement(Position(68.0, 6.0)),
        "R11": Placement(Position(58.0, 18.0)),
        "H1": Placement(Position(33.0, 28.0)),
        "H2": Placement(Position(BOARD_WIDTH - 3.5, 4.0)),
    }


def generate_board(output: Path = OUTPUT / "power.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "power.net")
    builder = BoardBuilder(netlist, board_thickness_mm=1.0)
    builder.board.GetDesignSettings().m_CopperEdgeClearance = pcbnew.FromMM(0.25)
    builder.add_outline(BOARD_WIDTH, BOARD_HEIGHT)
    placements = _placements()
    for component in netlist.components:
        # References starting with a hash are schematic-only power flags.
        if component.reference.startswith("#"):
            continue
        placement = placements.get(component.reference)
        if placement is None:
            raise ValueError(f"no placement for {component.reference}")
        builder.add_component(component, placement)
    builder.save(output)


def route_board(
    board_path: Path = OUTPUT / "power.kicad_pcb",
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
            raise FileNotFoundError(f"Freerouting jar not found at {FREEROUTING_JAR}")
        subprocess.run(
            (
                "java", "-Djava.awt.headless=true", "-jar", FREEROUTING_JAR,
                "-de", str(dsn), "-do", str(session_path), "-mp", str(FREEROUTING_PASSES),
            ),
            check=True,
        )
    board = pcbnew.LoadBoard(str(board_path))
    apply_session(board, session_path.read_text(encoding="utf-8"))
    _add_local_boost_routes(board)
    board.BuildConnectivity()
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save routed board {board_path}")
    _finalize_ground(board_path)


def _add_local_boost_routes(board: pcbnew.BOARD) -> None:
    """Close the two sub-millimetre regulator connections the router leaves."""
    for source_ref, source_pad, target_ref, target_pad, net_name in (
        ("U2", "1", "C9", "1", "BOOST_VCC"),
        ("U2", "10", "C11", "1", "BOOST_SS"),
    ):
        source = board.FindFootprintByReference(source_ref).FindPadByNumber(source_pad)
        target = board.FindFootprintByReference(target_ref).FindPadByNumber(target_pad)
        _add_segment(board, net_name, source.GetPosition(), target.GetPosition(), pcbnew.F_Cu)

def _add_segment(
    board: pcbnew.BOARD,
    net_name: str,
    start: pcbnew.VECTOR2I,
    end: pcbnew.VECTOR2I,
    layer: int,
) -> None:
    segment = pcbnew.PCB_TRACK(board)
    segment.SetNet(board.FindNet(net_name))
    segment.SetLayer(layer)
    segment.SetWidth(pcbnew.FromMM(0.2))
    segment.SetStart(start)
    segment.SetEnd(end)
    board.Add(segment)


def _finalize_ground(board_path: Path) -> None:
    """Pour ground on both faces after routing, as the other boards do."""
    board = pcbnew.LoadBoard(str(board_path))
    if not board.Zones():
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            zone = pcbnew.ZONE(board)
            zone.SetLayer(layer)
            zone.SetNet(board.FindNet("GND"))
            zone.SetLocalClearance(pcbnew.FromMM(0.2))
            zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
            # This compact power board has several high-current ground pins.
            # Solid joins avoid both thermal bottlenecks and isolated partial
            # spokes where routing passes close to the edge connector.
            zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
            outline = zone.Outline()
            outline.NewOutline()
            for point in (
                Position(0.3, 0.3),
                Position(BOARD_WIDTH - 0.3, 0.3),
                Position(BOARD_WIDTH - 0.3, BOARD_HEIGHT - 0.3),
                Position(0.3, BOARD_HEIGHT - 0.3),
            ):
                outline.Append(pcbnew.FromMM(point.x), pcbnew.FromMM(point.y))
            board.Add(zone)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


def main() -> None:
    generate_board()
    if "--route" in sys.argv or "--reroute" in sys.argv:
        route_board(reroute="--reroute" in sys.argv)


if __name__ == "__main__":
    main()
