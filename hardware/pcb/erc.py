"""Run the real KiCad ERC on a generated schematic."""

import re
import subprocess
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5


_UNCONNECTED = re.compile(
    r"\[pin_not_connected\]:.*?@\(([-\d.]+) mm, ([-\d.]+) mm\): Symbol (\S+) Pin (\S+)",
    re.DOTALL,
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


def run_error_erc(schematic: Path, report: Path) -> None:
    """Run KiCad ERC and fail generation if any error remains."""
    result = subprocess.run(
        (
            "kicad-cli",
            "sch",
            "erc",
            "--severity-error",
            "--exit-code-violations",
            "-o",
            str(report),
            str(schematic),
        ),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"KiCad ERC failed for {schematic}:\n{result.stdout}\n{result.stderr}")
