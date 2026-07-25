"""BOM export with a running cost total, per the Milestone 2 definition of done."""

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from skidl import Circuit


@dataclass(frozen=True)
class BomKey:
    value: str
    footprint: str
    mpn: str
    lcsc_part: str
    fitted: str
    unit_cost_eur: float


def _key(part: object) -> BomKey:
    return BomKey(
        str(getattr(part, "value", "")),
        str(getattr(part, "footprint", "")),
        str(getattr(part, "manf_num", "")),
        str(getattr(part, "lcsc_part", "")),
        str(getattr(part, "fitted", "yes")),
        float(getattr(part, "unit_cost_eur", 0.0)),
    )


def fitted_cost_eur(circuit: Circuit) -> float:
    return sum(
        float(getattr(part, "unit_cost_eur", 0.0))
        for part in circuit.parts
        if str(getattr(part, "fitted", "yes")) == "yes"
    )


def write_bom(circuit: Circuit, destination: Path) -> None:
    grouped: dict[BomKey, list[str]] = defaultdict(list)
    for part in circuit.parts:
        grouped[_key(part)].append(str(part.ref))
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as bom_file:
        writer = csv.writer(bom_file)
        writer.writerow(
            (
                "Comment", "Designator", "Footprint", "MPN", "LCSC Part #", "Fitted",
                "Quantity", "Unit EUR", "Line EUR",
            )
        )
        for key, references in sorted(grouped.items(), key=lambda item: item[1][0]):
            line_cost = key.unit_cost_eur * len(references) if key.fitted == "yes" else 0.0
            writer.writerow(
                (
                    key.value,
                    ",".join(references),
                    key.footprint,
                    key.mpn,
                    key.lcsc_part,
                    key.fitted,
                    len(references),
                    f"{key.unit_cost_eur:.3f}",
                    f"{line_cost:.3f}",
                )
            )
        writer.writerow(("TOTAL", "", "", "", "", "", "", "", f"{fitted_cost_eur(circuit):.3f}"))


def missing_manufacturer_parts(circuit: Circuit) -> tuple[str, ...]:
    missing = [
        str(part.ref)
        for part in circuit.parts
        if getattr(part, "fitted", "yes") == "yes" and not getattr(part, "manf_num", "")
    ]
    return tuple(sorted(missing))
