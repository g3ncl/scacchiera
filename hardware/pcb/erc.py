"""Run the real KiCad ERC on a generated schematic."""

import re
import subprocess
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


_UNCONNECTED = re.compile(
    r"\[pin_not_connected\]:.*?@\(([-\d.]+) mm, ([-\d.]+) mm\): Symbol (\S+) Pin (\S+)",
    re.DOTALL,
)
_ISSUE = re.compile(r"^\[([^]]+)\]:", re.MULTILINE)
_SEVERITY = re.compile(r"^    ; (error|warning)$", re.MULTILINE)

# SKiDL embeds modified generic symbols, and KiCad's standalone CLI does not
# load project library tables without a native project file. Its placement also
# uses valid electrical endpoints between display-grid points. These warnings
# remain visible in the report; V1 audits the libraries and PCB schematic
# parity verifies the resulting links and connectivity.
REVIEWED_WARNINGS = frozenset(
    {
        "endpoint_off_grid",
        "footprint_link_issues",
        "lib_symbol_issues",
        "lib_symbol_mismatch",
    }
)


def add_reviewed_no_connects(schematic: Path, report: Path, expected: frozenset[str]) -> None:
    """Add KiCad no-connect markers only for pins explicitly reviewed as unused."""
    report_text = report.read_text(encoding="utf-8")
    locations: dict[str, tuple[str, str]] = {}
    for x, y, reference, pin in _UNCONNECTED.findall(report_text):
        key = f"{reference}:{pin}"
        if key in expected:
            locations[key] = (x, y)
    missing = expected - locations.keys()
    if missing:
        raise ValueError(f"Reviewed no-connect pins missing from ERC report: {sorted(missing)}")

    schematic_text = schematic.read_text(encoding="utf-8")
    markers = []
    for key in sorted(expected):
        x, y = locations[key]
        marker_uuid = uuid5(NAMESPACE_URL, f"{schematic.name}:{key}")
        markers.append(f"  (no_connect\n    (at {x} {y})\n    (uuid {marker_uuid}))")
    closing = schematic_text.rfind(")")
    updated = schematic_text[:closing] + "\n" + "\n".join(markers) + schematic_text[closing:]
    schematic.write_text(updated, encoding="utf-8")


def run_reviewed_erc(schematic: Path, report: Path) -> None:
    """Run full KiCad ERC and reject errors or unreviewed warning classes."""
    result = subprocess.run(
        (
            "kicad-cli",
            "sch",
            "erc",
            "-o",
            str(report),
            str(schematic),
        ),
        check=False,
        capture_output=True,
        text=True,
        cwd=schematic.parent,
    )
    if result.returncode not in {0, 5}:
        raise RuntimeError(f"KiCad ERC failed for {schematic}:\n{result.stdout}\n{result.stderr}")
    report_text = report.read_text(encoding="utf-8")
    severities = frozenset(_SEVERITY.findall(report_text))
    issue_types = frozenset(_ISSUE.findall(report_text))
    unreviewed = issue_types - REVIEWED_WARNINGS
    if "error" in severities or unreviewed:
        raise RuntimeError(
            f"KiCad ERC has errors or unreviewed warnings for {schematic}: "
            f"{sorted(unreviewed)}"
        )
