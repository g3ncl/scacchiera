"""Deterministic non-overlapping placement for generated KiCad schematics."""

from typing import Any

from skidl.geometry import Point, Tx
from skidl.schematics import place


def install_nonoverlap_placer() -> None:
    """Replace SKiDL's variable-cell grid, which overlaps mixed-size symbols."""

    def place_floating_parts(node: Any, parts: list[Any], **options: object) -> None:
        del node, options
        if not parts:
            return
        place.add_placement_bboxes(parts)
        columns = max(1, int(len(parts) ** 0.5))
        cell_width = max(part.place_bbox.w for part in parts) + 400
        cell_height = max(part.place_bbox.h for part in parts) + 400
        for index, part in enumerate(parts):
            row, column = divmod(index, columns)
            part.tx = Tx().move(Point(column * cell_width, row * cell_height))

    place.Placer.place_floating_parts = place_floating_parts
