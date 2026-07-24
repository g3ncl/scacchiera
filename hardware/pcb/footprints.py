"""Generate the project footprints that are not in the KiCad libraries."""

from itertools import pairwise
from pathlib import Path

from hardware.pcb.matrix_geometry import (
    LOOP_BREADTH,
    LOOP_LENGTH,
    LOOP_TRACE_WIDTH,
    TERMINAL_GAP,
)


OUTPUT = Path(__file__).parent / "generated" / "footprints" / "Chessboard.pretty"

# The terminals sit on short tails outside the loop so they land in the margin,
# over the ground pour, clear of the play area's antenna copper.
TERMINAL_TAIL = 3.5


def _line_primitives(points: tuple[tuple[float, float], ...], anchor: tuple[float, float]) -> str:
    lines: list[str] = []
    for start, end in pairwise(points):
        lines.append(
            "      (gr_line "
            f"(start {start[0] - anchor[0]:.3f} {start[1] - anchor[1]:.3f}) "
            f"(end {end[0] - anchor[0]:.3f} {end[1] - anchor[1]:.3f}) "
            f"(width {LOOP_TRACE_WIDTH:.3f}))"
        )
    return "\n".join(lines)


def antenna_line_footprint() -> str:
    half_length = LOOP_LENGTH / 2.0
    half_breadth = LOOP_BREADTH / 2.0
    half_gap = TERMINAL_GAP / 2.0
    terminal_a = (-half_length - TERMINAL_TAIL, -half_gap)
    terminal_b = (-half_length - TERMINAL_TAIL, half_gap)
    # One conductor from terminal A around the lane and back to terminal B; the
    # gap between the two tails is the feed. The return stops 1.1 mm short of
    # terminal B's center: its copper still overlaps the pad ring (net tie) but
    # stays clear of the drill per the hole-clearance rule.
    path = (
        terminal_a,
        (-half_length, -half_gap),
        (-half_length, -half_breadth),
        (half_length, -half_breadth),
        (half_length, half_breadth),
        (-half_length, half_breadth),
        (-half_length, half_gap),
        (terminal_b[0] + 1.1, half_gap),
    )
    courtyard_left = terminal_a[0] - 0.5
    return f'''(footprint "Antenna_Line"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Single-turn line antenna loop for one row or column lane")
  (tags "NFC antenna net tie")
  (property "Reference" "REF**" (at 0 {-half_breadth - 2:.1f} 0) (layer "F.SilkS"))
  (property "Value" "Antenna_Line" (at 0 {half_breadth + 2:.1f} 0) (layer "F.Fab"))
  (attr smd)
  (net_tie_pad_groups "1,2")
  (fp_rect (start {courtyard_left:.3f} {-half_breadth - 1:.3f}) (end {half_length + 1:.3f} {half_breadth + 1:.3f}) (stroke (width 0.1) (type default)) (fill none) (layer "F.CrtYd"))
  (pad "1" smd custom (at {terminal_a[0]:.3f} {terminal_a[1]:.3f}) (size {LOOP_TRACE_WIDTH:.3f} {LOOP_TRACE_WIDTH:.3f}) (layers "F.Cu")
    (options (clearance outline) (anchor circle))
    (primitives
{_line_primitives(path, terminal_a)}
    ))
  (pad "1" thru_hole circle (at {terminal_a[0]:.3f} {terminal_a[1]:.3f}) (size 1.6 1.6) (drill 0.5) (layers "*.Cu" "*.Mask"))
  (pad "2" thru_hole circle (at {terminal_b[0]:.3f} {terminal_b[1]:.3f}) (size 1.6 1.6) (drill 0.5) (layers "*.Cu" "*.Mask"))
)\n'''


def esp32_footprint() -> str:
    pads: list[str] = []
    for number in range(1, 12):
        y = -3.3 + (number - 1) * 0.8
        pads.append(f'  (pad "{number}" smd rect (at -5.9 {y:.1f} 90) (size 0.4 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    for number in range(12, 25):
        x = -4.8 + (number - 12) * 0.8
        pads.append(f'  (pad "{number}" smd rect (at {x:.1f} 5.6) (size 0.4 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    for number in range(25, 36):
        y = 4.7 - (number - 25) * 0.8
        pads.append(f'  (pad "{number}" smd rect (at 5.9 {y:.1f} 90) (size 0.4 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    for number in range(36, 49):
        x = 4.8 - (number - 36) * 0.8
        pads.append(f'  (pad "{number}" smd rect (at {x:.1f} -4.2) (size 0.4 0.8) (layers "F.Cu" "F.Paste" "F.Mask"))')
    for x, y in ((-1.975, 0.7), (0.0, 0.7), (1.975, 0.7), (-1.975, 2.675), (0.0, 2.675), (1.975, 2.675), (0.0, -1.275), (1.975, -1.275)):
        pads.append(f'  (pad "49" smd rect (at {x:.3f} {y:.3f}) (size 1.45 1.45) (layers "F.Cu" "F.Paste" "F.Mask") (zone_connect 2))')
    pads.append('''  (pad "49" smd custom (at -1.975 -1.275) (size 0.8 0.8) (layers "F.Cu" "F.Paste" "F.Mask")
    (zone_connect 2) (options (clearance outline) (anchor rect))
    (primitives (gr_poly (pts (xy 0.725 0.725) (xy -0.725 0.725) (xy -0.725 -0.125) (xy -0.125 -0.725) (xy 0.725 -0.725)) (width 0) (fill yes))))''')
    for number, x, y in ((50, 5.95, -4.25), (51, 5.95, 5.65), (52, -5.95, 5.65), (53, -5.95, -4.25)):
        pads.append(f'  (pad "{number}" smd rect (at {x:.2f} {y:.2f}) (size 0.7 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))')
    return '''(footprint "ESP32-C3-MINI-1U"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Espressif ESP32-C3-MINI-1U recommended land pattern")
  (tags "ESP32-C3")
  (property "Reference" "REF**" (at 0 -7.05 0) (layer "F.SilkS"))
  (property "Value" "ESP32-C3-MINI-1U" (at 0 7.85 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -6.6 -6.2) (end 6.6 6.3) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -6.7 -6.3) (end 6.7 6.4) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
''' + "\n".join(pads) + "\n)\n"


def write_footprints(output: Path = OUTPUT) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "Antenna_Line.kicad_mod").write_text(antenna_line_footprint(), encoding="utf-8")
    (output / "ESP32-C3-MINI-1U.kicad_mod").write_text(esp32_footprint(), encoding="utf-8")


if __name__ == "__main__":
    write_footprints()
