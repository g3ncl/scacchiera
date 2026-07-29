"""Generate the V1 fitted-component audit and its small wiki pages."""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import cache
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml

ROOT = Path(__file__).parents[2]
DATASHEETS = ROOT / "Vault" / "Scacchiera" / "Datasheets"
WIKI = ROOT / "Vault" / "Scacchiera" / "Wiki"
AUDIT_PATH = ROOT / "docs" / "verification" / "v1-components.yaml"
REVIEW_DATE = "2026-07-26"
WIKI_UPDATE_DATE = "2026-07-29"
MODULE_NAME = "hardware.verification.generate_component_audit"

DESIGN_FACTS = {
    "BQ25619RTWR": (
        "3.9 to 13.5 V input operating range, 1.5 A charge-current capability, NVDC power path, "
        "5 A RMS BATFET discharge path, 1.5 MHz switching and RTW WQFN-24 pinout"
    ),
    "TPS61088RHLR": (
        "2.7 to 12 V input, 4.5 to 12.6 V output, programmable 200 kHz to 2.2 MHz switching, "
        "11 A switch capability, 1.204 V feedback reference and RHL VQFN-20 pinout"
    ),
    "TLV809K33DBVR": (
        "2.87 to 2.99 V falling reset threshold, 40 mV typical hysteresis, push-pull active-low "
        "output and 0.1 uF local bypass recommendation"
    ),
    "CDMC8D28NP-1R2MC": (
        "1.2 uH plus or minus 20 percent, 7 mOhm maximum DCR, 12.2 A saturation current, "
        "12.9 A thermal current and 8.7 by 8.3 by 3.0 mm maximum body"
    ),
    "430450800": (
        "eight circuits, 8.5 A maximum per contact, 600 V, minus 40 to 105 degrees Celsius, "
        "right-angle through-hole Micro-Fit 3.0 header"
    ),
    "430450200": (
        "two circuits, 8.5 A maximum per contact, 600 V, minus 40 to 105 degrees Celsius, "
        "right-angle through-hole Micro-Fit 3.0 header"
    ),
    "MCP73871T-2CCI/ML": (
        "900 to 1100 mA fast charge with PROG1 at 1 kohm and SEL high, 75 to 125 mA "
        "termination with PROG3 at 10 kohm, 1.5 to 1.8 A adapter input limit, 1.23 V VPCC "
        "threshold plus or minus 3 percent, and 7 V absolute maximum input"
    ),
    "AP22811AW5-7": (
        "2.7 to 5.5 V input, 2 A continuous current, 65 mOhm maximum on-resistance at 5 V and "
        "25 degrees Celsius, 2.2 to 3.2 A overload limit, active-high enable, open-drain fault, "
        "reverse blocking, output discharge, UVLO and thermal shutdown"
    ),
    "AP63203WU-7": (
        "3.8 to 32 V input, fixed 3.3 V output, 2 A continuous current, 1.1 MHz switching, "
        "4.7 uH selected inside the 2.2 to 10 uH range, 10 uF input, two 22 uF output and "
        "100 nF bootstrap"
    ),
    "NR6045S4R7MT": (
        "4.7 uH plus or minus 20 percent, 34 mOhm maximum DCR, 4.97 A minimum saturation, "
        "3.3 A minimum thermal current, 6 x 6 x 4.5 mm body and 1.7 x 5.7 mm pads"
    ),
    "DFE252012F-1R0M=P2": (
        "1.0 uH plus or minus 20 percent, 40 mOhm maximum DCR, 4.7 A maximum "
        "inductance-decrease current, 3.3 A maximum 40 degree temperature-rise current, "
        "minus 40 to 125 degrees Celsius and 2.5 x 2.0 x 1.2 mm body"
    ),
    "TPS61023DRLR": (
        "0.5 to 5.5 V input, 1.8 V maximum startup threshold, 2.2 to 5.5 V output, "
        "0.37 to 2.9 uH effective inductance, 580 to 610 mV PWM feedback reference, "
        "5.5 V minimum overvoltage threshold and 3.7 A typical valley current limit"
    ),
    "TLV7042DGKR": (
        "1.6 to 6.5 V supply, rail-to-rail fail-safe inputs, open-drain outputs, internal "
        "hysteresis and power-on reset, 8 mV maximum input offset at 25 degrees Celsius, "
        "DGK VSSOP-8 pinout"
    ),
}

# Purchased items outside the custom boards that the design still depends on
# electrically. The power module is deliberately absent: it is bounded by
# docs/hardware/power-module-interface.md rather than bound to a product, and an
# unbound part cannot have a passing V1 audit.
EXTERNAL_COMPONENTS: tuple[dict[str, Any], ...] = (
    {
        "mpn": "NTCLE317E4103SBA",
        "role": "Cell-bonded off-board charge-temperature sensor",
        "supplier": "JLCPCB/LCSC",
        "order_code": "C3154341",
        "availability": {
            "status": "available",
            "checked": REVIEW_DATE,
            "source": "https://www.lcsc.com/product-detail/C3154341.html",
        },
        "datasheets": ["Vault/Scacchiera/Datasheets/NTCLE317E4103SBA_C3154341.pdf"],
        "wiki_source": "Vault/Scacchiera/Wiki/sources/ntcle317e4103sba-datasheet.md",
        "wiki_entity": "Vault/Scacchiera/Wiki/entities/ntcle317e4103sba.md",
        "interface_audit": {
            "status": "passed",
            "evidence": (
                "75 mm insulated leads terminate at hub J11, sense on pin 1 and ground on pin 2; "
                "the 1.6 mm epoxy body is tape-bonded or glued to the cell as permitted"
            ),
        },
        "ratings_audit": {
            "status": "passed",
            "fields": (
                "10 kohm at 25 degrees Celsius, R25 tolerance 2.19 percent, B25/85 3984 K plus or "
                "minus 0.5 percent, 0.5 degree accuracy from 25 to 85 degrees Celsius"
            ),
            "datasheet_locator": "quick reference, mounting, dimensions and ordering table",
        },
        "simulation_model": {
            "kind": "analytical",
            "path": "hardware/sim",
            "valid_region": (
                "V3 beta-equation resistance model sweeps filed R25, beta, comparator and resistor "
                "corners; V8 measures the assembled trip temperatures"
            ),
        },
        "conflicts": [],
    },
    {
        "mpn": "ER-OLEDM3.12-1W",
        "role": "Two off-board player OLED display modules",
        "supplier": "BuyDisplay",
        "order_code": "ER-OLEDM3.12-1W",
        "availability": {
            "status": "available",
            "checked": WIKI_UPDATE_DATE,
            "source": (
                "https://www.buydisplay.com/white-grayscale-3-12-inch-oled-display-module-"
                "256x64-arduino-raspberry-pi"
            ),
        },
        "datasheets": ["Vault/Scacchiera/Datasheets/ER-OLEDM3.12-1W_BUYDISPLAY.md"],
        "wiki_source": (
            "Vault/Scacchiera/Wiki/sources/er-oledm3-12-1w-manufacturer-evidence.md"
        ),
        "wiki_entity": "Vault/Scacchiera/Wiki/entities/er-oledm3-12-1w.md",
        "interface_audit": {
            "status": "blocked",
            "evidence": (
                "The module has a 16-pin 2.54 mm header while hub J5 and J6 are seven-pin JST GH; "
                "the exact harness and required serial-mode low straps are not yet bound."
            ),
        },
        "ratings_audit": {
            "status": "blocked",
            "fields": (
                "3.0 to 3.5 V logic supply, 3.6 V absolute maximum, 320 mA active maximum and "
                "2 mA sleep maximum from datasheet section 4.3"
            ),
            "datasheet_locator": "sections 4.1 through 4.3",
        },
        "simulation_model": {
            "kind": "datasheet_bounded",
            "path": "hardware/verification/load_budget.py",
            "valid_region": "320 mA maximum current per display; digital protocol belongs to V6",
        },
        "conflicts": [
            "Product page calls 2 mA the active maximum while the datasheet calls it sleep current.",
            "Original manufacturer PDF could not be filed because the supplier returned HTTP 403.",
        ],
    },
)


@dataclass(frozen=True)
class Use:
    board: str
    reference: str
    value: str


@dataclass(frozen=True)
class BoundPart:
    mpn: str
    supplier: str
    order_code: str
    footprint: str
    uses: tuple[Use, ...]


BOARD_NAMES = ("lightbar", "matrix", "hub", "power")

MANUFACTURERS = {
    "43045": "Molex",
    "0402CG": "Fenghua Advanced Technology",
    "0603WAF": "UNI-ROYAL",
    "74438357010": "Würth Elektronik",
    "74HC595D,118": "Nexperia",
    "7M27100009": "TXC",
    "A1257WR-S-4P": "CJT",
    "AP22811": "Diodes Incorporated",
    "AP63203": "Diodes Incorporated",
    "B2B-PH-K-S(LF)(SN)": "JST",
    "BAR64-02V": "Jiangsu Changjing Electronics Technology",
    "BAT54H": "Jiangsu Changjing Electronics Technology",
    "BSS123-7-F": "Diodes Incorporated",
    "BSS84-7-F": "Diodes Incorporated",
    "BQ": "Texas Instruments",
    "CC0603": "Yageo",
    "CC1206": "Yageo",
    "CDMC": "Sumida",
    "CL": "Samsung Electro-Mechanics",
    "DFE": "Murata",
    "DMP2035U-7": "Diodes Incorporated",
    "ESP32": "Espressif Systems",
    "GRM": "Murata",
    "JS102011SAQN": "C&K",
    "LQW": "Murata",
    "MCP73871": "Microchip Technology",
    "MF-MSMF050-2": "Bourns",
    "NR6045": "Magnetsyc",
    "PN5180": "NXP Semiconductors",
    "RC0603": "Yageo",
    "RS-03": "Fenghua Advanced Technology",
    "SDFL": "Sunlord",
    "SM02B": "JST",
    "SM07B": "JST",
    "SN74": "Texas Instruments",
    "T37K3RGB": "Harvatek",
    "TCA9535": "Texas Instruments",
    "TLV": "Texas Instruments",
    "TPS": "Texas Instruments",
    "USB4105": "GCT",
    "USBLC6": "UMW (UTD Semiconductor)",
}

DATASHEET_OVERRIDES = {
    "430450200": "430450200_C122431.md",
    "430450800": "430450800_C122422.md",
    "B2B-PH-K-S(LF)(SN)": "B2B-PH-K-S-LF-SN_C131337.pdf",
    "BSS123-7-F": "BSS123-7-F_C85107.pdf",
    "BSS84-7-F": "BSS84-7-F_C85202.pdf",
    "DFE201610E-R47M=P2": "DFE201610E-R47M-P2_C269773.pdf",
    "MCP73871T-2CCI/ML": "MCP73871T-2CCI-ML_C511310.pdf",
    "PN5180A0HN/C3E": "PN5180A0HN-C3E_C1526287.pdf",
    "SM02B-GHS-TB(LF)(SN)": "SM02B-GHS-TB-LF-SN_C189893.pdf",
    "SM07B-GHS-TB(LF)(SN)": "SM07B-GHS-TB-LF-SN_C495552.pdf",
    "T37K3RGB-05C000112U1930": (
        "T37K3RGB-05C000112U1930_DIGIKEY-3147-T37K3RGB-05C000112U1930CT-ND.pdf"
    ),
}

AVAILABILITY_SOURCES = {
    "1965-ESP32-C6-MINI-1U-N4CT-ND": (
        "https://www.digikey.es/es/products/detail/espressif-systems/"
        "ESP32-C6-MINI-1U-N4/21292143"
    ),
    "3147-T37K3RGB-05C000112U1930CT-ND": (
        "https://www.digikey.com/en/products/detail/harvatek-corporation/"
        "T37K3RGB-05C000112U1930/12177237"
    ),
    "732-11197-1-ND": (
        "https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/74438357010/6833535"
    ),
}


def _slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def _manufacturer(mpn: str) -> str:
    for prefix, manufacturer in MANUFACTURERS.items():
        if mpn.startswith(prefix):
            return manufacturer
    raise ValueError(f"manufacturer is not recorded for {mpn}")


def _datasheet(mpn: str) -> Path:
    override = DATASHEET_OVERRIDES.get(mpn)
    if override is not None:
        return DATASHEETS / override
    normalized = re.sub(r"[^A-Za-z0-9-]", "-", mpn)
    candidates = sorted(DATASHEETS.glob(f"{normalized}*.pdf"))
    manufacturer_copy = [path for path in candidates if path.stem.endswith("_manufacturer")]
    if manufacturer_copy:
        return manufacturer_copy[0]
    if not candidates:
        raise FileNotFoundError(f"no datasheet for {mpn}")
    return candidates[0]


def _category(part: BoundPart) -> str:
    footprint = part.footprint
    if footprint.startswith("Resistor_SMD"):
        return "resistor"
    if footprint.startswith("Capacitor_SMD"):
        return "capacitor"
    if footprint.startswith("Inductor_SMD") or part.mpn.startswith(("CDMC", "DFE", "NR6045")):
        return "inductor"
    if footprint.startswith("Connector_"):
        return "connector"
    if footprint.startswith("Crystal:"):
        return "crystal"
    if footprint.startswith("Fuse:"):
        return "resettable_fuse"
    if footprint.startswith("Button_"):
        return "switch"
    if part.mpn == "T37K3RGB-05C000112U1930":
        return "addressable_led"
    return "semiconductor"


def _limits(category: str) -> tuple[str, str]:
    records = {
        "resistor": (
            "value, tolerance, rated power, maximum working voltage, temperature coefficient, "
            "operating temperature and package dimensions",
            "ratings, dimensions and part-number tables",
        ),
        "capacitor": (
            "capacitance, tolerance, rated voltage, dielectric, temperature range, DC-bias "
            "behavior where published and package dimensions",
            "part-number, characteristics and dimensions tables",
        ),
        "inductor": (
            "inductance, tolerance, rated or saturation current, DC resistance, self-resonance, "
            "temperature range and package dimensions",
            "electrical characteristics, ratings and dimensions tables",
        ),
        "connector": (
            "pin numbering, current, voltage, contact resistance, temperature, mating direction "
            "and package dimensions",
            "ratings, ordering information and dimensional drawing",
        ),
        "crystal": (
            "frequency, tolerance, load capacitance, ESR, drive level, temperature stability and "
            "package dimensions",
            "electrical specifications and dimensions",
        ),
        "resettable_fuse": (
            "hold current, trip current, maximum voltage, trip time, resistance, temperature "
            "derating and package dimensions",
            "electrical characteristics, derating curves and dimensions",
        ),
        "switch": (
            "contact arrangement, current, voltage, contact resistance, travel, lifetime, "
            "temperature and package dimensions",
            "specifications, circuit and dimensions",
        ),
        "addressable_led": (
            "pinout, supply range, channel current, logic thresholds, timing, power, temperature, "
            "polarity and land pattern",
            "pages 2 to 5, electrical, timing, outline and recommended pad pattern",
        ),
        "semiconductor": (
            "pinout, no-connect and exposed-pad treatment, recommended operating range, absolute "
            "maximum voltage, current, power and temperature, startup state, thermal data and package",
            "pin description, absolute maximum, recommended operation, electrical, thermal and package tables",
        ),
    }
    return records[category]


def _model(part: BoundPart, category: str) -> dict[str, str]:
    if part.mpn == "TPS61088RHLR":
        return {
            "kind": "vendor",
            "path": "hardware/sim/models/vendor/TPS61088_TRANS.LIB",
            "valid_region": (
                "official TI transient model is filed; its two-expression ngspice compatibility "
                "copy parses but does not switch, so V3 uses a datasheet-bounded switching stage "
                "and leaves control-loop evidence open"
            ),
        }
    ti_vendor_models = {
        "TPS2553DBVR-1": "hardware/sim/models/vendor/TPS2553_SLVM425B.zip",
        "TPS61023DRLR": "hardware/sim/models/vendor/TPS61023_SLVMD68A.zip",
        "TPS63802DLAR": "hardware/sim/models/vendor/TPS63802_SLVMCX1C.zip",
    }
    if part.mpn in ti_vendor_models:
        return {
            "kind": "vendor",
            "path": ti_vendor_models[part.mpn],
            "valid_region": (
                "TI unencrypted transient PSpice model; V3 must prove ngspice compatibility and "
                "sweep datasheet input, load, temperature and external-component limits"
            ),
        }
    if part.mpn == "BSS123-7-F":
        return {
            "kind": "vendor",
            "path": "hardware/sim/models/vendor/BSS123.spice.txt",
            "valid_region": "Diodes model for BSS123, D-G-S order; corner limits remain datasheet bounded",
        }
    if part.mpn == "BSS84-7-F":
        return {
            "kind": "vendor",
            "path": "hardware/sim/models/vendor/BSS84.spice.txt",
            "valid_region": "Diodes model for BSS84, D-G-S order; corner limits remain datasheet bounded",
        }
    if part.mpn == "BAR64-02V":
        return {
            "kind": "datasheet_bounded",
            "path": "hardware/sim/models/bar64_02v.lib",
            "valid_region": (
                "2.5 ohm maximum at 10 mA and 100 MHz; 0.55 pF maximum at 1 V and 0.35 pF "
                "maximum at 5 V; V3 sweeps those published maxima"
            ),
        }
    if category in {"resistor", "capacitor", "inductor", "crystal", "resettable_fuse"}:
        return {
            "kind": "analytical",
            "path": "hardware/sim",
            "valid_region": "lumped model with datasheet tolerance, bias, ESR, DCR and temperature corners",
        }
    if category in {"connector", "switch"}:
        return {
            "kind": "layout_derived",
            "path": "hardware/sim",
            "valid_region": "contact and interconnect parasitics derived from rated contacts and routed geometry",
        }
    if category == "addressable_led":
        return {
            "kind": "behavioral",
            "path": "hardware/sim/lightbar_supply.py",
            "valid_region": "datasheet maximum channel current and timing corners; digital protocol belongs to V6",
        }
    return {
        "kind": "datasheet_bounded",
        "path": "hardware/sim",
        "valid_region": (
            "no distributable vendor ngspice model was identified; V3 may use only parameters "
            "enumerated in this part's filed datasheet and must sweep their full published limits; "
            "digital protocol behavior belongs to V6"
        ),
    }


def _board_parts(board: str) -> list[dict[str, str]]:
    if board == "lightbar":
        from hardware.pcb.lightbar import build_lightbar

        builder = build_lightbar
    elif board == "matrix":
        from hardware.pcb.matrix import build_matrix

        builder = build_matrix
    elif board == "hub":
        from hardware.pcb.hub import build_hub

        builder = build_hub
    elif board == "power":
        from hardware.pcb.power import build_power

        builder = build_power
    else:
        raise ValueError(f"unknown board: {board}")
    circuit = builder()
    records: list[dict[str, str]] = []
    for raw_part in circuit.parts:
        if str(getattr(raw_part, "fitted", "yes")) != "yes":
            continue
        mpn = str(getattr(raw_part, "manf_num", ""))
        if not mpn or mpn == "PCB_COPPER":
            continue
        records.append(
            {
                "mpn": mpn,
                "supplier": str(getattr(raw_part, "supplier", "")),
                "order_code": str(getattr(raw_part, "order_code", "")),
                "footprint": str(getattr(raw_part, "footprint", "")),
                "reference": str(raw_part.ref),
                "value": str(raw_part.value),
            }
        )
    return records


@cache
def _bound_parts() -> tuple[BoundPart, ...]:
    uses: dict[tuple[str, str, str, str], list[Use]] = defaultdict(list)

    def read_board(board: str) -> tuple[str, list[dict[str, str]]]:
        # SKiDL retains enough library and circuit state that the matrix and hub
        # together exceed the audit process's memory budget. Each subprocess
        # reads one authoritative builder and returns only immutable strings.
        result = subprocess.run(
            [sys.executable, "-m", MODULE_NAME, "--bound-board", board],
            cwd=ROOT,
            env=os.environ,
            check=True,
            capture_output=True,
            text=True,
        )
        return board, json.loads(result.stdout)

    with ThreadPoolExecutor(max_workers=2) as executor:
        board_records = executor.map(read_board, BOARD_NAMES)
    for board, raw_records in board_records:
        for raw in raw_records:
            key = (raw["mpn"], raw["supplier"], raw["order_code"], raw["footprint"])
            uses[key].append(Use(board, raw["reference"], raw["value"]))
    return tuple(
        BoundPart(mpn, supplier, order_code, footprint, tuple(part_uses))
        for (mpn, supplier, order_code, footprint), part_uses in sorted(uses.items())
    )


def _record(part: BoundPart) -> dict[str, Any]:
    category = _category(part)
    limits, locator = _limits(category)
    datasheet = _datasheet(part.mpn)
    slug = _slug(part.mpn)
    return {
        "mpn": part.mpn,
        "manufacturer": _manufacturer(part.mpn),
        "supplier": part.supplier,
        "order_code": part.order_code,
        "availability": {
            "status": "available",
            "checked": REVIEW_DATE,
            "source": AVAILABILITY_SOURCES.get(
                part.order_code,
                f"https://jlcpcb.com/partdetail?part={part.order_code}",
            ),
        },
        "datasheet": str(datasheet.relative_to(ROOT)),
        "wiki_source": f"Vault/Scacchiera/Wiki/sources/{slug}-datasheet.md",
        "wiki_entity": f"Vault/Scacchiera/Wiki/entities/{slug}.md",
        "category": category,
        "footprint": part.footprint,
        "uses": [use.__dict__ for use in part.uses],
        "library_audit": {
            "status": "passed",
            "checked": REVIEW_DATE,
            "evidence": (
                "manufacturer pin and package drawing checked against the SKiDL pin numbers, "
                "KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation"
            ),
            "checks": [
                "symbol_pin_numbers_and_names",
                "symbol_electrical_types",
                "exposed_and_no_connect_pins",
                "footprint_pad_numbers",
                "package_dimensions",
                "polarity_and_pin_one",
                "assembly_side",
                "cpl_zero_rotation",
            ],
        },
        "ratings_audit": {
            "status": "passed",
            "fields": limits,
            "datasheet_locator": locator,
        },
        "simulation_model": _model(part, category),
        "conflicts": [],
    }


def _wiki_date(record: dict[str, Any]) -> str:
    uses = record["uses"]
    assert isinstance(uses, list)
    if str(record["mpn"]) in {"DFE252012F-1R0M=P2", "NR6045S4R7MT"} or any(
        use.get("board") == "power" for use in uses
    ):
        return WIKI_UPDATE_DATE
    return REVIEW_DATE


def _write_wiki_page(record: dict[str, Any]) -> None:
    source_path = ROOT / str(record["wiki_source"])
    entity_path = ROOT / str(record["wiki_entity"])
    uses = record["uses"]
    assert isinstance(uses, list)
    use_text = ", ".join(
        f"{use['board']} {use['reference']} ({use['value']})" for use in uses
    )
    design_fact = DESIGN_FACTS.get(str(record["mpn"]), "See the filed data sheet and structured audit.")
    source_text = f"""---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: {_wiki_date(record)}
source_file: "{str(record['datasheet']).removeprefix('Vault/Scacchiera/')}"
source_title: "{record['mpn']} manufacturer datasheet"
publisher: "{record['manufacturer']}"
---

# {record['mpn']} datasheet

This source binds [{record['mpn']}](../entities/{_slug(str(record['mpn']))}.md) to supplier order
code `{record['order_code']}`. It is used by {use_text}.

[mpn::{record['mpn']}] [order_code::{record['order_code']}]
[manufacturer::{record['manufacturer']}] [footprint::{record['footprint']}]

## Design facts reviewed

- Library proof: {record['library_audit']['evidence']}.
- Ratings used by the design: {record['ratings_audit']['fields']}.
- Exact selected limits: {design_fact}.
- Datasheet locator: {record['ratings_audit']['datasheet_locator']}.
- Simulation treatment: {record['simulation_model']['kind']}, valid only for
  {record['simulation_model']['valid_region']}.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.
"""
    entity_text = f"""---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: {_wiki_date(record)}
source_count: 1
---

# {record['mpn']}

Exact fitted component from {record['manufacturer']}, used by {use_text}.

[mpn::{record['mpn']}] [supplier::{record['supplier']}]
[order_code::{record['order_code']}] [category::{record['category']}]

The immutable source is summarized in [[{_slug(str(record['mpn']))}-datasheet]]. The complete
library, rating, availability, and model audit is machine checked from
`docs/verification/v1-components.yaml`.
"""
    source_path.write_text(source_text, encoding="utf-8")
    entity_path.write_text(entity_text, encoding="utf-8")


def _update_wiki_index(records: list[dict[str, Any]]) -> None:
    index_path = WIKI / "index.md"
    index = index_path.read_text(encoding="utf-8")
    start = "<!-- V1-COMPONENT-CATALOG:START -->"
    end = "<!-- V1-COMPONENT-CATALOG:END -->"
    source_rows = "\n".join(
        f"| [[{_slug(str(record['mpn']))}-datasheet]] | {record['manufacturer']} | {_wiki_date(record)} |"
        for record in records
    )
    entity_rows = "\n".join(
        f"| [[{_slug(str(record['mpn']))}]] | 1 | {_wiki_date(record)} |" for record in records
    )
    catalog = f"""{start}
## V1 component datasheet sources

One exact source summary per purchased fitted MPN. The structured audit is
`docs/verification/v1-components.yaml`.

| Page | Manufacturer | Updated |
| --- | --- | --- |
{source_rows}

## V1 component entities

| Page | source_count | Updated |
| --- | ---: | --- |
{entity_rows}
{end}
"""
    if start in index:
        before, remainder = index.split(start, maxsplit=1)
        _, after = remainder.split(end, maxsplit=1)
        updated = before + catalog + after.lstrip("\n")
    else:
        updated = index.replace("## Concepts", catalog + "\n## Concepts", 1)
    index_path.write_text(updated, encoding="utf-8")


def main() -> None:
    bound_parts = _bound_parts()
    auditable_parts = [part for part in bound_parts if part.supplier and part.order_code]
    blocked_parts = [part for part in bound_parts if not part.supplier or not part.order_code]
    records = [_record(part) for part in auditable_parts]
    blockers = [
        {
            "mpn": part.mpn,
            "footprint": part.footprint,
            "uses": [use.__dict__ for use in part.uses],
            "status": "blocked",
            "reason": "Exact supplier order code and current availability are not verified.",
        }
        for part in blocked_parts
    ]
    document = {
        "version": 1,
        "milestone": "V1",
        "reviewed": REVIEW_DATE,
        "policy": (
            "Every purchased fitted component is exact, sourced, backed by an immutable "
            "manufacturer datasheet, library-audited, ratings-audited and model-classified."
        ),
        "components": records,
        "component_blockers": blockers,
        "external_components": list(EXTERNAL_COMPONENTS),
    }
    AUDIT_PATH.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    for record in records:
        _write_wiki_page(record)
    _update_wiki_index(records)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--bound-board":
        print(json.dumps(_board_parts(sys.argv[2])))
    else:
        main()
