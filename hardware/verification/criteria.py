"""Typed access to numeric acceptance criteria."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).parents[2]
CRITERIA_PATH = ROOT / "docs" / "hardware" / "criteria.yaml"


@dataclass(frozen=True)
class Criterion:
    identifier: str
    unit: str
    limits: dict[str, float]


def load_criterion(identifier: str) -> Criterion:
    document = load_criteria_document()
    raw_criteria = document.get("criteria")
    if not isinstance(raw_criteria, dict):
        raise TypeError("criteria must be a mapping")
    raw = raw_criteria.get(identifier)
    if not isinstance(raw, dict):
        raise KeyError(identifier)
    unit = raw.get("unit")
    raw_limits = raw.get("limits")
    if not isinstance(unit, str) or not isinstance(raw_limits, dict):
        raise TypeError(f"invalid criterion {identifier}")
    limits: dict[str, float] = {}
    for name, value in raw_limits.items():
        if not isinstance(name, str) or not isinstance(value, (int, float)):
            raise TypeError(f"invalid limit in {identifier}")
        limits[name] = float(value)
    return Criterion(identifier=identifier, unit=unit, limits=limits)


def load_criteria_document() -> dict[str, Any]:
    document: Any = yaml.safe_load(CRITERIA_PATH.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise TypeError("criteria document must be a mapping")
    return document
