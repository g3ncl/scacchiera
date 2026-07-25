from hardware.pcb.bom import AssemblyPlan, BomKey, assembly_plan


def _key(*, footprint: str, library: str, fitted: str = "yes") -> BomKey:
    return BomKey("part", footprint, "MPN", "C1", library, fitted, 0.1)


def test_basic_part_stays_with_jlcpcb() -> None:
    plan = assembly_plan(
        _key(footprint="Capacitor_SMD:C_0805_2012Metric", library="Basic"),
        1,
    )
    assert plan.route == "JLCPCB"


def test_low_quantity_extended_connector_is_a_hand_solder_candidate() -> None:
    plan = assembly_plan(
        _key(footprint="Connector_JST:JST_GH_1x04_Horizontal", library="Extended"),
        1,
    )
    assert plan == AssemblyPlan(
        "Hand",
        "Iron",
        "Extended line: hand fitting it avoids a 2.70 EUR feeder change",
    )


def test_hidden_pad_module_stays_with_jlcpcb() -> None:
    plan = assembly_plan(
        _key(footprint="Chessboard:ESP32-C6-MINI-1U", library="Unbound"),
        1,
    )
    assert plan.route == "JLCPCB"
    assert plan.hand_method == "Reflow only"


def test_small_but_reachable_packages_are_hand_fitted() -> None:
    """0402, SOD-523 and 0.65 mm TSSOP are tedious, not unreachable."""
    for footprint in (
        "Capacitor_SMD:C_0402_1005Metric",
        "Diode_SMD:D_SOD-523",
        "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
    ):
        plan = assembly_plan(_key(footprint=footprint, library="Extended"), 1)
        assert plan == AssemblyPlan(
            "Hand",
            "Iron",
            "Extended line: hand fitting it avoids a 2.70 EUR feeder change",
        ), footprint


def test_matrix_is_populated_by_hand() -> None:
    plan = assembly_plan(
        _key(footprint="Diode_SMD:D_SOD-523", library="Extended"),
        32,
        "matrix",
    )
    assert plan == AssemblyPlan(
        "Hand",
        "Iron",
        "Hand populated to avoid JLCPCB's large-size assembly charge",
    )


def test_repeated_solderable_parts_stay_with_jlcpcb() -> None:
    plan = assembly_plan(
        _key(footprint="Package_TO_SOT_SMD:SOT-23", library="Extended"),
        16,
    )
    assert plan.route == "JLCPCB"


def test_lightbar_overrides_basic_and_reflow_parts_to_hand_assembly() -> None:
    basic = assembly_plan(
        _key(footprint="Capacitor_SMD:C_1210_3225Metric", library="Basic"),
        1,
        "lightbar",
    )
    # The SK6805MINI-E's legs sit outside its body, so unlike the WS2812C-2020
    # it replaced, an iron reaches every joint.
    led = assembly_plan(
        _key(footprint="Chessboard:SK6805MINI-E", library="Extended"),
        14,
        "lightbar",
    )
    assert basic.route == "Hand"
    assert led == AssemblyPlan(
        "Hand",
        "Iron",
        "The lightbar is below JLCPCB's supported assembly size",
    )


def test_hand_populated_board_flags_a_part_an_iron_cannot_reach() -> None:
    """A QFN on a hand-built board is unbuildable, and must not read as Iron."""
    plan = assembly_plan(
        _key(footprint="Package_DFN_QFN:QFN-40-1EP_6x6mm_P0.5mm", library="Extended"),
        1,
        "matrix",
    )
    assert plan.hand_method == "Needs reflow, not hand buildable"
