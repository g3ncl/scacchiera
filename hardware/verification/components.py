"""Typed access to the V1 fitted-component audit."""

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).parents[2]
COMPONENT_AUDIT_PATH = ROOT / "docs" / "verification" / "v1-components.yaml"


def load_component_audit() -> dict[str, Any]:
    document: Any = yaml.safe_load(COMPONENT_AUDIT_PATH.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise TypeError("component audit must be a mapping")
    return document
