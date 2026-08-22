"""Rendered review package for a board, per V7 in docs/simulation-workflow.md:
every copper, mask, paste, silkscreen and drill layer as its own image, plus
both 3D sides, so a reviewer looks at what the fab will build rather than at
the design source.

Runs entirely through `kicad-cli` against the board already sitting in
`generated/<board>/<board>.kicad_pcb`, exactly as fab.py does.
"""

import os
import subprocess
import sys
from pathlib import Path

KICAD_CLI = os.environ.get("KICAD_CLI", "/usr/bin/kicad-cli")
GENERATED = Path(__file__).resolve().parent / "generated"

BOARDS = ("lightbar", "matrix", "hub", "power", "quad")

# One image per fabrication layer. Edge cuts are drawn into every export so a
# layer is never reviewed without the outline it lives in.
LAYERS = (
    "F.Cu", "B.Cu",
    "F.Mask", "B.Mask",
    "F.Paste", "B.Paste",
    "F.Silkscreen", "B.Silkscreen",
    # Fab drawings carry each body's outline and pin-1 mark: the orientation
    # reference for the assembler's placement preview.
    "F.Fab", "B.Fab",
    "Edge.Cuts",
)


def run(args: list[str]) -> None:
    subprocess.run(args, check=True, capture_output=True)


def review(name: str) -> Path:
    board = GENERATED / name / f"{name}.kicad_pcb"
    if not board.is_file():
        raise SystemExit(f"{board} is missing; generate the board first")
    out = GENERATED / name / "review"
    out.mkdir(parents=True, exist_ok=True)

    for layer in LAYERS:
        run([
            KICAD_CLI, "pcb", "export", "svg", str(board),
            "--output", str(out / f"{layer.replace('.', '_')}.svg"),
            "--layers", f"{layer},Edge.Cuts",
            "--page-size-mode", "2",
            "--exclude-drawing-sheet",
        ])

    # The drill map is review evidence for the holes the gerber job carries.
    run([
        KICAD_CLI, "pcb", "export", "drill", str(board),
        "--output", str(out) + "/",
        "--format", "excellon",
        "--generate-map", "--map-format", "pdf",
    ])

    for side in ("top", "bottom"):
        run([
            KICAD_CLI, "pcb", "render", str(board),
            "--output", str(out / f"3d_{side}.png"),
            "--side", side,
            "--quality", "high",
            "--width", "1600", "--height", "900",
        ])
    return out


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in BOARDS:
        raise SystemExit(f"usage: review.py <{'|'.join(BOARDS)}>")
    out = review(sys.argv[1])
    count = len(list(out.iterdir()))
    print(f"review package: {count} files in {out}")


if __name__ == "__main__":
    main()
