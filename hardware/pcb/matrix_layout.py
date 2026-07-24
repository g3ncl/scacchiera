"""Place the 300 mm matrix board and autoroute it with Freerouting.

Antenna copper is fixed by code: row loops on the front face (toward the
pieces), column loops on the back, so the two sets cross without jumpers. All
components sit on the back side in the left and bottom margins, keeping the
front face flat for the controlled air gap and the read budget. The switch
cells, registers, and connector are placed deterministically; the signal
routing between them is delegated to Freerouting, which the previous board
generation already proved out, and verified afterward by the real KiCad DRC.
"""

import os
import subprocess
import sys
from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.matrix_geometry import (
    BOARD_SIZE,
    LINE_COUNT,
    PLAY_ORIGIN,
    PLAY_SPAN,
    line_center,
)
from hardware.pcb.netlist import read_netlist
from hardware.pcb.ses_import import apply_session


OUTPUT = Path(__file__).parent / "generated" / "matrix"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/tmp/freerouting-2.2.4.jar")
FREEROUTING_PASSES = int(os.environ.get("FREEROUTING_PASSES", "12"))

# The ground pour covers the two component margins up to this line; the play
# area beyond it carries only antenna copper, per the read budget.
MARGIN_POUR_EDGE = 14.5
PLAY_CENTER = PLAY_ORIGIN + PLAY_SPAN / 2.0


def _antenna_placements() -> dict[str, Placement]:
    placements: dict[str, Placement] = {}
    for index in range(8):
        placements[f"L{index * 2 + 2}"] = Placement(
            Position(PLAY_CENTER, line_center(index))
        )
    for index in range(8, LINE_COUNT):
        placements[f"L{index * 2 + 2}"] = Placement(
            Position(line_center(index - 8), PLAY_CENTER), rotation=90.0, back=True
        )
    return placements


def _cell_placements(line: int) -> dict[str, Placement]:
    # Two part files per cell in the margin: the RF chain nearest the play
    # edge, the bias chain behind it. Freerouting connects them.
    rf_refs = (
        f"C{line * 4 + 1}", f"D{line * 2 + 1}", f"Q{line * 2 + 1}",
        f"C{line * 4 + 2}", f"C{line * 4 + 3}", f"C{line * 4 + 4}",
    )
    bias_refs = (
        f"R{line * 3 + 1}", f"L{line * 2 + 1}", f"R{line * 3 + 3}",
        f"R{line * 3 + 2}", f"D{line * 2 + 2}", f"Q{line * 2 + 2}",
    )
    placements: dict[str, Placement] = {}
    center = line_center(line % 8)
    for margin_offset, refs in ((10.6, rf_refs), (4.4, bias_refs)):
        for slot, ref in enumerate(refs):
            lane = center - 9.5 + 4.0 * slot
            if line < 8:
                placements[ref] = Placement(
                    Position(margin_offset, lane), rotation=90.0, back=True
                )
            else:
                placements[ref] = Placement(
                    Position(lane, margin_offset), rotation=0.0, back=True
                )
    return placements


def _corner_placements() -> dict[str, Placement]:
    # Each register sits central to its bank, in the inter-cell gap of its
    # margin: U1 (rows) mid-left, U2 (columns) mid-bottom, so all 16 selection
    # lines fan out short and the autorouter completes them. J1 sits beside U1
    # so the shared serial lines it feeds are a short local hop the router
    # handles; only the three register-to-U2 links are hand-routed afterward.
    return {
        "J1": Placement(Position(7.0, 3.5), rotation=180.0, back=True),
        "U1": Placement(Position(3.5, 155.5), rotation=90.0, back=True),
        "U2": Placement(Position(155.5, 5.5), back=True),
        "C65": Placement(Position(10.6, 158.5), rotation=90.0, back=True),
        "C66": Placement(Position(160.5, 5.5), rotation=90.0, back=True),
    }


def _check_column_antennas(builder: BoardBuilder) -> None:
    """The flipped, rotated column loops must land their terminals in the
    bottom margin; orientation conventions differ between pcbnew versions, so
    verify and correct rather than trust the sign."""
    for index in range(8, LINE_COUNT):
        ref = f"L{index * 2 + 2}"
        if builder.pad_position(ref, "1").y > 20.0:
            builder.footprints[ref].SetOrientationDegrees(270.0)
        terminal = builder.pad_position(ref, "1")
        if terminal.y > 20.0:
            raise ValueError(f"{ref} terminals did not land in the bottom margin: {terminal}")


def _add_ground_pour(board: pcbnew.BOARD) -> None:
    """Pour the margin ground after routing: exported before routing it becomes
    a Specctra plane that walls the front margin off from the router, so GND is
    routed as a normal net first and the pour bonds to it afterward."""
    edge = 0.3
    far = BOARD_SIZE - edge
    # Both faces: the front pour is the RF return, the back pour bonds the
    # component-side ground pads and stubs. Outside the margins both faces
    # carry only antenna copper.
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
            (edge, edge),
            (far, edge),
            (far, MARGIN_POUR_EDGE),
            (MARGIN_POUR_EDGE, MARGIN_POUR_EDGE),
            (MARGIN_POUR_EDGE, far),
            (edge, far),
        ):
            point = pcbnew.VECTOR2I_MM(x, y)
            outline.Append(point.x, point.y)
        board.Add(zone)


def generate_board(output: Path = OUTPUT / "matrix.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "matrix.net")
    builder = BoardBuilder(netlist, board_thickness_mm=1.0)
    settings = builder.board.GetDesignSettings()
    # KiCad's default 0.5 mm copper-to-edge rule is stricter than the margins
    # need; 0.2 mm matches what the autorouter actually holds along the edge.
    settings.m_CopperEdgeClearance = pcbnew.FromMM(0.2)
    # The U1 serial escape uses 0.4/0.2 mm vias to thread the register's
    # 0.65 mm pin pitch; allow them (standard fab minimum).
    settings.m_ViasMinSize = pcbnew.FromMM(0.4)
    settings.m_MinThroughDrill = pcbnew.FromMM(0.2)
    settings.m_ViasMinAnnularWidth = pcbnew.FromMM(0.1)
    builder.add_outline(BOARD_SIZE, BOARD_SIZE)
    placements = _antenna_placements()
    for line in range(LINE_COUNT):
        placements.update(_cell_placements(line))
    placements.update(_corner_placements())
    for component in netlist.components:
        placement = placements.get(component.reference)
        if placement is not None:
            builder.add_component(component, placement)
    _check_column_antennas(builder)
    _preroute_connector_escapes(builder)
    _add_corridor_keepouts(builder)
    builder.save(output)


def _preroute_connector_escapes(builder: BoardBuilder) -> None:
    """Give every J1 signal pin a short stub to a via clear of the connector's
    own clearance shadow, so the router picks each net up from open copper. The
    corner is too congested for the router to escape these pads on its own; the
    3V3 pin in particular is left islanded without this."""
    start = builder.pad_position("J1", "4")
    top = Position(start.x, 8.5)
    builder.add_track("3V3", (start, top), width=0.3, layer=pcbnew.B_Cu)
    builder.add_via("3V3", top)
    # The router routes every serial net to the bottom corner but never up the
    # congested left margin to U1's buried 0.65 mm pads. Split that work: place
    # a back-copper pickup stub per net near the corner for the router to reach,
    # and connect U1 down to it afterward (_postroute_fixups) through a reserved
    # front-copper lane the router is kept out of.


# Reserved front-copper lane band for the U1 serial verticals, and the lane x
# Each U1 serial pin drops straight down a front-copper lane at its own x,
# via'd with a 0.4 mm via that fits the register's 0.65 mm TSSOP pitch (so no
# back-copper fanout is needed and nothing collides with the router's own
# back-copper tracks). Reserve that front-copper lane band so the router keeps
# its routing out from under the verticals.
_U1_LANE_KEEPOUT = (0.8, 8.5, 4.9, 151.2, ("F.Cu",))


# The registers sit apart, each central to its bank, so all 16 selection lines
# route automatically. The cost is the four shared serial nets (SER, SRCLK,
# RCLK, CHAIN) spanning between J1 in the corner, U1 mid-left, and U2
# mid-bottom, plus the one line-14 gate link. Freerouting plateaus on exactly
# these, and its optimizer loops on fixed multi-segment wiring, so they are
# drawn deterministically after routing through reserved edge-lane keepouts.
#
# Edge lanes (fully clear, verified against pad positions): a left B.Cu lane
# rising from the corner to U1, and a bottom F.Cu lane running to U2. U1 and U2
# are back-copper SMD, so a front-copper trace passes over their pads and vias
# straight down onto the target pad, threading the 0.65 mm serial-pin pitch
# that the autorouter cannot.
_KEEPOUTS: tuple[tuple[float, float, float, float, tuple[str, ...]], ...] = (_U1_LANE_KEEPOUT,)

# Only three nets are hand-routed: the register-to-register links U1 -> U2.
# SER stays a short local J1 <-> U1 hop the router handles. Left B.Cu lane x and
# bottom F.Cu lane y are 0.5 mm apart (0.25 mm track keeps 0.25 mm clearance),
# and both are ordered to match the U1 pin x order so the fanout never crosses.
_LEFT_X = {"SEL_CHAIN": 0.9, "SEL_SRCLK": 1.4, "SEL_RCLK": 1.9}
_BOTTOM_Y = {"SEL_SRCLK": 0.9, "SEL_RCLK": 1.4, "SEL_CHAIN": 1.9}
_U1_FAN_Y = {"SEL_CHAIN": 150.1, "SEL_SRCLK": 150.6, "SEL_RCLK": 151.1}
# Staggered front-copper turn-up x just left of U2, lower pin nearer the chip.
_U2_TURN_X = {"SEL_SRCLK": 157.9, "SEL_RCLK": 157.3, "SEL_CHAIN": 156.7}


def _add_corridor_keepouts(builder: BoardBuilder) -> None:
    for x1, y1, x2, y2, layers in _KEEPOUTS:
        for layer_name in layers:
            zone = pcbnew.ZONE(builder.board)
            zone.SetIsRuleArea(True)
            zone.SetDoNotAllowTracks(True)
            zone.SetDoNotAllowVias(True)
            zone.SetLayer(builder.board.GetLayerID(layer_name))
            outline = zone.Outline()
            outline.NewOutline()
            for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
                point = pcbnew.VECTOR2I_MM(x, y)
                outline.Append(point.x, point.y)
            builder.board.Add(zone)


def _route_waypoints(
    board: pcbnew.BOARD,
    net_name: str,
    nodes: tuple[tuple[float, float, str], ...],
    width: float = 0.25,
    via_diameter: float = 0.6,
    via_drill: float = 0.3,
) -> None:
    """Lay a fixed polyline. Each node is (x, y, layer); the segment leaving a
    node runs on that node's layer, and a via is dropped wherever the layer
    changes between consecutive nodes."""
    net = board.FindNet(net_name)
    for (ax, ay, alayer), (bx, by, blayer) in zip(nodes[:-1], nodes[1:]):
        segment = pcbnew.PCB_TRACK(board)
        segment.SetLayer(board.GetLayerID(alayer))
        segment.SetWidth(pcbnew.FromMM(width))
        segment.SetNet(net)
        segment.SetStart(pcbnew.VECTOR2I_MM(ax, ay))
        segment.SetEnd(pcbnew.VECTOR2I_MM(bx, by))
        board.Add(segment)
        if alayer != blayer:
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I_MM(bx, by))
            via.SetWidth(pcbnew.FromMM(via_diameter))
            via.SetDrill(pcbnew.FromMM(via_drill))
            via.SetNet(net)
            board.Add(via)


def _pad_mm(board: pcbnew.BOARD, reference: str, number: str) -> tuple[float, float]:
    position = board.FindFootprintByReference(reference).FindPadByNumber(number).GetPosition()
    return (pcbnew.ToMM(position.x), pcbnew.ToMM(position.y))


def _remove_rule_areas(board: pcbnew.BOARD) -> None:
    for zone in list(board.Zones()):
        if zone.GetIsRuleArea():
            board.Remove(zone)


def _postroute_fixups(board: pcbnew.BOARD) -> None:
    """Drop each U1 serial pin down its reserved front-copper lane onto the
    back-copper pickup stub the router connected to J1/U2."""
    for pad in ("9", "11", "12", "14"):
        net_name = board.FindFootprintByReference("U1").FindPadByNumber(pad).GetNetname()
        pin = _pad_mm(board, "U1", pad)
        lane_x = pin[0]
        # If the router already ran this net's copper up to the U1 pad, adding a
        # lane would duplicate it (co-located via, crossing). Skip those.
        nearest_to_pad = _nearest_net_point(board, net_name, pin)
        if (nearest_to_pad[0] - pin[0]) ** 2 + (nearest_to_pad[1] - pin[1]) ** 2 < 1.0:
            continue
        # Where the router left this net nearest the lane foot, before adding
        # any of my own copper.
        target = _nearest_net_point(board, net_name, (lane_x, 10.0))
        # 0.4 mm via on the pad (fits the 0.65 mm pitch), front-copper straight
        # down the reserved lane.
        pad_via = pcbnew.PCB_VIA(board)
        pad_via.SetPosition(pcbnew.VECTOR2I_MM(lane_x, pin[1]))
        pad_via.SetWidth(pcbnew.FromMM(0.4))
        pad_via.SetDrill(pcbnew.FromMM(0.2))
        pad_via.SetNet(board.FindNet(net_name))
        board.Add(pad_via)
        _route_waypoints(
            board,
            net_name,
            (
                (lane_x, pin[1], "F.Cu"),
                (lane_x, target[1], "F.Cu"),
                (lane_x, target[1], "B.Cu"),
                (target[0], target[1], "B.Cu"),
            ),
            width=0.25,
            via_diameter=0.4,
            via_drill=0.2,
        )


def _nearest_net_point(
    board: pcbnew.BOARD, net_name: str, point: tuple[float, float]
) -> tuple[float, float]:
    """Nearest endpoint of the net's existing (router-placed) copper to point."""
    best: tuple[float, float] | None = None
    best_d = float("inf")
    for track in board.Tracks():
        if track.GetNetname() != net_name:
            continue
        ends = (
            [track.GetPosition()]
            if track.Type() == pcbnew.PCB_VIA_T
            else [track.GetStart(), track.GetEnd()]
        )
        for end in ends:
            candidate = (pcbnew.ToMM(end.x), pcbnew.ToMM(end.y))
            distance = (candidate[0] - point[0]) ** 2 + (candidate[1] - point[1]) ** 2
            if distance < best_d:
                best_d = distance
                best = candidate
    if best is None:
        raise ValueError(f"no router copper for net {net_name}")
    return best



def _finalize_ground(board_path: Path) -> None:
    board = pcbnew.LoadBoard(str(board_path))
    if not board.Zones():
        _add_ground_pour(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


def route_board(board_path: Path = OUTPUT / "matrix.kicad_pcb") -> None:
    """Export Specctra DSN, run Freerouting headless, import the session, fill
    the ground pour. Idempotent from the placement."""
    dsn = board_path.with_suffix(".dsn")
    ses = board_path.with_suffix(".ses")
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
            "-de", str(dsn), "-do", str(ses), "-mp", str(FREEROUTING_PASSES),
        ),
        check=True,
    )
    board = pcbnew.LoadBoard(str(board_path))
    apply_session(board, ses.read_text(encoding="utf-8"))
    _remove_rule_areas(board)
    _postroute_fixups(board)
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save routed board {board_path}")
    _finalize_ground(board_path)


if __name__ == "__main__":
    generate_board()
    if "--route" in sys.argv:
        route_board()
