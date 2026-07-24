import csv
from pathlib import Path

from hardware.pcb.fab import JLC_CPL_COLUMNS, fitted_references, write_jlc_cpl


def test_write_jlc_cpl_uses_jlcpcb_headers(tmp_path: Path) -> None:
    source = tmp_path / "board.pos.csv"
    destination = tmp_path / "board_cpl.csv"
    bom = tmp_path / "board_bom.csv"
    source.write_text(
        "Ref,Val,Package,PosX,PosY,Rot,Side\n"
        '"C1","100n","C_0402",12.500000,-7.250000,90.000000,top\n'
        '"C2","DNP","C_0402",14.500000,-7.250000,90.000000,top\n',
        encoding="utf-8",
    )
    bom.write_text(
        "Comment,Designator,Footprint,MPN,Fitted,Quantity,Unit EUR,Line EUR\n"
        "100n,C1,C_0402,CL05B104KO5NNNC,yes,1,0.003,0.003\n"
        "DNP,C2,C_0402,,DNP,1,0.000,0.000\n",
        encoding="utf-8",
    )

    write_jlc_cpl(source, destination, fitted_references(bom))

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
