"""Merge the per-board hand-fit BOMs into one purchase list.

The upload pairs are what the factory places; everything an iron can reach is
bought separately and fitted by hand. This folds the four per-board
self-solder BOMs into a single order for the whole build (four sensing quads,
two light bars, one hub, one power board) and suggests a purchase quantity on
top of the fitted count: passives round up generously because hand-fitting
0402s loses parts and nobody sells eleven resistors; everything else gets two
spares. The one line with no LCSC code, the light-bar LED, is a DigiKey
purchase (docs/hardware/jlcpcb-sourcing.md).
"""

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
OUTPUT = PCB_DIR / "generated" / "self_solder_order.csv"

# Boards populated in one complete build. The fifth quad and the spare light
# bars stay bare.
BUILD = {"quad": 4, "lightbar": 2, "hub": 1, "power": 1}

PASSIVE_HINTS = ("0402", "0603", "0805", "1206", "1210", "SOD")


@dataclass
class Line:
    comment: str
    mpn: str
    lcsc: str
    footprint: str
    needed: int = 0
    boards: dict[str, int] = field(default_factory=dict)


def order_quantity(needed: int, footprint: str) -> int:
    if any(hint in footprint for hint in PASSIVE_HINTS):
        return max(10, math.ceil(needed * 1.3 / 10) * 10)
    return needed + 2


def main() -> None:
    lines: dict[str, Line] = {}
    for board, count in BUILD.items():
        path = PCB_DIR / "generated" / board / f"{board}_self_solder_bom.csv"
        if not path.is_file():
            raise SystemExit(f"{path} is missing; run make pcb-fab first")
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = row["LCSC Part #"] or row["MPN"]
                line = lines.setdefault(
                    key,
                    Line(row["Comment"], row["MPN"], row["LCSC Part #"], row["Footprint"]),
                )
                fitted = int(row["Quantity"]) * count
                line.needed += fitted
                line.boards[board] = line.boards.get(board, 0) + fitted
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ("Comment", "MPN", "LCSC Part #", "Source", "Fitted", "Order", "Fitted per board")
        )
        for line in sorted(lines.values(), key=lambda entry: (not entry.lcsc, entry.comment)):
            source = "LCSC" if line.lcsc else "DigiKey"
            spread = ", ".join(f"{board} {qty}" for board, qty in sorted(line.boards.items()))
            writer.writerow(
                (
                    line.comment,
                    line.mpn,
                    line.lcsc,
                    source,
                    line.needed,
                    order_quantity(line.needed, line.footprint),
                    spread,
                )
            )
    total = sum(line.needed for line in lines.values())
    print(f"{OUTPUT}: {len(lines)} purchase lines, {total} fitted parts")


if __name__ == "__main__":
    main()
