"""Validation for the V0 requirement and criterion manifests."""

import hashlib
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).parents[2]
TRACEABILITY_PATH = ROOT / "docs" / "verification" / "traceability.yaml"


def load_traceability_document() -> dict[str, Any]:
    document: Any = yaml.safe_load(TRACEABILITY_PATH.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise TypeError("traceability document must be a mapping")
    return document


def source_digest(relative_path: str) -> str:
    # Line endings are normalised before hashing so the recorded digest identifies
    # the reviewed text rather than the checkout that produced it. A Windows
    # checkout stores CRLF in the working tree and would otherwise fail the
    # freshness check on files nobody has edited.
    content = (ROOT / relative_path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def require_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{context} must be a mapping")
    return value


def require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{context} must be a list")
    return value


def require_nonempty_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{context} must be a nonempty string")
    return value
