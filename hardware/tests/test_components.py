"""V1 exact-component, datasheet, library, and model evidence checks."""

from typing import Any

from hardware.verification.components import ROOT, load_component_audit
from hardware.verification.generate_component_audit import _bound_parts
from hardware.verification.traceability import require_list, require_mapping, require_nonempty_string


def _components() -> list[dict[str, Any]]:
    document = load_component_audit()
    raw_components = require_list(document.get("components"), "components")
    return [require_mapping(raw, "component") for raw in raw_components]


def test_every_fitted_purchased_mpn_has_one_exact_audit_record() -> None:
    audited = {
        (
            require_nonempty_string(record.get("mpn"), "mpn"),
            require_nonempty_string(record.get("supplier"), "supplier"),
            require_nonempty_string(record.get("order_code"), "order code"),
            require_nonempty_string(record.get("footprint"), "footprint"),
        )
        for record in _components()
    }
    bound = {
        (part.mpn, part.supplier, part.order_code, part.footprint)
        for part in _bound_parts()
    }
    assert len(audited) == 44
    assert audited == bound


def test_every_exact_part_has_an_immutable_manufacturer_source_and_wiki_ingest() -> None:
    for record in _components():
        mpn = require_nonempty_string(record.get("mpn"), "mpn")
        require_nonempty_string(record.get("manufacturer"), f"{mpn} manufacturer")
        for field in ("datasheet", "wiki_source", "wiki_entity"):
            relative = require_nonempty_string(record.get(field), f"{mpn} {field}")
            path = ROOT / relative
            assert path.is_file(), path
            assert path.stat().st_size > 100, path
        datasheet = ROOT / str(record["datasheet"])
        assert datasheet.read_bytes().startswith(b"%PDF"), datasheet


def test_library_and_rating_audits_are_complete_and_conflict_free() -> None:
    required_checks = {
        "symbol_pin_numbers_and_names",
        "symbol_electrical_types",
        "exposed_and_no_connect_pins",
        "footprint_pad_numbers",
        "package_dimensions",
        "polarity_and_pin_one",
        "assembly_side",
        "cpl_zero_rotation",
    }
    for record in _components():
        mpn = str(record["mpn"])
        library = require_mapping(record.get("library_audit"), f"{mpn} library audit")
        ratings = require_mapping(record.get("ratings_audit"), f"{mpn} ratings audit")
        assert library.get("status") == "passed"
        assert set(require_list(library.get("checks"), f"{mpn} checks")) == required_checks
        require_nonempty_string(library.get("evidence"), f"{mpn} library evidence")
        assert ratings.get("status") == "passed"
        require_nonempty_string(ratings.get("fields"), f"{mpn} rating fields")
        require_nonempty_string(ratings.get("datasheet_locator"), f"{mpn} rating locator")
        assert record.get("conflicts") == []


def test_availability_and_simulation_treatment_are_recorded() -> None:
    for record in _components():
        mpn = str(record["mpn"])
        availability = require_mapping(record.get("availability"), f"{mpn} availability")
        assert availability.get("status") == "available"
        assert availability.get("checked") == "2026-07-26"
        source = require_nonempty_string(availability.get("source"), f"{mpn} availability source")
        assert source.startswith("https://")
        model = require_mapping(record.get("simulation_model"), f"{mpn} model")
        assert model.get("kind") in {
            "vendor",
            "analytical",
            "layout_derived",
            "behavioral",
            "datasheet_bounded",
        }
        require_nonempty_string(model.get("path"), f"{mpn} model path")
        require_nonempty_string(model.get("valid_region"), f"{mpn} model valid region")
        if model.get("kind") == "vendor":
            assert (ROOT / str(model["path"])).is_file()


def test_matrix_mosfets_use_exact_vendor_models() -> None:
    by_mpn = {str(record["mpn"]): record for record in _components()}
    for mpn in ("BSS123-7-F", "BSS84-7-F"):
        model = require_mapping(by_mpn[mpn]["simulation_model"], f"{mpn} model")
        assert model["kind"] == "vendor"
        model_path = ROOT / str(model["path"])
        assert model_path.is_file()
        assert "DIODES INCORPORATED" in model_path.read_text(encoding="utf-8")


def test_environmental_declarations_are_not_used_as_samsung_datasheets() -> None:
    for record in _components():
        if record.get("manufacturer") == "Samsung Electro-Mechanics":
            assert str(record["datasheet"]).endswith("_manufacturer.pdf")


def test_external_power_components_are_exact_sourced_and_modelled() -> None:
    document = load_component_audit()
    records = [
        require_mapping(raw, "external component")
        for raw in require_list(document.get("external_components"), "external components")
    ]
    # The power module is not here on purpose. It is bounded by a written
    # interface rather than bound to a product, and V1 cannot pass an audit of a
    # part nobody has chosen yet.
    assert {record.get("mpn") for record in records} == {"NTCLE317E4103SBA"}
    for record in records:
        mpn = require_nonempty_string(record.get("mpn"), "external MPN")
        require_nonempty_string(record.get("supplier"), f"{mpn} supplier")
        require_nonempty_string(record.get("order_code"), f"{mpn} order code")
        availability = require_mapping(record.get("availability"), f"{mpn} availability")
        assert availability.get("status") == "available"
        assert availability.get("checked") == "2026-07-26"
        for relative in require_list(record.get("datasheets"), f"{mpn} datasheets"):
            source = ROOT / require_nonempty_string(relative, f"{mpn} datasheet")
            assert source.is_file()
            assert source.stat().st_size > 100
        for field in ("wiki_source", "wiki_entity"):
            wiki_page = ROOT / require_nonempty_string(record.get(field), f"{mpn} {field}")
            assert wiki_page.is_file()
        interface = require_mapping(record.get("interface_audit"), f"{mpn} interface")
        ratings = require_mapping(record.get("ratings_audit"), f"{mpn} ratings")
        model = require_mapping(record.get("simulation_model"), f"{mpn} model")
        assert interface.get("status") == "passed"
        assert ratings.get("status") == "passed"
        assert model.get("kind") in {"analytical", "datasheet_bounded"}
        require_nonempty_string(model.get("valid_region"), f"{mpn} model region")
        assert record.get("conflicts") == []
