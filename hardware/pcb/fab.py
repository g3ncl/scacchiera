"""Export JLCPCB fabrication and assembly files from a routed board.

Runs entirely through `kicad-cli`, so it uses whatever board already sits in
`generated/<board>/<board>.kicad_pcb` rather than regenerating it.
"""

import csv
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from hardware.pcb.bom import HAND_POPULATED_BOARDS

KICAD_CLI = "/usr/bin/kicad-cli"
GENERATED = Path(__file__).parent / "generated"
BOARDS = ("lightbar", "matrix", "hub", "power", "strip", "spine")
# Names this export has used before. Deleted on every run so a stale file from
# an older naming scheme cannot be uploaded by mistake.
LEGACY_ASSEMBLY_SUFFIXES = (
    "_bom.csv",
    "_cpl.csv",
    "_jlc_bom.csv",
    "_jlc_cpl.csv",
    "_jlcpcb_bom.csv",
    "_jlcpcb_cpl.csv",
    "_jlcpcb_hybrid_bom.csv",
    "_jlcpcb_hybrid_cpl.csv",
    "_hand_bom.csv",
    "_engineering_bom.csv",
)

GERBER_NON_COPPER_LAYERS = (
    "F.Paste", "B.Paste", "F.Silkscreen", "B.Silkscreen", "F.Mask", "B.Mask", "Edge.Cuts",
)
_COPPER_LAYER = re.compile(r'\(\d+ "([A-Za-z0-9]+\.Cu)" ')

JLC_CPL_COLUMNS = ("Designator", "Mid X", "Mid Y", "Rotation", "Layer")
JLC_BOM_COLUMNS = ("Comment", "Designator", "Footprint", "LCSC Part #")
HAND_BOM_COLUMNS = (
    "Comment", "Designator", "Footprint", "MPN", "LCSC Part #", "JLC Library",
    "Quantity", "Hand Method", "Assembly Reason",
)
NON_ASSEMBLED_MPNS = frozenset({"PCB_COPPER"})
HAND_ASSEMBLY_ROUTES = frozenset({"Hand"})


def copper_layers(pcb_file: Path) -> tuple[str, ...]:
    """Read the board's copper stack, in stack order, from its layer table.

    The hub is four layers while the other two are two, so a fixed layer list
    would silently ship Gerbers missing routed inner copper."""
    # The layer table precedes (setup, so cutting there keeps per-footprint
    # layer references out of the match.
    header = pcb_file.read_text(encoding="utf-8").split("(setup", maxsplit=1)[0]
    layers = tuple(dict.fromkeys(_COPPER_LAYER.findall(header)))
    if not layers:
        raise ValueError(f"{pcb_file} declares no copper layers")
    return layers


def gerber_layers(pcb_file: Path) -> str:
    return ",".join((*copper_layers(pcb_file), *GERBER_NON_COPPER_LAYERS))


def _is_assembled(row: dict[str, str], excluded_routes: frozenset[str] = frozenset()) -> bool:
    return (
        row["Fitted"] == "yes"
        and row["MPN"] not in NON_ASSEMBLED_MPNS
        and row.get("Assembly Route", "") not in excluded_routes
    )


def assembly_references(
    bom_path: Path,
    excluded_routes: frozenset[str] = frozenset(),
    *,
    ignore_routes: bool = False,
) -> frozenset[str]:
    """Read the purchased assembly designators from the engineering BOM.

    `ignore_routes` mirrors `write_jlc_bom`. The two have to agree exactly or
    `validate_assembly_designators` rejects the pair, which is what caught this
    when only the BOM side had been widened.
    """
    with bom_path.open(encoding="utf-8", newline="") as bom_file:
        reader = csv.DictReader(bom_file)
        required_columns = {"Designator", "MPN", "Fitted", "LCSC Part #"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{bom_path} is not a project BOM export")
        return frozenset(
            reference
            for row in reader
            if _is_assembled(row, frozenset() if ignore_routes else excluded_routes)
            and (row["LCSC Part #"] if ignore_routes else True)
            for reference in row["Designator"].split(",")
        )


def write_jlc_bom(
    source: Path,
    destination: Path,
    excluded_routes: frozenset[str] = frozenset(),
    *,
    ignore_routes: bool = False,
) -> None:
    """Convert the engineering BOM into JLCPCB's assembly BOM layout.

    `ignore_routes` takes every fitted part JLCPCB could place, whatever the
    board's chosen assembly route says. That is what the max-assembly pair is
    for: it prices the alternative to the plan, and on a hand-populated board
    the plan routes everything to Hand, so honouring it emitted a header and no
    rows. The lightbar and matrix files were empty for exactly that reason,
    against a sourcing doc that says they show what the alternative would cost.

    A part with no LCSC code is still excluded, because that one really cannot
    be factory placed rather than merely being planned otherwise.
    """
    with source.open(encoding="utf-8", newline="") as source_file:
        reader = csv.DictReader(source_file)
        required_columns = {*JLC_BOM_COLUMNS, "MPN", "Fitted"}
        if reader.fieldnames is None or not required_columns.issubset(reader.fieldnames):
            raise ValueError(f"{source} is not a project BOM export")
        rows = tuple(
            row
            for row in reader
            if _is_assembled(row, frozenset() if ignore_routes else excluded_routes)
            and (row["LCSC Part #"] if ignore_routes else True)
        )

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


def write_self_solder_bom(source: Path, destination: Path) -> None:
    """The parts you buy and fit yourself, not the ones JLCPCB places."""
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
            "--layers", gerber_layers(pcb_file),
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
    cpl_path = board_dir / f"{name}_jlcpcb_upload_cpl.csv"
    all_parts_bom_path = board_dir / f"{name}_bom_all_parts.csv"
    bom_path = board_dir / f"{name}_jlcpcb_upload_bom.csv"
    max_assembly_bom_path = board_dir / f"{name}_jlcpcb_max_assembly_bom.csv"
    max_assembly_cpl_path = board_dir / f"{name}_jlcpcb_max_assembly_cpl.csv"
    self_solder_bom_path = board_dir / f"{name}_self_solder_bom.csv"
    for suffix in LEGACY_ASSEMBLY_SUFFIXES:
        (board_dir / f"{name}{suffix}").unlink(missing_ok=True)
    standard_excluded_routes = (
        HAND_ASSEMBLY_ROUTES if name in HAND_POPULATED_BOARDS else frozenset()
    )
    write_jlc_bom(all_parts_bom_path, bom_path, standard_excluded_routes)
    hand_populated = name in HAND_POPULATED_BOARDS
    write_jlc_bom(all_parts_bom_path, max_assembly_bom_path, ignore_routes=True)
    write_self_solder_bom(all_parts_bom_path, self_solder_bom_path)
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
    write_jlc_cpl(
        raw_cpl_path,
        cpl_path,
        assembly_references(all_parts_bom_path, standard_excluded_routes),
    )
    write_jlc_cpl(
        raw_cpl_path,
        max_assembly_cpl_path,
        assembly_references(all_parts_bom_path, ignore_routes=True),
    )
    validate_assembly_designators(bom_path, cpl_path)
    validate_assembly_designators(max_assembly_bom_path, max_assembly_cpl_path)

    # A hand-populated board's upload pair is a header and no rows, and the
    # files are named `upload`, so the obvious thing to do with them is the one
    # thing that cannot work: JLCPCB answers a zero-part list with an opaque
    # HTTP 500. Delete them rather than ship a trap whose only warning is in a
    # document. Bare Gerbers are the order for these boards, and the
    # max-assembly pair is what prices the alternative.
    if hand_populated:
        bom_path.unlink(missing_ok=True)
        cpl_path.unlink(missing_ok=True)

    shutil.rmtree(fab_dir)
    return zip_path, bom_path, cpl_path, max_assembly_bom_path, max_assembly_cpl_path, self_solder_bom_path


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in BOARDS:
        raise SystemExit(f"Usage: python -m hardware.pcb.fab {{{'|'.join(BOARDS)}}}")
    zip_path, bom_path, cpl_path, max_assembly_bom_path, max_assembly_cpl_path, self_solder_bom_path = export_fab(
        sys.argv[1]
    )
    print(f"gerbers: {zip_path}")
    if bom_path.exists():
        print(f"JLCPCB upload BOM: {bom_path}")
        print(f"JLCPCB upload CPL: {cpl_path}")
    else:
        print(
            f"no upload pair: {sys.argv[1]} is hand populated, so order bare Gerbers.\n"
            "  To price factory assembly instead, upload the max-assembly pair below."
        )
    print(f"JLCPCB max-assembly BOM: {max_assembly_bom_path}")
    print(f"JLCPCB max-assembly CPL: {max_assembly_cpl_path}")
    print(f"self-solder BOM: {self_solder_bom_path}")


if __name__ == "__main__":
    main()
