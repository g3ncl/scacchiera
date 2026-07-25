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
    jlc_library: str
    fitted: str
    unit_cost_eur: float


@dataclass(frozen=True)
class AssemblyPlan:
    route: str
    hand_method: str
    reason: str


REFLOW_ONLY_FOOTPRINT_MARKERS = (
    "0402_1005Metric",
    "D_SOD-523",
    "DFN_QFN",
    "LED_WS2812B-2020",
    "R-PDSO-N6_DRL-6",
    "Texas_S-PVSON",
    "TSSOP-24",
    "USB_C_Receptacle",
    "ESP32-C3-MINI-1U",
    "Crystal_SMD_2016",
)


def _key(part: object) -> BomKey:
    return BomKey(
        str(getattr(part, "value", "")),
        str(getattr(part, "footprint", "")),
        str(getattr(part, "manf_num", "")),
        str(getattr(part, "lcsc_part", "")),
        str(getattr(part, "jlc_library", "Unbound")),
        str(getattr(part, "fitted", "yes")),
        float(getattr(part, "unit_cost_eur", 0.0)),
    )


def assembly_plan(key: BomKey, quantity: int, board_name: str = "") -> AssemblyPlan:
    """Choose a practical assembly route without changing what is fitted."""
    if key.fitted != "yes" or key.mpn == "PCB_COPPER":
        return AssemblyPlan("Omit", "None", "Not a fitted purchased component")
    if board_name == "lightbar":
        reflow_only = any(marker in key.footprint for marker in REFLOW_ONLY_FOOTPRINT_MARKERS)
        return AssemblyPlan(
            "Hand",
            "Stencil reflow" if reflow_only else "Iron or hot air",
            "The lightbar is below JLCPCB's supported assembly size",
        )
    if key.jlc_library == "Basic":
        return AssemblyPlan("JLCPCB", "Factory reflow", "Basic placement avoids an Extended fee")
    if any(marker in key.footprint for marker in REFLOW_ONLY_FOOTPRINT_MARKERS):
        return AssemblyPlan(
            "JLCPCB",
            "Stencil reflow only",
            "Hidden, fine-pitch, or very small pads make iron soldering risky",
        )
    if quantity >= 10:
        return AssemblyPlan(
            "JLCPCB",
            "Factory reflow",
            "Individually solderable, but the repeated quantity makes manual work error-prone",
        )
    return AssemblyPlan(
        "Hand",
        "Iron or hot air",
        "Low quantity and accessible pads make external purchase and manual fitting practical",
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
                "Comment", "Designator", "Footprint", "MPN", "LCSC Part #", "JLC Library",
                "Fitted", "Quantity", "Assembly Route", "Hand Method", "Assembly Reason",
                "Unit EUR", "Line EUR",
            )
        )
        for key, references in sorted(grouped.items(), key=lambda item: item[1][0]):
            line_cost = key.unit_cost_eur * len(references) if key.fitted == "yes" else 0.0
            plan = assembly_plan(key, len(references), circuit.name)
            writer.writerow(
                (
                    key.value,
                    ",".join(references),
                    key.footprint,
                    key.mpn,
                    key.lcsc_part,
                    key.jlc_library,
                    key.fitted,
                    len(references),
                    plan.route,
                    plan.hand_method,
                    plan.reason,
                    f"{key.unit_cost_eur:.3f}",
                    f"{line_cost:.3f}",
                )
            )
        writer.writerow(
            ("TOTAL", "", "", "", "", "", "", "", "", "", "", "", f"{fitted_cost_eur(circuit):.3f}")
        )


def missing_manufacturer_parts(circuit: Circuit) -> tuple[str, ...]:
    missing = [
        str(part.ref)
        for part in circuit.parts
        if getattr(part, "fitted", "yes") == "yes" and not getattr(part, "manf_num", "")
    ]
    return tuple(sorted(missing))
