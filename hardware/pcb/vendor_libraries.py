"""Vendor the KiCad symbols and footprints the design binds into the repo.

The schematics and the reviewed routes were validated against one specific
library release; any other release may carry renamed pins or resized pads, and
a reviewed route replayed against different pads is a different board (the
power board's U4 demonstrates it). Copying the bound library elements into the
repo makes every machine regenerate the reviewed board, which is what the
workflow's single-sources rule demands.

Run this once on the machine whose libraries the routes were reviewed against;
the Makefile then prefers the vendored set everywhere. Harvesting from a
machine with drifted libraries would vendor the drift instead, and the
reviewed-route DRC in `make check` would fail on it, which is the guard.
"""

import os
import re
import shutil
import sys
from pathlib import Path

PCB_DIR = Path(__file__).resolve().parent
ROOT = PCB_DIR.parents[1]
DEST = PCB_DIR / "vendored"

# Generated locally, never harvested.
LOCAL_LIBRARIES = {"Chessboard"}


def symbol_libraries() -> set[str]:
    pattern = re.compile(r"Part\(\s*[\"']([A-Za-z_0-9]+)[\"']", re.S)
    found: set[str] = set()
    for path in PCB_DIR.glob("*.py"):
        found |= set(pattern.findall(path.read_text(encoding="utf-8")))
    return found - LOCAL_LIBRARIES


def footprint_pairs() -> set[tuple[str, str]]:
    pattern = re.compile(r"[\"']([A-Z][A-Za-z_0-9]*):([A-Za-z0-9_.\-]+)[\"']")
    text = (ROOT / "docs" / "verification" / "v1-components.yaml").read_text(encoding="utf-8")
    pairs = {(lib, name) for lib, name in re.findall(r"footprint: ([A-Za-z_0-9]+):(\S+)", text)}
    for path in PCB_DIR.glob("*.py"):
        pairs |= set(pattern.findall(path.read_text(encoding="utf-8")))
    return {(lib, name) for lib, name in pairs if lib not in LOCAL_LIBRARIES}


def main() -> None:
    symbol_dir = os.environ.get("KICAD9_SYMBOL_DIR")
    footprint_dir = os.environ.get("KICAD_FOOTPRINT_DIR")
    if not symbol_dir or not footprint_dir:
        raise SystemExit("KICAD9_SYMBOL_DIR and KICAD_FOOTPRINT_DIR must be set")
    print(f"harvesting symbols from   {symbol_dir}")
    print(f"harvesting footprints from {footprint_dir}")

    (DEST / "symbols").mkdir(parents=True, exist_ok=True)
    copied_symbols = 0
    for library in sorted(symbol_libraries()):
        source = Path(symbol_dir) / f"{library}.kicad_sym"
        if not source.is_file():
            raise SystemExit(f"symbol library missing at source: {source}")
        shutil.copy(source, DEST / "symbols" / source.name)
        copied_symbols += 1

    copied_footprints = 0
    missing: list[str] = []
    for library, name in sorted(footprint_pairs()):
        source = Path(footprint_dir) / f"{library}.pretty" / f"{name}.kicad_mod"
        if not source.is_file():
            missing.append(f"{library}:{name}")
            continue
        target = DEST / "footprints" / f"{library}.pretty"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target / source.name)
        copied_footprints += 1

    print(f"vendored {copied_symbols} symbol libraries, {copied_footprints} footprints")
    if missing:
        # Pattern-scanned strings can include false positives; report rather
        # than fail so a real miss is visible next to the counts.
        print(f"not found at source ({len(missing)}): {', '.join(missing)}", file=sys.stderr)


if __name__ == "__main__":
    main()
