"""Generate the firmware's glyph table from readable art.

A hand-typed hex font is unreviewable: a wrong bit is invisible until it is on
a display. The glyphs below are drawn, so a mistake is visible in the diff, and
this script packs them into the column bytes the renderer wants.

5 by 7 in a 6 by 8 cell, which leaves one blank column and one blank row so
adjacent characters and lines do not touch. Coverage is space, digits, the
punctuation a clock and a status line need, and uppercase letters. Lowercase is
absent because nothing in docs/functional/ currently asks for it.
"""

from pathlib import Path


HEADER_PATH = Path(__file__).resolve().parent.parent / "core" / "font_glyphs.h"

GLYPH_WIDTH = 5
GLYPH_HEIGHT = 7
CELL_WIDTH = 6
CELL_HEIGHT = 8

# Each glyph is seven rows of five, top row first. "1" is a lit pixel.
GLYPHS: dict[str, list[str]] = {
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "%": ["11000", "11001", "00010", "00100", "01000", "10011", "00011"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    ",": ["00000", "00000", "00000", "00000", "00000", "00100", "01000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "10001", "11001", "10101", "10011", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
}

FIRST_CODE = 0x20
LAST_CODE = 0x5A


def _column_bytes(rows: list[str]) -> list[int]:
    """Pack a glyph into five column bytes, bit 0 the top row.

    Columns rather than rows because the renderer walks left to right across a
    horizontal window, so a column is the inner loop.
    """
    columns: list[int] = []
    for x in range(GLYPH_WIDTH):
        value = 0
        for y in range(GLYPH_HEIGHT):
            if rows[y][x] == "1":
                value |= 1 << y
        columns.append(value)
    return columns


def render() -> str:
    for character, rows in GLYPHS.items():
        if len(rows) != GLYPH_HEIGHT or any(len(row) != GLYPH_WIDTH for row in rows):
            raise ValueError(f"glyph {character!r} is not {GLYPH_WIDTH} by {GLYPH_HEIGHT}")

    lines = [
        "/* Generated by software/firmware/tools/generate_font.py.",
        " * Do not edit. The glyphs are drawn as art in that script so a wrong bit is",
        " * visible in review rather than only on a display.",
        " */",
        "#ifndef CHESSBOARD_CORE_FONT_GLYPHS_H",
        "#define CHESSBOARD_CORE_FONT_GLYPHS_H",
        "",
        "#include <stdint.h>",
        "",
        f"#define FONT_GLYPH_WIDTH {GLYPH_WIDTH}",
        f"#define FONT_GLYPH_HEIGHT {GLYPH_HEIGHT}",
        f"#define FONT_CELL_WIDTH {CELL_WIDTH}",
        f"#define FONT_CELL_HEIGHT {CELL_HEIGHT}",
        f"#define FONT_FIRST_CODE 0x{FIRST_CODE:02X}",
        f"#define FONT_LAST_CODE 0x{LAST_CODE:02X}",
        "",
        "/* Five column bytes per glyph, bit 0 the top row. Characters with no",
        " * drawn glyph are blank rather than absent, so rendering never has to",
        " * special-case an unknown byte. */",
        "static const uint8_t FONT_GLYPHS[FONT_LAST_CODE - FONT_FIRST_CODE + 1]"
        "[FONT_GLYPH_WIDTH] = {",
    ]
    for code in range(FIRST_CODE, LAST_CODE + 1):
        character = chr(code)
        rows = GLYPHS.get(character)
        columns = _column_bytes(rows) if rows else [0] * GLYPH_WIDTH
        packed = ", ".join(f"0x{value:02X}" for value in columns)
        label = "space" if character == " " else character
        lines.append(f"    {{{packed}}}, /* {label} */")
    lines += ["};", "", "#endif", ""]
    return "\n".join(lines)


def main() -> None:
    HEADER_PATH.write_text(render(), encoding="utf-8")
    print(f"wrote {HEADER_PATH}")


if __name__ == "__main__":
    main()
