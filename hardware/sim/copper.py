"""Extract routed copper from a generated .kicad_pcb as resistance data.

The SPICE validations read the board file, not the layout script, so the
simulated copper is exactly the copper that will be fabricated.
"""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from math import hypot
from pathlib import Path

from hardware.pcb.netlist import SExpr, parse_sexpr, sexpr_children, sexpr_value


# 1 oz copper on a standard stackup.
COPPER_THICKNESS_M = 35e-6
COPPER_RESISTIVITY_OHM_M = 1.72e-8


@dataclass(frozen=True)
class TrackSegment:
    net: str
    layer: str
    start: tuple[float, float]
    end: tuple[float, float]
    width_mm: float

    def resistance_ohm(self) -> float:
        length_m = hypot(self.end[0] - self.start[0], self.end[1] - self.start[1]) / 1000.0
        area_m2 = (self.width_mm / 1000.0) * COPPER_THICKNESS_M
        return COPPER_RESISTIVITY_OHM_M * length_m / area_m2


@dataclass(frozen=True)
class Via:
    net: str
    position: tuple[float, float]


@dataclass(frozen=True)
class Copper:
    segments: tuple[TrackSegment, ...]
    vias: tuple[Via, ...]


def split_at_junctions(
    segments: Iterable[TrackSegment], points: Iterable[tuple[float, float]]
) -> tuple[TrackSegment, ...]:
    """Split segments where another track ends on them mid-span.

    Routed copper joins at T-junctions, but a node graph built from raw
    endpoints only connects tracks that share an endpoint, so a branch meeting
    the middle of a bus would float electrically.
    """
    point_list = tuple(points)
    result: list[TrackSegment] = []
    for segment in segments:
        ax, ay = segment.start
        bx, by = segment.end
        length_sq = (bx - ax) ** 2 + (by - ay) ** 2
        if length_sq == 0.0:
            result.append(segment)
            continue
        cuts: list[tuple[float, tuple[float, float]]] = []
        for px, py in point_list:
            t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / length_sq
            if not 1e-9 < t < 1.0 - 1e-9:
                continue
            off = hypot(ax + t * (bx - ax) - px, ay + t * (by - ay) - py)
            if off < 1e-3:
                cuts.append((t, (px, py)))
        previous = segment.start
        for _, cut in sorted(cuts):
            result.append(replace(segment, start=previous, end=cut))
            previous = cut
        result.append(replace(segment, start=previous, end=segment.end))
    return tuple(result)


def _point(expression: list[SExpr], name: str) -> tuple[float, float]:
    child = sexpr_children(expression, name)[0]
    if len(child) < 3 or not isinstance(child[1], str) or not isinstance(child[2], str):
        raise ValueError(f"malformed {name}")
    return (float(child[1]), float(child[2]))


def read_copper(board: Path) -> Copper:
    root = parse_sexpr(board.read_text(encoding="utf-8"))
    if not isinstance(root, list) or not root or root[0] != "kicad_pcb":
        raise ValueError("not a KiCad board file")
    net_names = {
        net[1]: net[2]
        for net in sexpr_children(root, "net")
        if len(net) >= 3 and isinstance(net[1], str) and isinstance(net[2], str)
    }

    def net_of(expression: list[SExpr]) -> str:
        # KiCad 9 references nets by number; KiCad 10 writes the name inline.
        token = sexpr_value(expression, "net")
        return net_names.get(token, token)

    segments = tuple(
        TrackSegment(
            net=net_of(segment),
            layer=sexpr_value(segment, "layer"),
            start=_point(segment, "start"),
            end=_point(segment, "end"),
            width_mm=float(sexpr_value(segment, "width")),
        )
        for segment in sexpr_children(root, "segment")
    )
    vias = tuple(
        Via(net=net_of(via), position=_point(via, "at"))
        for via in sexpr_children(root, "via")
    )
    return Copper(segments=segments, vias=vias)
