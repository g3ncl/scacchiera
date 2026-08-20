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

# Two copper layers, at the cost of length. A four-layer version of this board
# fits in 110 mm, but four layers cost multiples of two at every fab, and the
# service volume is a 310 mm player rail with only the hub in it: length is the
# one dimension this design has to spare. Width stays at 46 mm because that is
# what fits under a 50 mm rail.
BOARD_WIDTH = 162.0
BOARD_HEIGHT = 46.0

# Extra length only helps if the parts use it. Each functional zone slides right
# by a fixed amount, so the crossings between zones open while the geometry
# inside one is untouched: a decoupling capacitor keeps its distance to the pin
# it serves. Zones are chosen by x, with the few parts whose cluster straddles a
# boundary named explicitly.
ZONE_BOUNDS = (34.0, 56.0, 74.0, 93.0)
ZONE_SHIFTS = (0.0, 8.0, 20.0, 32.0, 44.0)
ZONE_OVERRIDES = {"R23": 2, "R31": 2, "C25": 3, "C26": 3}

# Left edge of the reserved back-copper region. It starts clear of the reader:
# a QFN-40 in 6 mm needs both faces to escape its pins, and covering it stranded
# its supplies. What the reserve protects is the path after the escape, the EMC
# filter, the match and the run to the matrix connector.
RF_KEEPOUT_LEFT = 122.0


def _zone_of(reference: str, x: float) -> int:
    if reference in ZONE_OVERRIDES:
        return ZONE_OVERRIDES[reference]
    return sum(1 for bound in ZONE_BOUNDS if x >= bound)


def _spread(placements: dict[str, Placement]) -> dict[str, Placement]:
    return {
        reference: Placement(
            Position(
                placement.position.x + ZONE_SHIFTS[_zone_of(reference, placement.position.x)],
                placement.position.y,
            ),
            rotation=placement.rotation,
            back=placement.back,
        )
        for reference, placement in placements.items()
    }


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
        "R34": Placement(Position(10.0, 6.5), rotation=90.0),
        "R35": Placement(Position(12.4, 6.5), rotation=90.0),
        "U2": Placement(Position(19.0, 23.0)),
        "U1": Placement(Position(29.0, 23.0)),
        # Input decoupling under the VBUS spine that runs between the comparator
        # and the switch. Left in the capacitor block below, these two sat 9 mm
        # off that spine: poor decoupling, and the one net the router could not
        # close on two layers.
        "C13": Placement(Position(26.0, 26.8), rotation=90.0),
        "C16": Placement(Position(28.6, 26.8), rotation=90.0),
        # The module return uses an 8-pin Micro-Fit shell sized for the 10 W
        # path. Keep both power harnesses accessible along the bottom edge.
        "J2": Placement(Position(14.0, 42.5)),
        "J11": Placement(Position(37.0, 42.5)),
        "J3": Placement(Position(33.9, 36.0), rotation=180.0),
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
        "C38": Placement(Position(59.0, 26.0), rotation=90.0, back=True),
        "C39": Placement(Position(61.2, 26.0), rotation=90.0, back=True),
        "U6": Placement(Position(63.0, 12.0), rotation=90.0),
        # Reader.
        "U3": Placement(Position(84.0, 28.0)),
        # Beside the reader's CLK1 and CLK2 pins on its upper left edge, not
        # below the part: from under it the oscillator loop had to travel around
        # the package, and it was the one net the two-layer route could not
        # close. The 3225 courtyard is 4.20 x 3.50 mm, so it keeps 3.5 mm from
        # the resistors above it and 1.5 mm from the reader.
        "Y1": Placement(Position(76.0, 24.8)),
        "L3": Placement(Position(92.0, 24.0), rotation=90.0),
        "L4": Placement(Position(92.0, 30.0), rotation=90.0),
        # Edge connectors.
        "J4": Placement(Position(106.5, 23.0), rotation=270.0),
        "J5": Placement(Position(50.0, 42.5)),
        "J6": Placement(Position(64.0, 42.5)),
        "J7": Placement(Position(62.0, 3.5), rotation=180.0),
        "J8": Placement(Position(74.0, 3.5), rotation=180.0),
        "J9": Placement(Position(86.0, 3.5), rotation=180.0),
        "J10": Placement(Position(96.0, 3.5), rotation=180.0),
        "TP1": Placement(Position(59.0, 8.0), back=True),
        "TP2": Placement(Position(56.0, 8.0), back=True),
        "TP3": Placement(Position(49.0, 8.0), back=True),
        # Cell voltage divider, above the module and clear of its courtyard, so
        # the high-impedance tap reaches U4 pin 9 without crossing the board.
        "R32": Placement(Position(67.5, 17.5), rotation=90.0),
        "R33": Placement(Position(69.7, 17.5), rotation=90.0),
        "C18": Placement(Position(71.9, 17.5), rotation=90.0),
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
    # C14, C15 and C17 belong to the switch output and the ADC tap. C13 and C16
    # decouple the switch input and are placed with it above, not here.
    placements.update(_grid(("C14", "C15", "C17"), (24.0, 30.0), 3, (3.6, 3.8), 90.0))
    # Buck and protected LED rail support.
    placements.update(_grid(("C1", "C2", "C3", "C4"), (39.0, 32.5), 2, (4.0, 3.8), 90.0))
    # The 3V3 bleeder sits with the output capacitors it discharges, and the
    # light-bar data pulldown with the buffer and connectors it defines.
    placements.update(_grid(("R36",), (47.0, 36.3), 1, (2.2, 3.4), 90.0))
    placements.update(_grid(("R37",), (57.0, 25.0), 1, (2.2, 3.4), 90.0))
    placements.update(_grid(("C10", "C11", "C6"), (48.0, 10.0), 3, (2.6, 3.4), 90.0))
    # MCU support: strapping, I2C, button, latch resistors.
    placements.update(
        _grid(("R20", "R21", "R22", "R23", "R24", "R25", "R26", "R31"), (69.0, 10.5), 4, (2.2, 3.4), 90.0)
    )
    # Reader supplies and crystal loads along the top, front end at the right.
    placements.update(
        _grid(("C20", "C21", "C22", "C23", "C24", "C25", "C26"), (76.0, 42.5), 7, (3.4, 2.2))
    )
    # Crystal loads and series resistors follow the crystal to the reader's
    # clock pins, keeping the oscillator loop on one side of the package.
    placements.update(_grid(("C31", "C32"), (74.5, 19.0), 2, (3.4, 2.2)))
    placements.update(_grid(("R27", "R28"), (74.5, 21.3), 2, (3.4, 2.2)))
    return _spread(placements)


def generate_board(output: Path = OUTPUT / "hub.kicad_pcb") -> None:
    netlist = read_netlist(OUTPUT / "hub.net")
    builder = BoardBuilder(netlist, board_thickness_mm=1.0)
    builder.board.GetDesignSettings().m_CopperEdgeClearance = pcbnew.FromMM(0.25)
    # The stock GCT USB-C footprint holds 0.19 mm between its own mechanical
    # holes and its shield pads; that geometry is routinely fabricated, so the
    # default 0.25 mm hole clearance is relaxed rather than the footprint edited.
    builder.board.GetDesignSettings().m_HoleClearance = pcbnew.FromMM(0.15)
    builder.add_outline(BOARD_WIDTH, BOARD_HEIGHT)
    # Keep the back copper solid under the reader, its match and the matrix
    # connector, so the 13.56 MHz return is a plane rather than whatever the
    # router leaves between traces. The strip above y=40 and below y=10 stays
    # routable, which is how the top-edge service connectors still reach the MCU.
    builder.add_keepout(
        pcbnew.B_Cu,
        (
            Position(RF_KEEPOUT_LEFT, 10.0),
            Position(BOARD_WIDTH - 6.0, 10.0),
            Position(BOARD_WIDTH - 6.0, 40.0),
            Position(RF_KEEPOUT_LEFT, 40.0),
        ),
    )
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
    # The receptacle's four shield pads share one pad number, spelled SH in
    # some footprint-library releases and S1 in others.
    shield_pads = sorted(
        builder.pad_positions("J1", "SH") or builder.pad_positions("J1", "S1"),
        key=lambda point: (point.y, point.x),
    )
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
    comparator_supply = builder.pad_position("U2", "8")
    comparator_supply_via = Position(comparator_supply.x + 1.0, comparator_supply.y)
    builder.add_track("USB_VBUS", (comparator_supply, comparator_supply_via), 0.25)
    builder.add_via("USB_VBUS", comparator_supply_via, diameter=0.6, drill=0.3)
    builder.add_track(
        "USB_VBUS",
        (comparator_supply_via, vbus_window_via),
        0.25,
        pcbnew.B_Cu,
    )
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
    # U1's input capacitors sit below its right edge. Escape pin 5 outside the
    # package before turning down, then join both capacitors with one short
    # branch. This is the power switch input loop, not a router-dependent
    # signal route.
    switch_input = builder.pad_position("U1", "5")
    input_capacitor = builder.pad_position("C16", "1")
    bulk_input = builder.pad_position("C13", "1")
    builder.add_via("USB_VBUS", bulk_input, diameter=0.6, drill=0.3)
    builder.add_track(
        "USB_VBUS",
        (comparator_supply_via, bulk_input),
        0.25,
        pcbnew.B_Cu,
    )
    input_escape_x = switch_input.x + 1.2
    builder.add_track(
        "USB_VBUS",
        (
            switch_input,
            Position(input_escape_x, switch_input.y),
            Position(input_escape_x, input_capacitor.y),
            input_capacitor,
            bulk_input,
        ),
        0.5,
    )
    # The comparator supply branch and the reader-to-MCU SCLK bridge used to be
    # drawn here. Both were workarounds for a four-layer route that could not
    # close them, and on two layers they would have to run on the back copper,
    # slotting the ground the RF front end returns through. The board is long
    # enough now for the router to close them on the front face instead.
    # No free-standing stitching vias. With four layers a via anywhere landed in
    # a pour on some layer; with two, the front pour is fragmented by the signals
    # it carries, so a via in the wrong place connects on one layer only. The two
    # pours tie together through the ground pads of the parts themselves, which
    # are spread across the whole board.
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
    apply_session(board, session_path.read_text(encoding="utf-8"))
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
    board.BuildConnectivity()
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            _close_pad(board, pad)



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


# The unrouted export is an external placement and routing job (Quilter), and
# a placer starts from intent, not from a finished floor plan: whatever the
# enclosure or the 13.56 MHz physics pins down stays fixed, everything else is
# parked below the outline for the placer to position. Fixed by name are the
# connectors, the mounting holes, and the parts the code-laid pre-routes in
# generate_board are drawn to; fixed by position is the reader region, from
# the reader supply row rightward.
PREROUTE_FIXED = frozenset({"U1", "U2", "R3", "R4", "R5", "R12", "C12", "C13", "C16"})
RF_FIXED_LEFT = 100.0


def _park_free_components(board_path: Path) -> None:
    board = pcbnew.LoadBoard(str(board_path))
    x, y = 4.0, BOARD_HEIGHT + 8.0
    for footprint in sorted(board.GetFootprints(), key=lambda f: f.GetReference()):
        reference = footprint.GetReference()
        if (
            reference[0] in "JH"
            or reference in PREROUTE_FIXED
            or pcbnew.ToMM(footprint.GetPosition().x) >= RF_FIXED_LEFT
        ):
            continue
        footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        x += 8.0
        if x > BOARD_WIDTH:
            x, y = 4.0, y + 10.0
    if not pcbnew.SaveBoard(str(board_path), board):
        raise OSError(f"could not save {board_path}")


if __name__ == "__main__":
    if "--unrouted" in sys.argv:
        unrouted = OUTPUT / "hub-unrouted.kicad_pcb"
        generate_board(unrouted)
        _park_free_components(unrouted)
    else:
        generate_board()
        if "--route" in sys.argv or "--reroute" in sys.argv:
            route_board(reroute="--reroute" in sys.argv)
