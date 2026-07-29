"""Combine the two light bars and the power board into one fabricated panel.

Three small boards ordered separately pay three minimum quantities and three
setup charges. Ordered as one panel they pay one, and the panel is above the
outline JLCPCB will assemble, which the 120 by 8.5 mm light bar on its own is
not. The boards are joined by mouse-bite tabs and snapped apart after delivery.

The panel is generated from the routed boards rather than drawn: each is loaded,
translated into place, and appended whole, so a panel can never disagree with
the board it came from. Re-run it after any board changes.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import pcbnew


GENERATED = Path(__file__).parent / "generated"
OUTPUT = GENERATED / "panel"

# Gap between neighbouring boards. Wide enough for the router bit that cuts the
# slots between them, which JLCPCB specifies at 1.6 mm minimum for routed edges.
GUTTER_MM = 2.0

# Panel border, so the fabricator has material to hold and to rail-mount.
BORDER_MM = 5.0

# Mouse bites: a row of small drills across the gutter. The web left between
# them snaps by hand and files flat. 0.5 mm holes on a 1.0 mm pitch is the
# common compromise between snapping cleanly and holding during assembly.
BITE_DRILL_MM = 0.5
BITE_PITCH_MM = 1.0
BITES_PER_TAB = 5
TAB_WIDTH_MM = BITE_PITCH_MM * (BITES_PER_TAB - 1)


@dataclass(frozen=True)
class Placement:
    """One board's origin inside the panel."""

    board: str
    x_mm: float
    y_mm: float


def _board_extent(board: pcbnew.BOARD) -> tuple[float, float]:
    box = board.GetBoardEdgesBoundingBox()
    return pcbnew.ToMM(box.GetWidth()), pcbnew.ToMM(box.GetHeight())


def placements() -> tuple[Placement, ...]:
    """Two bars stacked above the power board, all left-aligned.

    The bars are 120 mm long and the power board 46 mm, so stacking rather than
    tiling keeps the panel at the bars' length instead of three times it.
    """
    lightbar_height = 8.5
    return (
        Placement("lightbar", BORDER_MM, BORDER_MM),
        Placement("lightbar", BORDER_MM, BORDER_MM + lightbar_height + GUTTER_MM),
        Placement(
            "power", BORDER_MM, BORDER_MM + 2.0 * (lightbar_height + GUTTER_MM)
        ),
    )


def _duplicate(item: pcbnew.BOARD_ITEM) -> pcbnew.BOARD_ITEM:
    """Copy one board item.

    KiCad 10 gives FOOTPRINT.Duplicate an addToParentGroup argument that the
    BOARD_ITEM overload does not take, so the call is tried both ways rather
    than branching on a type list that would go stale.
    """
    try:
        return item.Duplicate(False)
    except TypeError:
        return item.Duplicate()


def _translate_and_append(
    panel: pcbnew.BOARD, source: pcbnew.BOARD, offset: pcbnew.VECTOR2I, suffix: str
) -> None:
    """Copy one board into the panel, moved to its place and uniquely named."""
    for footprint in source.GetFootprints():
        # Duplicate returns a base item, so it is cast back before the
        # footprint-only calls below.
        copy = pcbnew.Cast_to_FOOTPRINT(_duplicate(footprint))
        copy.Move(offset)
        # References repeat across the two identical bars, so each copy is
        # suffixed. A panel with two J1 pads confuses assembly and DRC alike.
        copy.SetReference(f"{footprint.GetReference()}{suffix}")
        panel.Add(copy)
    for track in source.GetTracks():
        copy = _duplicate(track)
        copy.Move(offset)
        panel.Add(copy)
    for drawing in source.GetDrawings():
        copy = _duplicate(drawing)
        copy.Move(offset)
        panel.Add(copy)
    for zone in source.Zones():
        copy = _duplicate(zone)
        copy.Move(offset)
        panel.Add(copy)


def _add_edge(panel: pcbnew.BOARD, start: tuple[float, float], end: tuple[float, float]) -> None:
    segment = pcbnew.PCB_SHAPE(panel)
    segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
    segment.SetLayer(pcbnew.Edge_Cuts)
    segment.SetWidth(pcbnew.FromMM(0.05))
    segment.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(start[0]), pcbnew.FromMM(start[1])))
    segment.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(end[0]), pcbnew.FromMM(end[1])))
    panel.Add(segment)


def _add_mouse_bites(panel: pcbnew.BOARD, tab: int, centre_x: float, centre_y: float) -> None:
    """Drill a snap line across one tab, centred on the gutter.

    The holes are non-plated. Emitted as vias they would be plated barrels with
    no annular ring, which is both wrong and a DRC violation; a mouse bite is
    bare drilled material meant to break.
    """
    carrier = pcbnew.FOOTPRINT(panel)
    carrier.SetReference(f"MB{tab}")
    carrier.Reference().SetVisible(False)
    carrier.Value().SetVisible(False)
    carrier.SetPosition(
        pcbnew.VECTOR2I(pcbnew.FromMM(centre_x), pcbnew.FromMM(centre_y))
    )
    drill = pcbnew.FromMM(BITE_DRILL_MM)
    for index in range(BITES_PER_TAB):
        offset = (index - (BITES_PER_TAB - 1) / 2.0) * BITE_PITCH_MM
        hole = pcbnew.PAD(carrier)
        hole.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        hole.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        hole.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_CIRCLE)
        hole.SetSize(pcbnew.VECTOR2I(drill, drill))
        hole.SetDrillSize(pcbnew.VECTOR2I(drill, drill))
        hole.SetLayerSet(hole.UnplatedHoleMask())
        hole.SetPosition(
            pcbnew.VECTOR2I(
                pcbnew.FromMM(centre_x + offset), pcbnew.FromMM(centre_y)
            )
        )
        carrier.Add(hole)
    panel.Add(carrier)


def build_panel(output: Path = OUTPUT / "panel.kicad_pcb") -> None:
    panel = pcbnew.BOARD()
    panel.SetCopperLayerCount(2)
    panel.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.0))
    # The panel inherits the boards' own edge rule. Left at the 0.5 mm default
    # it would fail pours that already passed on the board they came from.
    panel.GetDesignSettings().m_CopperEdgeClearance = pcbnew.FromMM(0.25)

    widths: list[float] = []
    heights: list[float] = []
    for index, placement in enumerate(placements()):
        source = pcbnew.LoadBoard(
            str(GENERATED / placement.board / f"{placement.board}.kicad_pcb")
        )
        box = source.GetBoardEdgesBoundingBox()
        # Boards are drawn from their own origin; subtract it so the placement
        # coordinate means the same thing for every board.
        offset = pcbnew.VECTOR2I(
            pcbnew.FromMM(placement.x_mm) - box.GetLeft(),
            pcbnew.FromMM(placement.y_mm) - box.GetTop(),
        )
        _translate_and_append(panel, source, offset, f"_{index + 1}")
        width, height = _board_extent(source)
        widths.append(placement.x_mm + width)
        heights.append(placement.y_mm + height)

    panel_width = max(widths) + BORDER_MM
    panel_height = max(heights) + BORDER_MM
    for start, end in (
        ((0.0, 0.0), (panel_width, 0.0)),
        ((panel_width, 0.0), (panel_width, panel_height)),
        ((panel_width, panel_height), (0.0, panel_height)),
        ((0.0, panel_height), (0.0, 0.0)),
    ):
        _add_edge(panel, start, end)

    # A snap line in each gutter, at both ends of the boards so a bar is held
    # at two points rather than cantilevered from one.
    tab = 0
    for placement, width in zip(placements()[1:], widths[1:], strict=True):
        gutter_y = placement.y_mm - GUTTER_MM / 2.0
        for tab_x in (placement.x_mm + 15.0, width - 15.0):
            tab += 1
            _add_mouse_bites(panel, tab, tab_x, gutter_y)

    output.parent.mkdir(parents=True, exist_ok=True)
    if not pcbnew.SaveBoard(str(output), panel):
        raise OSError(f"could not save panel {output}")
    print(f"panel {panel_width:.1f} x {panel_height:.1f} mm -> {output}")


def main() -> None:
    build_panel()


if __name__ == "__main__":
    main()
    sys.exit(0)
