"""Place the hub board and autoroute it with Freerouting.

Functional zones left to right: USB entry and temperature gate, managed rails,
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
        # External power enters here. The safety gate remains physically ahead
        # of every connector and converter it controls.
        "J1": Placement(Position(6.0, 23.0), rotation=90.0),
        "R3": Placement(Position(12.0, 17.5)),
        "C12": Placement(Position(12.65, 20.0)),
        "U2": Placement(Position(19.0, 23.0)),
        "U1": Placement(Position(29.0, 23.0)),
        "J2": Placement(Position(15.0, 42.5)),
        "J11": Placement(Position(22.0, 42.5)),
        "J3": Placement(Position(32.0, 42.5)),
        # Managed 5 V returns through J3. Keep the buck switching loop compact
        # and away from the reader front end at the opposite side of the board.
        "U5": Placement(Position(42.0, 27.0)),
        "L1": Placement(Position(49.0, 27.0)),
        "U7": Placement(Position(53.5, 16.0)),
        "U8": Placement(Position(53.5, 22.0)),
        # MCU and expander.
        "U4": Placement(Position(65.0, 29.5)),
        "C28": Placement(Position(56.0, 32.0)),
        "C27": Placement(Position(56.0, 28.5), rotation=90.0),
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
        "J5": Placement(Position(47.0, 42.5)),
        "J6": Placement(Position(60.5, 42.5)),
        "J7": Placement(Position(62.0, 3.5), rotation=180.0),
        "J8": Placement(Position(74.0, 3.5), rotation=180.0),
        "J9": Placement(Position(86.0, 3.5), rotation=180.0),
        "J10": Placement(Position(96.0, 3.5), rotation=180.0),
        "TP1": Placement(Position(59.0, 8.0), back=True),
        "TP2": Placement(Position(56.0, 8.0), back=True),
        "TP3": Placement(Position(49.0, 8.0), back=True),
        "R17": Placement(Position(57.2, 16.0)),
        "R18": Placement(Position(57.0, 18.5), rotation=90.0),
        "R19": Placement(Position(57.0, 22.0), rotation=90.0),
        # RF matching follows the transmit path toward J4. The receive tap and
        # bias stay at the PN5180 pins so those high-impedance traces are short.
        "C33": Placement(Position(95.0, 14.0), rotation=90.0),
        "C34": Placement(Position(97.2, 14.0), rotation=90.0),
        "C35": Placement(Position(99.4, 14.0), rotation=90.0),
        "C36": Placement(Position(97.2, 17.4), rotation=90.0),
        "C37": Placement(Position(89.8, 33.8)),
        "R29": Placement(Position(87.0, 33.8)),
        "R30": Placement(Position(84.0, 33.8)),
    }
    # Temperature window and input switch support. The references follow the
    # signal flow: CC and shield nearest J1, then sensor references, switch
    # decoupling and ADC telemetry.
    placements.update(_grid(("R1", "R2"), (10.0, 10.0), 2, (2.4, 3.4), 90.0))
    placements.update(
        _grid(
            ("R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12", "R13", "R14", "R15"),
            (14.0, 8.0), 4, (3.0, 3.4), 90.0,
        )
    )
    placements.update(_grid(("C13", "C14", "C15", "C16", "C17"), (24.0, 30.0), 3, (3.6, 3.8), 90.0))
    # Buck and protected LED rail support.
    placements.update(_grid(("C1", "C2", "C3", "C4"), (39.0, 32.5), 2, (4.0, 3.8), 90.0))
    placements.update(_grid(("C10", "C11", "C6"), (48.0, 10.0), 3, (2.6, 3.4), 90.0))
    # MCU support: strapping, I2C, button, latch resistors.
    placements.update(
        _grid(("R20", "R21", "R22", "R23", "R24", "R25", "R26", "R31"), (69.0, 10.5), 4, (2.2, 3.4), 90.0)
    )
    # Reader supplies and crystal loads along the top, front end at the right.
    placements.update(
        _grid(("C20", "C21", "C22", "C23", "C24", "C25", "C26"), (76.0, 42.5), 7, (3.4, 2.2))
    )
    placements.update(_grid(("C31", "C32"), (75.0, 32.5), 2, (3.4, 2.2)))
    placements.update(_grid(("R27", "R28"), (75.0, 34.8), 2, (3.4, 2.2)))
    return placements


def generate_board(output: Path = OUTPUT / "hub.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "hub.net")
    builder = BoardBuilder(netlist, copper_layers=4, board_thickness_mm=1.0)
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
        (top_left, Position(2.2, 17.3), Position(2.2, 28.7)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (top_right, Position(6.5, 17.3), Position(2.2, 17.3)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (bottom_left, Position(2.2, 28.7)),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_track(
        "USB_SHIELD",
        (bottom_right, Position(8.0, 28.7), Position(2.2, 28.7)),
        0.4,
        pcbnew.B_Cu,
    )
    shield_resistor = builder.pad_position("R3", "1")
    shield_capacitor = builder.pad_position("C12", "1")
    shield_via = Position(shield_resistor.x, (shield_resistor.y + shield_capacitor.y) / 2)
    builder.add_track(
        "USB_SHIELD",
        (
            Position(2.2, 17.3),
            Position(shield_via.x, 17.3),
            shield_via,
        ),
        0.4,
        pcbnew.B_Cu,
    )
    builder.add_via("USB_SHIELD", shield_via)
    builder.add_track(
        "USB_SHIELD",
        (shield_resistor, shield_via, shield_capacitor),
        0.4,
    )
    # The receptacle's VBUS pads face the board edge and cannot escape around
    # its signal row on the front face. Take the qualified input under the
    # connector, then return beside the temperature-window pull-up.
    vbus_pad = builder.pad_position("J1", "A9")
    vbus_second_pad = builder.pad_position("J1", "A4")
    vbus_pullup = builder.pad_position("R12", "1")
    vbus_entry_via = Position(0.8, vbus_pad.y)
    vbus_window_via = Position(vbus_pullup.x - 1.5, vbus_pullup.y)
    builder.add_track("USB_VBUS", (vbus_pad, vbus_entry_via), 0.5)
    builder.add_track(
        "USB_VBUS",
        (
            vbus_second_pad,
            Position(vbus_entry_via.x, vbus_second_pad.y),
            vbus_entry_via,
        ),
        0.5,
    )
    builder.add_via("USB_VBUS", vbus_entry_via, diameter=0.8, drill=0.4)
    builder.add_track(
        "USB_VBUS",
        (
            vbus_entry_via,
            Position(vbus_entry_via.x, 14.5),
            Position(vbus_window_via.x, 14.5),
            vbus_window_via,
        ),
        0.5,
        pcbnew.B_Cu,
    )
    builder.add_via("USB_VBUS", vbus_window_via, diameter=0.8, drill=0.4)
    builder.add_track("USB_VBUS", (vbus_window_via, vbus_pullup), 0.5)
    vbus_reference = builder.pad_position("R4", "1")
    vbus_reference_via = Position(15.5, 7.0)
    builder.add_track(
        "USB_VBUS",
        (vbus_window_via, vbus_reference_via),
        0.5,
        pcbnew.B_Cu,
    )
    builder.add_via("USB_VBUS", vbus_reference_via, diameter=0.8, drill=0.4)
    builder.add_track(
        "USB_VBUS",
        (
            vbus_reference_via,
            Position(vbus_reference_via.x, vbus_reference.y),
            vbus_reference,
        ),
        0.5,
    )
    builder.add_track(
        "USB_VBUS",
        (vbus_reference, builder.pad_position("R5", "1")),
        0.5,
    )
    vbus_comparator = builder.pad_position("U2", "8")
    vbus_input_capacitor = builder.pad_position("C13", "1")
    vbus_comparator_escape = Position(vbus_comparator.x + 2.5, vbus_comparator.y - 1.025)
    vbus_input_capacitor_escape = Position(
        vbus_input_capacitor.x + 2.0,
        vbus_input_capacitor.y + 1.025,
    )
    for pad, escape in (
        (vbus_comparator, vbus_comparator_escape),
        (vbus_input_capacitor, vbus_input_capacitor_escape),
    ):
        builder.add_track("USB_VBUS", (pad, escape), 0.4)
        builder.add_via("USB_VBUS", escape, diameter=0.8, drill=0.4)
    sclk_reader = builder.pad_position("U3", "7")
    sclk_mcu = builder.pad_position("U4", "25")
    sclk_reader_via = Position(sclk_reader.x - 1.5, sclk_reader.y)
    sclk_mcu_via = Position(sclk_mcu.x + 1.5, sclk_mcu.y)
    builder.add_track("SCLK", (sclk_reader, sclk_reader_via), 0.2)
    builder.add_via("SCLK", sclk_reader_via)
    builder.add_track(
        "SCLK",
        (sclk_reader_via, sclk_mcu_via),
        0.2,
        pcbnew.In1_Cu,
    )
    builder.add_via("SCLK", sclk_mcu_via)
    builder.add_track("SCLK", (sclk_mcu_via, sclk_mcu), 0.2)
    for ground_via in (
        Position(25.0, 38.0),
        Position(35.0, 6.0),
        Position(45.0, 6.0),
        Position(100.0, 38.0),
    ):
        builder.add_via("GND", ground_via)
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
    _deduplicate_vias(board)
    _add_vbus_comparator_branch(board)
    board.BuildConnectivity()
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            _close_pad(board, pad)


def _add_vbus_comparator_branch(board: pcbnew.BOARD) -> None:
    """Join the two VBUS regions the router cannot escape around U2."""
    comparator = _pad_position(board, "U2", "8")
    input_capacitor = _pad_position(board, "C13", "1")
    comparator_via = (comparator[0] + 2.5, comparator[1] - 1.025)
    input_capacitor_via = (input_capacitor[0] + 2.0, input_capacitor[1] + 1.025)
    _route_waypoints(
        board,
        "USB_VBUS",
        (
            (comparator_via[0], comparator_via[1], "In2.Cu"),
            (input_capacitor_via[0], input_capacitor_via[1], "In2.Cu"),
        ),
        width=0.4,
    )


def _pad_position(board: pcbnew.BOARD, reference: str, number: str) -> tuple[float, float]:
    footprint = board.FindFootprintByReference(reference)
    if footprint is None:
        raise ValueError(f"footprint {reference} not found")
    for pad in footprint.Pads():
        if pad.GetNumber() == number:
            position = pad.GetPosition()
            return pcbnew.ToMM(position.x), pcbnew.ToMM(position.y)
    raise ValueError(f"pad {reference}.{number} not found")


def _deduplicate_vias(board: pcbnew.BOARD) -> None:
    """Remove a fixed via repeated verbatim by a Specctra session import."""
    seen: set[tuple[str, int, int]] = set()
    duplicates: list[pcbnew.PCB_TRACK] = []
    for track in board.Tracks():
        if track.Type() != pcbnew.PCB_VIA_T:
            continue
        position = track.GetPosition()
        # Specctra may return a fixed via one nanometre from its source
        # coordinate. Treat sub-micron differences as the same drilled hole.
        key = (
            track.GetNetname(),
            (position.x + 500) // 1000,
            (position.y + 500) // 1000,
        )
        if key in seen:
            duplicates.append(track)
        else:
            seen.add(key)
    for duplicate in duplicates:
        board.Remove(duplicate)


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
        for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
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
