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
    """ESP32-C6-MINI-1U land pattern.

    Geometry is shared with the C3-MINI-1U this replaced: datasheet v1.5
    section 10.1 gives the same 13.20 x 12.50 mm body and the same 53-pad
    layout, and the 1U has no antenna keepout zone. Only the pin functions
    differ, and those live in parts.esp32_c6_mini_1u.
    """
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
    return '''(footprint "ESP32-C6-MINI-1U"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Espressif ESP32-C6-MINI-1U recommended land pattern")
  (tags "ESP32-C6")
  (property "Reference" "REF**" (at 0 -7.05 0) (layer "F.SilkS"))
  (property "Value" "ESP32-C6-MINI-1U" (at 0 7.85 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -6.6 -6.2) (end 6.6 6.3) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -6.7 -6.3) (end 6.7 6.4) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
''' + "\n".join(pads) + "\n)\n"


def t37k3rgb_footprint() -> str:
    """Harvatek T37K3RGB land pattern from datasheet page 5."""
    pad_w, pad_h = 0.72, 1.15
    dx, dy = 0.74, 1.575
    corners = (("1", -1, -1), ("2", -1, 1), ("3", 1, 1), ("4", 1, -1))
    pads = [
        f'  (pad "{number}" smd roundrect (at {dx * sx:.3f} {dy * sy:.3f}) '
        f'(size {pad_w} {pad_h}) (layers "F.Cu" "F.Paste" "F.Mask") '
        f'(roundrect_rratio 0.25))'
        for number, sx, sy in corners
    ]
    return '''(footprint "T37K3RGB-05C000112U1930"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Harvatek T37K3RGB 5 mA addressable RGB LED")
  (tags "addressable LED RGB NeoPixel")
  (property "Reference" "REF**" (at 0 -2.8 0) (layer "F.SilkS"))
  (property "Value" "T37K3RGB-05C000112U1930" (at 0 2.8 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -1.4 -1.75) (end 1.4 1.75) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -1.65 -2.4) (end 1.65 2.4) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
  (fp_circle (center -1.5 -2.1) (end -1.4 -2.1) (stroke (width 0.2) (type default)) (fill none) (layer "F.SilkS"))
''' + "\n".join(pads) + "\n)\n"


def nr6045s_footprint() -> str:
    """Magnetsyc NR6045S land pattern from data sheet page 1."""
    return '''(footprint "NR6045S"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Magnetsyc NR6045S recommended land pattern")
  (tags "shielded power inductor")
  (property "Reference" "REF**" (at 0 -4.1 0) (layer "F.SilkS"))
  (property "Value" "NR6045S" (at 0 4.1 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -3 -3) (end 3 3) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -3.3 -3.3) (end 3.3 3.3) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
  (pad "1" smd roundrect (at -2.25 0) (size 1.7 5.7) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))
  (pad "2" smd roundrect (at 2.25 0) (size 1.7 5.7) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))
)\n'''


def dfe252012f_footprint() -> str:
    """Murata DFE252012F land pattern from the manufacturer series sheet."""
    return '''(footprint "DFE252012F"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Murata DFE252012F recommended land pattern")
  (tags "shielded metal-alloy power inductor")
  (property "Reference" "REF**" (at 0 -1.8 0) (layer "F.SilkS"))
  (property "Value" "DFE252012F" (at 0 1.8 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -1.25 -1) (end 1.25 1) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -1.65 -1.25) (end 1.65 1.25) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
  (pad "1" smd roundrect (at -1 0) (size 0.8 2) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))
  (pad "2" smd roundrect (at 1 0) (size 0.8 2) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))
)\n'''


def tlv7042_dgk_footprint() -> str:
    """TI DGK0008A land pattern from the TLV7042 data sheet."""
    pads = []
    for number, x, y in (
        (1, -1.5, -0.975), (2, -1.5, -0.325), (3, -1.5, 0.325), (4, -1.5, 0.975),
        (5, 1.5, 0.975), (6, 1.5, 0.325), (7, 1.5, -0.325), (8, 1.5, -0.975),
    ):
        pads.append(
            f'  (pad "{number}" smd roundrect (at {x} {y}) (size 1.4 0.45) '
            '(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))'
        )
    return '''(footprint "TLV7042_DGK"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Texas Instruments DGK0008A manufacturer land pattern")
  (tags "VSSOP-8 DGK")
  (property "Reference" "REF**" (at 0 -2.8 0) (layer "F.SilkS"))
  (property "Value" "TLV7042_DGK" (at 0 2.8 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -1.5 -1.5) (end 1.5 1.5) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -2.45 -1.75) (end 2.45 1.75) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
  (fp_circle (center -0.5 -1.15) (end -0.35 -1.15) (stroke (width 0.15) (type default)) (fill none) (layer "F.SilkS"))
''' + "\n".join(pads) + "\n)\n"


def sot563_drl_footprint() -> str:
    """TI DRL0006A land pattern from the TPS61023 data sheet.

    The stock SOT-563 footprint holds 0.15 mm between adjacent pads, under this
    project's 0.2 mm rule. TI's own pattern is 0.3 mm pads on the 0.5 mm pitch,
    which leaves exactly 0.2 mm, so the manufacturer geometry is the one that
    fits rather than a relaxed rule.
    """
    pads = []
    # Pins 1 to 3 down the left column, 4 to 6 up the right, per the data
    # sheet's pin configuration. Pad centres sit 0.405 mm either side, so the
    # pattern spans the 1.48 mm the drawing dimensions.
    for number, x, y in (
        (1, -0.405, -0.5), (2, -0.405, 0.0), (3, -0.405, 0.5),
        (4, 0.405, 0.5), (5, 0.405, 0.0), (6, 0.405, -0.5),
    ):
        pads.append(
            f'  (pad "{number}" smd roundrect (at {x} {y}) (size 0.67 0.3) '
            '(layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.15))'
        )
    return '''(footprint "SOT-563_DRL"
  (version 20240108)
  (generator pcbnew)
  (layer "F.Cu")
  (descr "Texas Instruments DRL0006A manufacturer land pattern")
  (tags "SOT-563 DRL")
  (property "Reference" "REF**" (at 0 -1.4 0) (layer "F.SilkS"))
  (property "Value" "SOT-563_DRL" (at 0 1.4 0) (layer "F.Fab"))
  (attr smd)
  (fp_rect (start -0.8 -0.6) (end 0.8 0.6) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
  (fp_rect (start -1.0 -0.85) (end 1.0 0.85) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
  (fp_circle (center -0.9 -0.75) (end -0.8 -0.75) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))
''' + "\n".join(pads) + "\n)\n"


def write_footprints(output: Path = OUTPUT) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "Antenna_Line.kicad_mod").write_text(antenna_line_footprint(), encoding="utf-8")
    (output / "ESP32-C6-MINI-1U.kicad_mod").write_text(esp32_footprint(), encoding="utf-8")
    (output / "T37K3RGB-05C000112U1930.kicad_mod").write_text(t37k3rgb_footprint(), encoding="utf-8")
    (output / "NR6045S.kicad_mod").write_text(nr6045s_footprint(), encoding="utf-8")
    (output / "DFE252012F.kicad_mod").write_text(dfe252012f_footprint(), encoding="utf-8")
    (output / "TLV7042_DGK.kicad_mod").write_text(tlv7042_dgk_footprint(), encoding="utf-8")
    (output / "SOT-563_DRL.kicad_mod").write_text(sot563_drl_footprint(), encoding="utf-8")


if __name__ == "__main__":
    write_footprints()
