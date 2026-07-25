"""Apply a Specctra session's routed wires and vias to a KiCad board.

pcbnew's ImportSpecctraSES intermittently rejects sessions Freerouting emits,
reporting only False. The session's wire and via records are plain
s-expressions, so this applies them directly and deterministically, reusing
the project's existing parser. Runs under the system interpreter (pcbnew),
stdlib plus this repo only.
"""

import re

import pcbnew

from hardware.pcb.netlist import SExpr, parse_sexpr, sexpr_children


# Session coordinates are tenths of micrometers ((resolution um 10)), with the
# y axis flipped relative to the board.
_MM_DIVISOR = 10000.0
_VIA_PADSTACK = re.compile(r"Via\[[^\]]*\]_(\d+):(\d+)_um")


def _mm(token: SExpr) -> float:
    if not isinstance(token, str):
        raise ValueError(f"expected coordinate token, got {token!r}")
    return float(token) / _MM_DIVISOR


def _point(x_token: SExpr, y_token: SExpr) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I_MM(_mm(x_token), -_mm(y_token))


def apply_session(
    board: pcbnew.BOARD,
    session_text: str,
    excluded_nets: frozenset[str] = frozenset(),
    net_aliases: dict[str, str] | None = None,
) -> int:
    """Add every routed wire segment and via from the session; returns the
    number of items added."""
    root = parse_sexpr(session_text)
    if not isinstance(root, list) or not root or root[0] != "session":
        raise ValueError("not a Specctra session")
    routes = sexpr_children(root, "routes")[0]
    resolution = sexpr_children(routes, "resolution")[0]
    if resolution[1:3] != ["um", "10"]:
        raise ValueError(f"unexpected session resolution: {resolution}")
    # The session echoes pre-routed fixed wiring back; skip anything already
    # on the board so vias are not doubled into co-located holes.
    existing_vias = {
        (item.GetPosition().x, item.GetPosition().y)
        for item in board.Tracks()
        if item.Type() == pcbnew.PCB_VIA_T
    }
    existing_segments = {
        (item.GetStart().x, item.GetStart().y, item.GetEnd().x, item.GetEnd().y, item.GetLayer())
        for item in board.Tracks()
        if item.Type() == pcbnew.PCB_TRACE_T
    }
    added = 0
    network = sexpr_children(routes, "network_out")[0]
    for net_expr in sexpr_children(network, "net"):
        net_name = net_expr[1]
        if not isinstance(net_name, str):
            raise ValueError(f"unnamed net in session: {net_expr[:2]}")
        if net_name in excluded_nets:
            continue
        if net_aliases is not None:
            net_name = net_aliases.get(net_name, net_name)
        net = board.FindNet(net_name)
        if net is None:
            raise ValueError(f"session net not on board: {net_name}")
        for wire in sexpr_children(net_expr, "wire"):
            for path in sexpr_children(wire, "path"):
                layer_token, width_token = path[1], path[2]
                if not isinstance(layer_token, str):
                    raise ValueError(f"bad layer in path: {layer_token!r}")
                layer = board.GetLayerID(layer_token)
                coordinates = path[3:]
                points = [
                    _point(coordinates[index], coordinates[index + 1])
                    for index in range(0, len(coordinates) - 1, 2)
                ]
                for start, end in zip(points[:-1], points[1:]):
                    if start == end:
                        continue
                    key = (start.x, start.y, end.x, end.y, layer)
                    reverse_key = (end.x, end.y, start.x, start.y, layer)
                    if key in existing_segments or reverse_key in existing_segments:
                        continue
                    segment = pcbnew.PCB_TRACK(board)
                    segment.SetLayer(layer)
                    segment.SetWidth(pcbnew.FromMM(_mm(width_token) if isinstance(width_token, str) else 0.2))
                    segment.SetNet(net)
                    segment.SetStart(start)
                    segment.SetEnd(end)
                    board.Add(segment)
                    added += 1
        for via_expr in sexpr_children(net_expr, "via"):
            padstack = via_expr[1]
            if not isinstance(padstack, str):
                raise ValueError(f"bad via padstack: {padstack!r}")
            match = _VIA_PADSTACK.search(padstack)
            if match is None:
                raise ValueError(f"unrecognized via padstack: {padstack}")
            position = _point(via_expr[2], via_expr[3])
            if (position.x, position.y) in existing_vias:
                continue
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(position)
            via.SetWidth(pcbnew.FromMM(int(match.group(1)) / 1000.0))
            via.SetDrill(pcbnew.FromMM(int(match.group(2)) / 1000.0))
            via.SetNet(net)
            board.Add(via)
            added += 1
    return added
