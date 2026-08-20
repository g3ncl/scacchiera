"""Run the fabricator's limits against a routed board: the manufacturer's DFM
as a repeatable check instead of an upload-time surprise.

The board is copied to a scratch directory with jlcpcb.kicad_dru beside it, so
the fabrication rules never sit next to the generated boards where the design
gate's own DRC would silently absorb them. The design gate checks the rules
the boards route against; this checks the floors the factory can build.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KICAD_CLI = os.environ.get("KICAD_CLI", "/usr/bin/kicad-cli")
PCB_DIR = Path(__file__).resolve().parent
BOARDS = ("lightbar", "hub", "power", "quad")


def check(name: str) -> int:
    board = PCB_DIR / "generated" / name / f"{name}.kicad_pcb"
    if not board.is_file():
        raise SystemExit(f"{board} is missing; generate the board first")
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch) / board.name
        shutil.copy(board, work)
        shutil.copy(PCB_DIR / "jlcpcb.kicad_dru", Path(scratch) / f"{name}.kicad_dru")
        report = Path(scratch) / f"{name}-dfm.rpt"
        subprocess.run(
            [KICAD_CLI, "pcb", "drc", "--output", str(report), str(work)],
            check=True, capture_output=True,
        )
        text = report.read_text(encoding="utf-8")
    # Only the fabrication rules matter here; the design gate owns the rest.
    findings = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("[") and "'JLC" in line
    ]
    # Silkscreen near copper is clipped by the fab, not rejected: advisory.
    errors = [f for f in findings if "silk" not in f.lower()]
    by_rule: dict[str, int] = {}
    for f in findings:
        rule = f.split("'")[1] if "'" in f else f[:40]
        by_rule[rule] = by_rule.get(rule, 0) + 1
    summary = ", ".join(f"{rule}: {count}" for rule, count in sorted(by_rule.items()))
    print(f"{name}: {len(errors)} errors, {len(findings) - len(errors)} advisories"
          f"{'  [' + summary + ']' if summary else ''}")
    for line in errors[:6]:
        print(f"  {line}")
    return len(errors)


def main() -> None:
    names = sys.argv[1:] or list(BOARDS)
    total = sum(check(name) for name in names)
    print(f"DFM: {total} fabrication findings across {', '.join(names)}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
