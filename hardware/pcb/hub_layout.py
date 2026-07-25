"""Place the hub board and autoroute it with Freerouting.

Functional zones left to right: USB entry and charging, battery and rails,
MCU and expander, reader and its front end, with the harness connectors on
the board edges. The board lives in the service volume under one 50 mm player
rail, so the envelope is long and shallow. Placement is deterministic; track
routing is delegated to Freerouting and verified by KiCad DRC, as on the
matrix board.
"""

import os
import subprocess
import sys
from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.netlist import read_netlist
from hardware.pcb.ses_import import apply_session


OUTPUT = Path(__file__).parent / "generated" / "hub"
REVIEWED_SESSION = Path(__file__).parent / "routes" / "hub.ses"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/tmp/freerouting-2.2.4.jar")
FREEROUTING_PASSES = int(os.environ.get("FREEROUTING_PASSES", "40"))
# Longest straight bridge the post-route closer may lay. See _close_pad.
MAX_BRIDGE_MM = 2.5

BOARD_WIDTH = 110.0
BOARD_HEIGHT = 46.0

# M2.5 plated mounting holes bonded to ground, so the enclosure screws tie the
# shell to the pours rather than leaving it floating. 4.0 mm in from each corner
# keeps the 5.4 mm pad clear of the board edge and of J10, J4 and the reader
# supply row, the nearest parts to the corners.
MOUNTING_HOLE_SIZE = "2.7mm_M2.5"
MOUNTING_HOLE_INSET = 4.0


def _grid(
    refs: tuple[str, ...],
    origin: tuple[float, float],
    columns: int,
    pitch: tuple[float, float],
    rotation: float = 0.0,
) -> dict[str, Placement]:
    return {
        ref: Placement(
            Position(
                origin[0] + (index % columns) * pitch[0],
                origin[1] + (index // columns) * pitch[1],
            ),
            rotation=rotation,
        )
        for index, ref in enumerate(refs)
    }


def _placements() -> dict[str, Placement]:
    placements: dict[str, Placement] = {
        # USB entry.
        "J1": Placement(Position(6.0, 23.0), rotation=90.0),
        "U9": Placement(Position(16.0, 36.0)),
        "F1": Placement(Position(12.0, 12.0)),
        # Charger and battery.
        "U1": Placement(Position(22.0, 23.0)),
        "Q1": Placement(Position(28.0, 34.0)),
        "D1": Placement(Position(32.0, 34.0)),
        "J2": Placement(Position(28.0, 41.0)),
        "J3": Placement(Position(35.0, 41.0)),
        "SW1": Placement(Position(30.0, 6.0)),
        # Rails.
        "U2": Placement(Position(36.0, 23.0)),
        "L1": Placement(Position(36.0, 28.5)),
        "U5": Placement(Position(46.0, 23.0)),
        "L2": Placement(Position(46.0, 28.5)),
        "U7": Placement(Position(52.5, 23.0)),
        "U8": Placement(Position(52.5, 28.5)),
        # MCU and expander. C28 and C27 decouple the module locally, tucked into
        # the 3.3 mm gap between U8 and U4's left edge so they sit within 4 mm of
        # U4 pin 3 at (58.1, 28.3). WiFi TX peaks at 382 mA and the regulator's
        # bulk capacitors are 17 mm away.
        "U4": Placement(Position(64.0, 30.0)),
        # The gap between U8's courtyard (right edge 54.55) and U4's (left edge
        # 57.3) is 2.75 mm, narrower than an 0805's 3.4 mm courtyard, so C27 is
        # rotated to present its 1.96 mm side.
        "C28": Placement(Position(55.925, 25.5)),
        "C27": Placement(Position(55.925, 32.3), rotation=90.0),
        "U6": Placement(Position(63.0, 12.0), rotation=90.0),
        # Reader.
        "U3": Placement(Position(84.0, 28.0)),
        # 38.3, not 37.5: the 3225 crystal's courtyard is 4.20 x 3.50 mm against
        # the 2016 part's 3.00 x 2.60, which reached into R28 above it.
        "Y1": Placement(Position(77.5, 38.3)),
        "L3": Placement(Position(92.0, 24.0), rotation=90.0),
        "L4": Placement(Position(92.0, 30.0), rotation=90.0),
        # Edge connectors.
        "J4": Placement(Position(106.5, 23.0), rotation=270.0),
        "J5": Placement(Position(53.0, 42.5)),
        "J6": Placement(Position(66.5, 42.5)),
        "J7": Placement(Position(62.0, 3.5), rotation=180.0),
        "J8": Placement(Position(74.0, 3.5), rotation=180.0),
        "J9": Placement(Position(86.0, 3.5), rotation=180.0),
        "J10": Placement(Position(96.0, 3.5), rotation=180.0),
        # TP1 and TP2 sit directly on reviewed route waypoints. This makes the
        # recovery pads accessible without adding long, obstacle-blind stubs.
        "TP1": Placement(Position(62.16138, 11.31167945), back=True),
        "TP2": Placement(Position(55.9304, 10.1021), back=True),
        "TP3": Placement(Position(45.0, 6.0), back=True),
    }
    # Grid pitches respect the courtyards: a rotated 0603 needs 3.4 mm between
    # rows, an 0805 3.8 mm.
    placements.update(
        _grid(("R4", "R5", "R6", "R7", "R8", "R9", "R10"), (16.0, 8.0), 4, (2.2, 3.4), 90.0)
    )
    placements.update(_grid(("C13", "C14", "C15"), (18.0, 30.0), 3, (3.6, 3.8), 90.0))
    placements.update(_grid(("R1", "R2", "R3"), (14.0, 17.0), 3, (2.2, 3.4), 90.0))
    placements.update(_grid(("C12",), (12.0, 40.0), 1, (3.6, 3.8), 90.0))
    # Rail feedback and support parts.
    placements.update(
        _grid(("R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19"), (30.0, 12.0), 5, (2.2, 3.4), 90.0)
    )
    placements.update(_grid(("C1", "C2", "C3", "C7", "C8", "C9"), (41.0, 32.5), 2, (3.6, 3.8), 90.0))
    placements.update(_grid(("C10", "C11", "C6"), (48.0, 8.0), 3, (2.2, 3.4), 90.0))
    # MCU support: strapping, I2C, button, latch resistors.
    placements.update(
        _grid(("R20", "R21", "R22", "R23", "R24", "R25", "R26", "R31"), (70.0, 10.5), 4, (2.2, 3.4), 90.0)
    )
    # Reader supplies and crystal loads along the top, front end at the right.
    placements.update(
        _grid(("C20", "C21", "C22", "C23", "C24", "C25", "C26"), (76.0, 42.5), 7, (3.4, 2.2))
    )
    placements.update(_grid(("C31", "C32", "R27", "R28"), (73.0, 33.0), 2, (3.4, 2.2)))
    placements.update(_grid(("C33", "C34", "C35", "C36", "C37"), (95.0, 14.0), 2, (2.2, 3.4), 90.0))
    placements.update(_grid(("R29", "R30"), (95.0, 28.0), 2, (2.2, 3.4), 90.0))
    return placements


def generate_board(output: Path = OUTPUT / "hub.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "hub.net")
    builder = BoardBuilder(netlist, board_thickness_mm=1.0)
    builder.board.GetDesignSettings().m_CopperEdgeClearance = pcbnew.FromMM(0.25)
    # The stock GCT USB-C footprint holds 0.19 mm between its own mechanical
    # holes and its shield pads; that geometry is routinely fabricated, so the
    # default 0.25 mm hole clearance is relaxed rather than the footprint edited.
    builder.board.GetDesignSettings().m_HoleClearance = pcbnew.FromMM(0.15)
    builder.add_outline(BOARD_WIDTH, BOARD_HEIGHT)
    placements = _placements()
    inset = MOUNTING_HOLE_INSET
    corners = (
        (inset, inset),
        (BOARD_WIDTH - inset, inset),
        (inset, BOARD_HEIGHT - inset),
        (BOARD_WIDTH - inset, BOARD_HEIGHT - inset),
    )
    placements.update(
        {
            f"H{index}": Placement(Position(x, y))
            for index, (x, y) in enumerate(corners, start=1)
        }
    )
    for component in netlist.components:
        placement = placements.get(component.reference)
        if placement is not None:
            builder.add_component(component, placement)
    shield_pads = sorted(builder.pad_positions("J1", "SH"), key=lambda point: (point.y, point.x))
    top_left, top_right, bottom_left, bottom_right = shield_pads
    builder.add_track(
        "USB_SHIELD",
        (top_left, Position(1.5, 17.3), Position(1.5, 28.7)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (top_right, Position(6.5, 17.3), Position(1.5, 17.3)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (bottom_left, Position(1.5, 28.7)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (bottom_right, Position(8.0, 28.7), Position(1.5, 28.7)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (Position(1.5, 17.3), Position(9.0, 15.0)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_via("USB_SHIELD", Position(9.0, 15.0))
    builder.add_track(
        "USB_SHIELD",
        (Position(9.0, 15.0), Position(10.5, 15.0)),
        0.4,
    )
    builder.add_via("USB_SHIELD", Position(10.5, 15.0))
    builder.add_track(
        "USB_SHIELD",
        (
            Position(10.5, 15.0),
            Position(15.5, 15.0),
            Position(15.5, 18.0),
            Position(17.2231, 18.0),
        ),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_via("GND", Position(45.0, 6.0))
    builder.save(output)


def route_board(
    board_path: Path = OUTPUT / "hub.kicad_pcb",
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
    apply_session(
        board,
        session_path.read_text(encoding="utf-8"),
        net_aliases={"NFC_VMID_TAP": "NFC_VMID"},
    )
    _postroute_fixups(board)
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save routed board {board_path}")
    _finalize_ground(board_path)


def _postroute_fixups(board: pcbnew.BOARD) -> None:
    """Close whatever the router leaves open at the dense footprints (the
    PN5180 reader, the USB-C receptacle, the matrix connector) by connecting
    each still-open pad to its net's nearest routed copper. Adaptive, so it
    survives the router's run-to-run variation instead of hard-coding a path."""
    board.BuildConnectivity()
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            _close_pad(board, pad)


def _close_pad(board: pcbnew.BOARD, pad: pcbnew.PAD) -> None:
    net_name = pad.GetNetname()
    # GND pads bond to the ground pours in _finalize_ground.
    if not net_name or net_name == "GND":
        return
    pin = (pcbnew.ToMM(pad.GetPosition().x), pcbnew.ToMM(pad.GetPosition().y))
    target = _nearest_net_copper(board, net_name, pin, exclude_pad=pad)
    if target is None:
        # The router sometimes skips a short two-pin net outright, leaving no
        # copper at all to bridge to. Fall back to the net's nearest other pad.
        target = _nearest_net_pad(board, net_name, pin, exclude_pad=pad)
    if target is None:
        return
    distance_sq = (target[0] - pin[0]) ** 2 + (target[1] - pin[1]) ** 2
    # Already joined (router copper sits on the pad), or too far to bridge.
    # The ceiling is deliberately short: this lays a straight track with no
    # obstacle avoidance, so a long one crosses whatever lies between. A 9 mm
    # bridge across the MCU module once produced ten DRC violations on its own.
    # Anything longer is left for the router, and shows up as an unconnected
    # pad rather than a short.
    if distance_sq < 0.35**2 or distance_sq > MAX_BRIDGE_MM**2:
        return
    # A direct bridge on the pad's own face: shortest, so it stays clear of the
    # neighbouring pads a routed detour would run past.
    layer = "F.Cu" if pad.IsOnLayer(pcbnew.F_Cu) else "B.Cu"
    _route_waypoints(
        board,
        net_name,
        ((pin[0], pin[1], layer), (target[0], target[1], layer)),
        width=0.2,
    )


def _nearest_net_copper(
    board: pcbnew.BOARD,
    net_name: str,
    point: tuple[float, float],
    exclude_pad: pcbnew.PAD | None = None,
) -> tuple[float, float] | None:
    """Nearest track/via endpoint of the net's routed copper to point."""
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
    return best


def _nearest_net_pad(
    board: pcbnew.BOARD,
    net_name: str,
    point: tuple[float, float],
    exclude_pad: pcbnew.PAD | None = None,
) -> tuple[float, float] | None:
    """Nearest other pad on the net, for nets the router left bare."""
    best: tuple[float, float] | None = None
    best_d = float("inf")
    for footprint in board.GetFootprints():
        for candidate_pad in footprint.Pads():
            if candidate_pad.GetNetname() != net_name:
                continue
            if exclude_pad is not None and candidate_pad.GetPosition() == exclude_pad.GetPosition():
                continue
            position = candidate_pad.GetPosition()
            candidate = (pcbnew.ToMM(position.x), pcbnew.ToMM(position.y))
            distance = (candidate[0] - point[0]) ** 2 + (candidate[1] - point[1]) ** 2
            if distance < best_d:
                best_d = distance
                best = candidate
    return best


def _route_waypoints(
    board: pcbnew.BOARD,
    net_name: str,
    nodes: tuple[tuple[float, float, str], ...],
    width: float = 0.25,
) -> None:
    net = board.FindNet(net_name)
    for (ax, ay, alayer), (bx, by, blayer) in zip(nodes[:-1], nodes[1:]):
        if (ax, ay) != (bx, by):
            segment = pcbnew.PCB_TRACK(board)
            segment.SetLayer(board.GetLayerID(alayer))
            segment.SetWidth(pcbnew.FromMM(width))
            segment.SetNet(net)
            segment.SetStart(pcbnew.VECTOR2I_MM(ax, ay))
            segment.SetEnd(pcbnew.VECTOR2I_MM(bx, by))
            board.Add(segment)


def _finalize_ground(board_path: Path) -> None:
    """Pour ground on both faces after routing (a pre-routing pour would export
    as a Specctra plane and wall the layer off from the router). The pours bond
    the routed ground into planes and absorb the router's short ground spurs."""
    board = pcbnew.LoadBoard(str(board_path))
    if not board.Zones():
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
                (0.3, 0.3),
                (BOARD_WIDTH - 0.3, 0.3),
                (BOARD_WIDTH - 0.3, BOARD_HEIGHT - 0.3),
                (0.3, BOARD_HEIGHT - 0.3),
            ):
                point = pcbnew.VECTOR2I_MM(x, y)
                outline.Append(point.x, point.y)
            board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


if __name__ == "__main__":
    generate_board()
    if "--route" in sys.argv or "--reroute" in sys.argv:
        route_board(reroute="--reroute" in sys.argv)
