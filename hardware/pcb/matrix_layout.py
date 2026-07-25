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
from dataclasses import dataclass
from pathlib import Path

import pcbnew

from hardware.pcb.layout import BoardBuilder, Placement, Position
from hardware.pcb.matrix_geometry import (
    BOARD_SIZE,
    LINE_COUNT,
    MOUNTING_HOLE_SIZE,
    PLAY_ORIGIN,
    PLAY_SPAN,
    line_center,
    mounting_hole_positions,
)
from hardware.pcb.netlist import read_netlist
from hardware.pcb.ses_import import apply_session


OUTPUT = Path(__file__).parent / "generated" / "matrix"
FREEROUTING_JAR = os.environ.get("FREEROUTING_JAR", "/tmp/freerouting-2.2.4.jar")
# 25, not 12: the selection lines into U2's left column are the last the router
# finishes and it plateaus on them below this. 40 quadrupled the runtime for no
# further gain.
FREEROUTING_PASSES = int(os.environ.get("FREEROUTING_PASSES", "25"))

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


def _shift_footprint(builder: BoardBuilder, reference: str, dx: float) -> None:
    footprint = builder.footprints[reference]
    position = footprint.GetPosition()
    footprint.SetPosition(pcbnew.VECTOR2I(position.x + pcbnew.FromMM(dx), position.y))


def _seat_inside_left_edge(builder: BoardBuilder, reference: str, margin: float) -> float:
    """Shift a footprint right until all of it clears the board edge.

    U1's placement used to be a bare 3.5 mm, which put its pads 8 and 9 at
    x = -1.245: entirely off the board. Pad 9 is SEL_CHAIN, and a pad outside the
    outline is a pad Freerouting cannot reach, which is why `make
    pcb-matrix-route` failed on exactly that net while the other three serial
    nets routed. Pads 7 and 10 landed 0.025 mm from the edge against a 0.2 mm
    rule, the same bug one pin further in.

    Measured on the courtyard, not the pads: seating pad 8 at the margin still
    left the body and its silkscreen hanging over the edge, because a SOIC's
    outline is drawn wider than its pad field.

    Deriving the offset from the footprint rather than naming a number means
    neither fault can come back if the footprint or rotation changes. Same
    verify-and-correct approach as _check_column_antennas below.
    """
    footprint = builder.footprints[reference]
    courtyard = footprint.GetCourtyard(pcbnew.B_CrtYd)
    if courtyard.IsEmpty():
        courtyard = footprint.GetCourtyard(pcbnew.F_CrtYd)
    leftmost = float(pcbnew.ToMM(courtyard.BBox().GetLeft()))
    shift = margin - leftmost
    if shift <= 0.0:
        return 0.0
    _shift_footprint(builder, reference, shift)
    return shift


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
    # C65 is U1's decoupling capacitor, so it follows U1 rather than being
    # placed against a separate number that would drift out of step.
    _shift_footprint(builder, "C65", _seat_inside_left_edge(builder, "U1", U1_EDGE_MARGIN))
    for index, (x, y) in enumerate(mounting_hole_positions(), start=1):
        builder.add_mounting_hole(
            "GND", Position(x, y), f"H{index}", size=MOUNTING_HOLE_SIZE
        )
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
# Clearance from the board edge to U1's leftmost pad. 0.35 mm sits comfortably
# over the board's 0.2 mm copper-to-edge rule.
U1_EDGE_MARGIN = 0.35
# The reserved lane band starts above J1's 3V3 escape via (which sits at y 8.5)
# and extends just past U1's serial pad row: a negative gap. Without that the
# router runs 3V3 across the pad row on front copper, through where the lanes
# leave their pads. Stopping short of the row was tried and is worse: it frees
# 3V3 but splits the ground pour into islands.
_LANE_BAND_BOTTOM = 9.5
_LANE_BAND_GAP_TO_U1 = -0.6
# Slack either side of the outermost serial pad, so a 0.25 mm lane plus its
# clearance fits inside the band.
_LANE_BAND_SLACK = 0.6


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
# The serial pins whose verticals the band has to protect: QH' out, SHCP, STCP,
# and DS in.
U1_SERIAL_PADS = ("9", "11", "12", "14")
# The nets those pins carry, which _postroute_fixups owns end to end.
SHARED_SERIAL_NETS = ("SEL_CHAIN", "SEL_SRCLK", "SEL_RCLK", "SEL_SER")
# Lane geometry for the deterministic fan-out. See _serial_plan.
_LANE_WIDTH = 0.25
_LANE_VIA = 0.4
_LANE_DRILL = 0.2
# Lanes get their own pitch rather than sitting on their U1 pad x. U1's pins are
# on 1.27 mm and J1's on 1.25 mm, so lanes placed at the pads interleave with
# J1's pads about 0.44 mm away, against the 0.525 mm a 0.4 mm tap via needs from
# a 0.25 mm lane. This pitch keeps every lane at least 0.55 mm from every J1 pad
# (which sit at x 3.25, 4.50 and 5.75).
_LANE_X0 = 1.2
_LANE_PITCH = 1.3
_JOG_DROP = 3.0
# Crossing band below U2, one lane per net.
_CROSS_Y0 = 1.2
_CROSS_PITCH = 1.0
# Turn-up x, assigned by U2 pad y ascending so each final leg into U2 passes
# below the turn-ups of the nets stopping short of it. The net reaching U2's
# highest pad would need a vertical tall enough to cross every other final leg,
# so it goes around the far side of U2 and comes back in from the right.
_TURN_X0 = 156.5
_TURN_PITCH = 1.0
_TURN_X_FAR = 159.5
# Tap rows: lowest y clear of J1's pad band, then 0.6 mm apart so two
# adjacent back-copper taps keep their 0.2 mm clearance.
_TAP_MIN_Y = 3.0
_TAP_PITCH = 0.7
_CROSS_BAND = (0.6, 0.9, 151.5, 5.0)
# J1's serial pins come off the connector in a different order than U1's, so a
# single-layer fan-out cannot satisfy both: whichever way the crossing band is
# ordered, one tap has to cut another net's lane. The taps therefore drop onto
# J1 on back copper, and this window reserves that. It spans only J1's three
# serial pads: its GND, RF_BUS and 3V3 pins sit at x 7.0 and beyond, so they
# keep their back-copper escape.
_J1_TAP_BAND = (2.0, 1.3, 6.6, 5.0)
# Turn-up column: covers turn_x 155.5 to 159.5 and every U2 serial pad y.
_TURN_BAND = (154.9, 0.9, 156.9, 8.0)
# The far turn rounds U2 on its right, so it needs its own strip beyond the
# pad column rather than a band swallowing it.
_TURN_BAND_FAR = (159.0, 0.9, 160.1, 8.0)


@dataclass(frozen=True)
class SerialLane:
    net: str
    pad: tuple[float, float]
    lane_x: float
    cross_y: float
    turn_x: float


def _u1_lane_band(builder: BoardBuilder) -> tuple[float, float, float, float]:
    """The front-copper band reserved for U1's serial verticals.

    Derived from where U1's serial pads actually ended up rather than hardcoded,
    so it keeps covering them after _seat_inside_left_edge moves the part.
    """
    footprint = builder.footprints["U1"]
    pads = [pad for pad in footprint.Pads() if pad.GetNumber() in U1_SERIAL_PADS]
    xs = [pcbnew.ToMM(pad.GetPosition().x) for pad in pads]
    row_y = min(pcbnew.ToMM(pad.GetPosition().y) for pad in pads)
    return (
        min(xs) - _LANE_BAND_SLACK,
        _LANE_BAND_BOTTOM,
        max(xs) + _LANE_BAND_SLACK,
        row_y - _LANE_BAND_GAP_TO_U1,
    )


def _add_corridor_keepouts(builder: BoardBuilder) -> None:
    bands = (
        (*_u1_lane_band(builder), ("F.Cu",)),
        (*_CROSS_BAND, ("F.Cu",)),
        (*_TURN_BAND, ("F.Cu",)),
        (*_TURN_BAND_FAR, ("F.Cu",)),
        (*_J1_TAP_BAND, ("B.Cu",)),
    )
    for x1, y1, x2, y2, layers in bands:
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
        if (ax, ay) == (bx, by) and alayer == blayer:
            continue
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


def _rip_up(board: pcbnew.BOARD, net_names: tuple[str, ...]) -> None:
    """Delete every routed track and via on these nets."""
    for track in list(board.Tracks()):
        if track.GetNetname() in net_names:
            board.Remove(track)


def _serial_plan(board: pcbnew.BOARD) -> tuple[SerialLane, ...]:
    """Assign each shared serial net a lane x, a crossing y, and a turn-up x.

    Three orderings, each earning its place:

    * lanes keep the U1 pad order, so the verticals down the left margin are
      parallel and cannot cross;
    * crossing y rises with lane x, so each horizontal passes below the lane
      verticals of every net to its right;
    * turn-up x falls as the U2 pad y rises, so each final leg into U2 passes
      below the turn-ups of the nets stopping short of it. The net reaching U2's
      highest pad cannot satisfy that against the others, since its vertical
      would be tall enough to cut them, so it rounds the far side of U2 instead.

    Taps get their own rows on top of this; see _tap_rows.
    """
    pads = {
        board.FindFootprintByReference("U1").FindPadByNumber(number).GetNetname(): _pad_mm(
            board, "U1", number
        )
        for number in U1_SERIAL_PADS
    }
    far_pads = {
        net: _pad_mm(board, "U2", number)
        for net in pads
        for number in (_pad_of(board, net, "U2"),)
        if number is not None
    }
    by_pad_y = sorted(far_pads, key=lambda net: far_pads[net][1])
    turn_x = {net: _TURN_X0 - i * _TURN_PITCH for i, net in enumerate(by_pad_y[:-1])}
    turn_x[by_pad_y[-1]] = _TURN_X_FAR
    return tuple(
        SerialLane(
            net=net,
            pad=pads[net],
            lane_x=_LANE_X0 + index * _LANE_PITCH,
            cross_y=_CROSS_Y0 + index * _CROSS_PITCH,
            turn_x=turn_x.get(net, 0.0),
        )
        for index, net in enumerate(sorted(pads, key=lambda net: pads[net][0]))
    )


def _tap_rows(board: pcbnew.BOARD, plan: tuple[SerialLane, ...]) -> dict[str, float]:
    """The y at which each J1 tap leaves its lane for back copper.

    Ordered by how far right the hop reaches, which is deliberately not the lane
    ordering. SEL_SRCLK runs rightward from a lane left of its pin, SEL_RCLK
    leftward from a lane right of its pin, so the two hops overlap and the one
    reaching further has to sit below the other. Sharing the lanes' crossing rows
    put them in exactly the wrong order and crossed them.

    Rows are floored clear of J1's own pad band (y 0.8 to 2.5) so a tap via never
    lands on a neighbouring pin, and spaced so two adjacent hops keep clearance.
    """
    taps = {
        lane.net: lane for lane in plan if _pad_of(board, lane.net, "J1") is not None
    }
    reach = {
        net: max(lane.lane_x, _pad_mm(board, "J1", str(_pad_of(board, net, "J1")))[0])
        for net, lane in taps.items()
    }
    rows: dict[str, float] = {}
    floor = _TAP_MIN_Y
    for net in sorted(reach, key=lambda name: reach[name]):
        rows[net] = max(taps[net].cross_y, floor)
        floor = rows[net] + _TAP_PITCH
    return rows


def _postroute_fixups(board: pcbnew.BOARD) -> None:
    """Draw the four shared serial nets deterministically.

    Freerouting reaches U1's and U2's 0.65 mm serial pins unreliably, leaving a
    different one of these four bare on each run, so anything derived from where
    it stopped varied run to run. Three skip heuristics were measured and all
    left the board sometimes clean and sometimes not, because the problem sits
    upstream of the heuristic. These nets are therefore taken away from the
    router: its copper is ripped up and the paths drawn from measured pad
    positions, which is what makes the layout reproducible.
    """
    _rip_up(board, SHARED_SERIAL_NETS)
    plan = _serial_plan(board)
    tap_rows = _tap_rows(board, plan)
    for lane in plan:
        _via(board, lane.net, *lane.pad)
        nodes: list[tuple[float, float, str]] = [(*lane.pad, "F.Cu")]
        if abs(lane.lane_x - lane.pad[0]) > 1e-6:
            nodes.append((lane.lane_x, lane.pad[1] - _JOG_DROP, "F.Cu"))
        nodes.append((lane.lane_x, lane.cross_y, "F.Cu"))
        far = _pad_of(board, lane.net, "U2")
        if far is not None:
            far_x, far_y = _pad_mm(board, "U2", far)
            _route_waypoints(
                board, lane.net,
                tuple(nodes) + (
                    (lane.turn_x, lane.cross_y, "F.Cu"),
                    (lane.turn_x, far_y, "F.Cu"),
                    (far_x, far_y, "F.Cu"),
                ),
                width=_LANE_WIDTH,
            )
            _via(board, lane.net, far_x, far_y)
        tap = _pad_of(board, lane.net, "J1")
        if tap is None:
            continue
        if far is None:
            _route_waypoints(board, lane.net, tuple(nodes), width=_LANE_WIDTH)
        j1_x, j1_y = _pad_mm(board, "J1", tap)
        # Drop further down the lane's own x first, then hop on back copper. The
        # drop is on the net's own lane so it can never conflict, and it buys the
        # tap a row of its own: hopping at the lane's foot forced every tap to
        # share the lane ordering, which is the wrong one for them (see
        # _tap_rows). The hop itself has to be back copper, because on front
        # copper it would run the length of every lane between it and its pin.
        _route_waypoints(
            board, lane.net,
            (
                (lane.lane_x, lane.cross_y, "F.Cu"),
                (lane.lane_x, tap_rows[lane.net], "F.Cu"),
                (lane.lane_x, tap_rows[lane.net], "B.Cu"),
                (j1_x, tap_rows[lane.net], "B.Cu"),
                (j1_x, j1_y, "B.Cu"),
            ),
            width=_LANE_WIDTH, via_diameter=_LANE_VIA, via_drill=_LANE_DRILL,
        )


def _pad_of(board: pcbnew.BOARD, net_name: str, reference: str = "U1") -> str | None:
    footprint = board.FindFootprintByReference(reference)
    for pad in footprint.Pads():
        if pad.GetNetname() == net_name:
            return str(pad.GetNumber())
    return None


def _via(board: pcbnew.BOARD, net_name: str, x: float, y: float) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(pcbnew.VECTOR2I_MM(x, y))
    via.SetWidth(pcbnew.FromMM(_LANE_VIA))
    via.SetDrill(pcbnew.FromMM(_LANE_DRILL))
    via.SetNet(board.FindNet(net_name))
    board.Add(via)


def _nearest_net_point(
    board: pcbnew.BOARD, net_name: str, point: tuple[float, float]
) -> tuple[float, float]:
    """Nearest endpoint of the net's routed copper to point.

    Falls back to the net's own pads when the router left it bare. Freerouting
    skips one of the four serial nets fairly often, and which one varies run to
    run, so raising here turned an imperfect board into a failed build: the
    matrix could not be regenerated from code at all. A lane drawn to the
    counterpart pad is a worse route than one drawn to router copper, but it is
    a route, and DRC then gets to judge it instead of the script aborting.
    """
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
        for footprint in board.GetFootprints():
            for pad in footprint.Pads():
                if pad.GetNetname() != net_name:
                    continue
                position = pad.GetPosition()
                candidate = (pcbnew.ToMM(position.x), pcbnew.ToMM(position.y))
                distance = (candidate[0] - point[0]) ** 2 + (candidate[1] - point[1]) ** 2
                if distance < best_d:
                    best_d = distance
                    best = candidate
    if best is None:
        raise ValueError(f"net {net_name} has neither routed copper nor pads")
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
