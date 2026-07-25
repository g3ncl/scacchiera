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
LEGACY_ASSEMBLY_SUFFIXES = (
    "_bom.csv",
    "_cpl.csv",
    "_jlc_bom.csv",
    "_jlc_cpl.csv",
)

GERBER_LAYERS = (
    "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"
)

JLC_CPL_COLUMNS = ("Designator", "Mid X", "Mid Y", "Rotation", "Layer")
JLC_BOM_COLUMNS = ("Comment", "Designator", "Footprint", "LCSC Part #")
HAND_BOM_COLUMNS = (
    "Comment", "Designator", "Footprint", "MPN", "LCSC Part #", "JLC Library",
    "Quantity", "Hand Method", "Assembly Reason",
)
NON_ASSEMBLED_MPNS = frozenset({"PCB_COPPER"})
HAND_ASSEMBLY_ROUTES = frozenset({"Hand"})


def _is_assembled(row: dict[str, str], excluded_routes: frozenset[str] = frozenset()) -> bool:
    return (
        row["Fitted"] == "yes"
        and row["MPN"] not in NON_ASSEMBLED_MPNS
        and row.get("Assembly Route", "") not in excluded_routes
    )


def assembly_references(
    bom_path: Path, excluded_routes: frozenset[str] = frozenset()
) -> frozenset[str]:
    """Read the purchased assembly designators from the engineering BOM."""
    with bom_path.open(encoding="utf-8", newline="") as bom_file:
        reader = csv.DictReader(bom_file)
        required_columns = {"Designator", "MPN", "Fitted"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{bom_path} is not a project BOM export")
        return frozenset(
            reference
            for row in reader
            if _is_assembled(row, excluded_routes)
            for reference in row["Designator"].split(",")
        )


def write_jlc_bom(
    source: Path, destination: Path, excluded_routes: frozenset[str] = frozenset()
) -> None:
    """Convert the engineering BOM into JLCPCB's assembly BOM layout."""
    with source.open(encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)
        required_columns = {*JLC_BOM_COLUMNS, "MPN", "Fitted"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{source} is not a project BOM export")
        rows = tuple(row for row in reader if _is_assembled(row, excluded_routes))

    with destination.open("w", encoding="utf-8", newline="") as destination_file:
        writer = csv.DictWriter(destination_file, fieldnames=JLC_BOM_COLUMNS)
        writer.writeheader()
        writer.writerows(
            {
                "Comment": row["MPN"],
                "Designator": row["Designator"],
                "Footprint": row["Footprint"],
                "LCSC Part #": row["LCSC Part #"],
            }
            for row in rows
        )


def write_hand_bom(source: Path, destination: Path) -> None:
    """Write the externally sourced parts recommended for manual fitting."""
    with source.open(encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)
        required_columns = {*HAND_BOM_COLUMNS, "Fitted", "Assembly Route"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{source} is not an assembly-classified project BOM export")
        rows = tuple(
            {column: row[column] for column in HAND_BOM_COLUMNS}
            for row in reader
            if _is_assembled(row) and row["Assembly Route"] == "Hand"
        )

    with destination.open("w", encoding="utf-8", newline="") as destination_file:
        writer = csv.DictWriter(destination_file, fieldnames=HAND_BOM_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


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


def validate_assembly_designators(bom_path: Path, cpl_path: Path) -> None:
    """Require the upload BOM and CPL to describe the same fitted parts."""
    with bom_path.open(encoding="utf-8", newline="") as bom_file:
        bom_references = {
            reference
            for row in csv.DictReader(bom_file)
            for reference in row["Designator"].split(",")
        }
    with cpl_path.open(encoding="utf-8", newline="") as cpl_file:
        cpl_references = {row["Designator"] for row in csv.DictReader(cpl_file)}
    if bom_references != cpl_references:
        missing_from_cpl = sorted(bom_references - cpl_references)
        missing_from_bom = sorted(cpl_references - bom_references)
        raise ValueError(
            "JLCPCB BOM/CPL designator mismatch: "
            f"BOM only={missing_from_cpl}, CPL only={missing_from_bom}"
        )


def export_fab(name: str) -> tuple[Path, Path, Path, Path, Path, Path]:
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
    cpl_path = board_dir / f"{name}_jlcpcb_cpl.csv"
    engineering_bom_path = board_dir / f"{name}_engineering_bom.csv"
    bom_path = board_dir / f"{name}_jlcpcb_bom.csv"
    hybrid_bom_path = board_dir / f"{name}_jlcpcb_hybrid_bom.csv"
    hybrid_cpl_path = board_dir / f"{name}_jlcpcb_hybrid_cpl.csv"
    hand_bom_path = board_dir / f"{name}_hand_bom.csv"
    for suffix in LEGACY_ASSEMBLY_SUFFIXES:
        (board_dir / f"{name}{suffix}").unlink(missing_ok=True)
    write_jlc_bom(engineering_bom_path, bom_path)
    write_jlc_bom(engineering_bom_path, hybrid_bom_path, HAND_ASSEMBLY_ROUTES)
    write_hand_bom(engineering_bom_path, hand_bom_path)
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
    write_jlc_cpl(raw_cpl_path, cpl_path, assembly_references(engineering_bom_path))
    write_jlc_cpl(
        raw_cpl_path,
        hybrid_cpl_path,
        assembly_references(engineering_bom_path, HAND_ASSEMBLY_ROUTES),
    )
    validate_assembly_designators(bom_path, cpl_path)
    validate_assembly_designators(hybrid_bom_path, hybrid_cpl_path)

    shutil.rmtree(fab_dir)
    return zip_path, bom_path, cpl_path, hybrid_bom_path, hybrid_cpl_path, hand_bom_path


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in BOARDS:
        raise SystemExit(f"Usage: python -m hardware.pcb.fab {{{'|'.join(BOARDS)}}}")
    zip_path, bom_path, cpl_path, hybrid_bom_path, hybrid_cpl_path, hand_bom_path = export_fab(
        sys.argv[1]
    )
    print(f"gerbers: {zip_path}")
    print(f"JLCPCB BOM: {bom_path}")
    print(f"JLCPCB CPL: {cpl_path}")
    print(f"hybrid JLCPCB BOM: {hybrid_bom_path}")
    print(f"hybrid JLCPCB CPL: {hybrid_cpl_path}")
    print(f"hand assembly BOM: {hand_bom_path}")


if __name__ == "__main__":
    main()
