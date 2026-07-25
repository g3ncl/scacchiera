import csv
from pathlib import Path

from hardware.pcb.fab import (
    HAND_ASSEMBLY_ROUTES,
    HAND_BOM_COLUMNS,
    JLC_BOM_COLUMNS,
    JLC_CPL_COLUMNS,
    assembly_references,
    validate_assembly_designators,
    write_hand_bom,
    write_jlc_bom,
    write_jlc_cpl,
)


def test_write_jlc_cpl_uses_jlcpcb_headers(tmp_path: Path) -> None:
    source = tmp_path / "board.pos.csv"
    destination = tmp_path / "board_cpl.csv"
    bom = tmp_path / "board_bom.csv"
    source.write_text(
        "Ref,Val,Package,PosX,PosY,Rot,Side\n"
        '"C1","100n","C_0402",12.500000,-7.250000,90.000000,top\n'
        '"C2","DNP","C_0402",14.500000,-7.250000,90.000000,top\n'
        '"L1","PCB loop","Antenna_Line",16.500000,-7.250000,0.000000,bottom\n',
        encoding="utf-8",
    )
    bom.write_text(
        "Comment,Designator,Footprint,MPN,LCSC Part #,Fitted,Quantity,Unit EUR,Line EUR\n"
        "100n,C1,C_0402,CL05B104KO5NNNC,C1525,yes,1,0.003,0.003\n"
        "DNP,C2,C_0402,,,DNP,1,0.000,0.000\n"
        "PCB loop,L1,Antenna_Line,PCB_COPPER,,yes,1,0.000,0.000\n",
        encoding="utf-8",
    )

    write_jlc_cpl(source, destination, assembly_references(bom))

    with destination.open(encoding="utf-8", newline="") as cpl_file:
        rows = list(csv.DictReader(cpl_file))
    assert tuple(rows[0]) == JLC_CPL_COLUMNS
    assert rows == [
        {
            "Designator": "C1",
            "Mid X": "12.500000",
            "Mid Y": "-7.250000",
            "Rotation": "90.000000",
            "Layer": "Top",
        }
    ]


def test_write_jlc_bom_filters_dnp_parts(tmp_path: Path) -> None:
    source = tmp_path / "board_bom.csv"
    destination = tmp_path / "board_jlc_bom.csv"
    source.write_text(
        "Comment,Designator,Footprint,MPN,LCSC Part #,Fitted,Quantity,Unit EUR,Line EUR\n"
        "100n,C1,C_0402,CL05B104KO5NNNC,C1525,yes,1,0.003,0.003\n"
        "DNP,C2,C_0402,,,DNP,1,0.000,0.000\n"
        "PCB loop,L1,Antenna_Line,PCB_COPPER,,yes,1,0.000,0.000\n",
        encoding="utf-8",
    )

    write_jlc_bom(source, destination)

    with destination.open(encoding="utf-8", newline="") as bom_file:
        rows = list(csv.DictReader(bom_file))
    assert tuple(rows[0]) == JLC_BOM_COLUMNS
    assert rows == [
        {
            "Comment": "CL05B104KO5NNNC",
            "Designator": "C1",
            "Footprint": "C_0402",
            "LCSC Part #": "C1525",
        }
    ]


def test_hybrid_exports_split_hand_assembly_without_mismatching_cpl(tmp_path: Path) -> None:
    engineering = tmp_path / "engineering.csv"
    hybrid_bom = tmp_path / "hybrid_bom.csv"
    hand_bom = tmp_path / "hand_bom.csv"
    engineering.write_text(
        "Comment,Designator,Footprint,MPN,LCSC Part #,JLC Library,Fitted,Quantity,"
        "Assembly Route,Hand Method,Assembly Reason,Unit EUR,Line EUR\n"
        "100n,C1,C_0402,CL05B104KO5NNNC,C1525,Basic,yes,1,JLCPCB,Factory reflow,"
        "Basic placement,0.003,0.003\n"
        "connector,J1,JST_GH,A1257WR-S-4P,C225127,Extended,yes,1,Hand,Iron or hot air,"
        "Accessible pads,0.130,0.130\n",
        encoding="utf-8",
    )

    write_jlc_bom(engineering, hybrid_bom, HAND_ASSEMBLY_ROUTES)
    write_hand_bom(engineering, hand_bom)

    with hybrid_bom.open(encoding="utf-8", newline="") as bom_file:
        hybrid_rows = list(csv.DictReader(bom_file))
    with hand_bom.open(encoding="utf-8", newline="") as bom_file:
        hand_rows = list(csv.DictReader(bom_file))
    assert [row["Designator"] for row in hybrid_rows] == ["C1"]
    assert tuple(hand_rows[0]) == HAND_BOM_COLUMNS
    assert [row["Designator"] for row in hand_rows] == ["J1"]


def test_validate_assembly_designators_rejects_a_mismatch(tmp_path: Path) -> None:
    bom = tmp_path / "board_bom.csv"
    cpl = tmp_path / "board_cpl.csv"
    bom.write_text(
        "Comment,Designator,Footprint,LCSC Part #\n100n,C1,C_0402,C1525\n",
        encoding="utf-8",
    )
    cpl.write_text(
        "Designator,Mid X,Mid Y,Rotation,Layer\nC2,1,1,0,Top\n",
        encoding="utf-8",
    )

    try:
        validate_assembly_designators(bom, cpl)
    except ValueError as error:
        assert "BOM only=['C1'], CPL only=['C2']" in str(error)
    else:
        raise AssertionError("mismatched BOM/CPL designators were accepted")
