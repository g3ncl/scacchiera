"""V0 requirement traceability and numeric-criterion schema checks."""

from typing import Any

from hardware.verification.criteria import load_criteria_document
from hardware.verification.traceability import (
    load_traceability_document,
    require_list,
    require_mapping,
    require_nonempty_string,
    source_digest,
)


def test_functional_sources_have_reviewed_hashes() -> None:
    document = load_traceability_document()
    sources = require_mapping(document.get("sources"), "sources")
    assert set(sources) == {
        "docs/functional/gameplay.md",
        "docs/functional/interface.md",
        "docs/functional/overview.md",
        "docs/functional/physical.md",
    }
    for path, expected_digest in sources.items():
        assert isinstance(path, str)
        assert source_digest(path) == expected_digest


def test_every_requirement_has_source_and_tests() -> None:
    document = load_traceability_document()
    requirements = require_list(document.get("requirements"), "requirements")
    identifiers: set[str] = set()
    for raw in requirements:
        requirement = require_mapping(raw, "requirement")
        identifier = require_nonempty_string(requirement.get("id"), "requirement id")
        assert identifier not in identifiers
        identifiers.add(identifier)
        require_nonempty_string(requirement.get("statement"), f"{identifier} statement")
        source = require_mapping(requirement.get("source"), f"{identifier} source")
        require_nonempty_string(source.get("path"), f"{identifier} source path")
        require_nonempty_string(source.get("locator"), f"{identifier} source locator")
        test_ids = require_list(requirement.get("test_ids"), f"{identifier} test_ids")
        assert test_ids
        assert all(isinstance(test_id, str) and test_id.startswith("TEST-") for test_id in test_ids)


def test_numeric_criteria_have_sources_conditions_and_margin() -> None:
    document = load_criteria_document()
    criteria = require_mapping(document.get("criteria"), "criteria")
    assert criteria
    for identifier, raw in criteria.items():
        assert isinstance(identifier, str)
        criterion = require_mapping(raw, identifier)
        require_nonempty_string(criterion.get("description"), f"{identifier} description")
        require_nonempty_string(criterion.get("unit"), f"{identifier} unit")
        limits = require_mapping(criterion.get("limits"), f"{identifier} limits")
        assert limits
        assert all(isinstance(value, (int, float)) for value in limits.values())
        evidence = require_mapping(criterion.get("evidence"), f"{identifier} evidence")
        assert evidence.get("class") in {"Datasheet", "Derived", "Measured"}
        require_nonempty_string(evidence.get("source"), f"{identifier} evidence source")
        require_nonempty_string(evidence.get("locator"), f"{identifier} evidence locator")
        require_nonempty_string(criterion.get("operating_conditions"), f"{identifier} conditions")
        require_nonempty_string(criterion.get("margin"), f"{identifier} margin")


def test_requirement_and_criterion_links_are_bidirectional() -> None:
    traceability = load_traceability_document()
    raw_requirements = require_list(traceability.get("requirements"), "requirements")
    requirements: dict[str, dict[str, Any]] = {}
    for raw in raw_requirements:
        requirement = require_mapping(raw, "requirement")
        identifier = require_nonempty_string(requirement.get("id"), "requirement id")
        requirements[identifier] = requirement

    criteria_document = load_criteria_document()
    criteria = require_mapping(criteria_document.get("criteria"), "criteria")
    for criterion_id, raw in criteria.items():
        criterion = require_mapping(raw, str(criterion_id))
        requirement_ids = require_list(criterion.get("requirement_ids"), f"{criterion_id} requirement_ids")
        test_ids = require_list(criterion.get("test_ids"), f"{criterion_id} test_ids")
        assert requirement_ids and test_ids
        for requirement_id in requirement_ids:
            assert requirement_id in requirements
            linked = requirements[requirement_id].get("criterion_ids", [])
            assert criterion_id in linked
        for test_id in test_ids:
            assert any(test_id in requirement.get("test_ids", []) for requirement in requirements.values())

    for requirement_id, requirement in requirements.items():
        for criterion_id in requirement.get("criterion_ids", []):
            assert criterion_id in criteria, f"{requirement_id} links missing criterion {criterion_id}"


def test_component_absolute_maximums_have_test_ownership() -> None:
    document = load_traceability_document()
    mapping = require_mapping(document.get("component_absolute_maximums"), "component absolute maximums")
    require_nonempty_string(mapping.get("source"), "component source")
    require_nonempty_string(mapping.get("rule"), "component rule")
    test_ids = require_list(mapping.get("test_ids"), "component test_ids")
    assert test_ids == ["TEST-V1-ABSOLUTE-MAXIMUM-COVERAGE"]
