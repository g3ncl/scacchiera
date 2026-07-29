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
BOARD_WIDTH = 46.0
BOARD_HEIGHT = 32.0

MOUNTING_HOLE_SIZE = "2.7mm_M2.5"


def _placements() -> dict[str, Placement]:
    return {
        # Qualified 5 V enters here and leaves regulated at the far edge, so the
        # two harnesses cannot be confused during assembly.
        "J1": Placement(Position(7.0, 26.5)),
        "J2": Placement(Position(39.0, 26.5), rotation=180.0),
        # Cell lead on the long edge, away from both harness connectors.
        "J3": Placement(Position(23.0, 3.5), rotation=180.0),
        # Charger with its programming resistors around it and the input and
        # system bulk capacitors either side.
        "U1": Placement(Position(14.5, 15.0)),
        "C1": Placement(Position(7.0, 19.0), rotation=90.0),
        "C2": Placement(Position(22.0, 19.0), rotation=90.0),
        "C3": Placement(Position(22.0, 11.0), rotation=90.0),
        "R1": Placement(Position(10.5, 9.5)),
        "R2": Placement(Position(14.5, 9.5)),
        "R3": Placement(Position(18.5, 9.5)),
        "R4": Placement(Position(8.0, 12.0), rotation=90.0),
        "R5": Placement(Position(8.0, 15.5), rotation=90.0),
        # Boost: inductor beside the switch pin, output capacitor beside the
        # output pin, feedback divider behind them so the sense node stays short
        # and away from the switching node.
        "U2": Placement(Position(31.0, 15.0)),
        "L1": Placement(Position(29.0, 21.0)),
        "C4": Placement(Position(38.0, 15.0), rotation=90.0),
        "R6": Placement(Position(35.5, 9.5)),
        "R7": Placement(Position(31.5, 9.5)),
        "R8": Placement(Position(27.5, 9.5)),
        "H1": Placement(Position(3.5, 3.5)),
        "H2": Placement(Position(BOARD_WIDTH - 3.5, 3.5)),
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
    _relax_boost_pad_clearance(builder)
    builder.save(output)


def _relax_boost_pad_clearance(builder: BoardBuilder) -> None:
    """Let the boost keep its manufacturer land pattern.

    TI's DRL0006A pattern puts 0.14 mm between the two pad rows, because a
    1.2 mm wide body with 0.67 mm pads has nowhere else to go. That is under
    this project's 0.2 mm rule and above JLCPCB's 0.127 mm capability, so the
    exception is scoped to this part's pads rather than applied to the board,
    the same way the hub relaxes hole clearance for its USB-C receptacle
    instead of editing the receptacle.
    """
    footprint = builder.footprints["U2"]
    for pad in footprint.Pads():
        pad.SetLocalClearance(pcbnew.FromMM(0.13))


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
    board.BuildConnectivity()
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save routed board {board_path}")
    _finalize_ground(board_path)


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
