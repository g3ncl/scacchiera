"""Export JLCPCB fabrication and assembly files from a routed board.

Runs entirely through `kicad-cli`, so it uses whatever board already sits in
`generated/<board>/<board>.kicad_pcb` rather than regenerating it.
"""

import csv
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

KICAD_CLI = "/usr/bin/kicad-cli"
GENERATED = Path(__file__).parent / "generated"
BOARDS = ("lightbar", "matrix", "hub")

GERBER_LAYERS = (
    "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
)

JLC_CPL_COLUMNS = ("Designator", "Mid X", "Mid Y", "Rotation", "Layer")


def fitted_references(bom_path: Path) -> frozenset[str]:
    """Read the fitted designators from the project's engineering BOM."""
    with bom_path.open(encoding="utf-8", newline="") as bom_file:
        reader = csv.DictReader(bom_file)
        required_columns = {"Designator", "Fitted"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{bom_path} is not a project BOM export")
        return frozenset(
            reference
            for row in reader
            if row["Fitted"] == "yes"
            for reference in row["Designator"].split(",")
        )


def write_jlc_cpl(
    source: Path, destination: Path, fitted: frozenset[str]
) -> None:
    """Convert KiCad's placement export to JLCPCB's required CPL layout."""
    with source.open(encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)
        required_columns = {"Ref", "PosX", "PosY", "Rot", "Side"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{source} is not a KiCad CSV placement export")
        rows = tuple(reader)

    with destination.open("w", encoding="utf-8", newline="") as destination_file:
        writer = csv.DictWriter(destination_file, fieldnames=JLC_CPL_COLUMNS)
        writer.writeheader()
        for row in rows:
            if row["Ref"] not in fitted:
                continue
            writer.writerow(
                {
                    "Designator": row["Ref"],
                    "Mid X": row["PosX"],
                    "Mid Y": row["PosY"],
                    "Rotation": row["Rot"],
                    "Layer": row["Side"].title(),
                }
            )


def export_fab(name: str) -> Path:
    board_dir = GENERATED / name
    pcb_file = board_dir / f"{name}.kicad_pcb"
    if not pcb_file.exists():
        raise SystemExit(f"{pcb_file} does not exist, generate and route the board first")

    fab_dir = board_dir / "fab"
    if fab_dir.exists():
        shutil.rmtree(fab_dir)
    fab_dir.mkdir(parents=True)

    subprocess.run(
        [
            KICAD_CLI, "pcb", "export", "gerbers",
            "--output", str(fab_dir),
            "--layers", GERBER_LAYERS,
            str(pcb_file),
        ],
        check=True,
    )
    subprocess.run(
        [
            KICAD_CLI, "pcb", "export", "drill",
            "--output", str(fab_dir),
            "--format", "excellon",
            "--drill-origin", "absolute",
            "--excellon-zeros-format", "decimal",
            "--excellon-units", "mm",
            "--excellon-separate-th",
            str(pcb_file),
        ],
        check=True,
    )

    gerber_files = sorted(p for p in fab_dir.iterdir() if p.suffix != ".csv")
    zip_path = board_dir / f"{name}_gerbers.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for gerber_file in gerber_files:
            archive.write(gerber_file, arcname=gerber_file.name)

    raw_cpl_path = fab_dir / f"{name}.pos.csv"
    cpl_path = board_dir / f"{name}_cpl.csv"
    subprocess.run(
        [
            KICAD_CLI, "pcb", "export", "pos",
            "--output", str(raw_cpl_path),
            "--format", "csv",
            "--units", "mm",
            "--side", "both",
            "--exclude-dnp",
            str(pcb_file),
        ],
        check=True,
    )
    write_jlc_cpl(raw_cpl_path, cpl_path, fitted_references(board_dir / f"{name}_bom.csv"))

    shutil.rmtree(fab_dir)
    return zip_path


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in BOARDS:
        raise SystemExit(f"Usage: python -m hardware.pcb.fab {{{'|'.join(BOARDS)}}}")
    zip_path = export_fab(sys.argv[1])
    print(f"gerbers: {zip_path}")


if __name__ == "__main__":
    main()
