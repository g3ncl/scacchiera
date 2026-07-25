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
        "Iron or hot air",
        "Low quantity and accessible pads make external purchase and manual fitting practical",
    )


def test_hidden_pad_module_stays_with_jlcpcb() -> None:
    plan = assembly_plan(
        _key(footprint="Chessboard:ESP32-C3-MINI-1U", library="Unbound"),
        1,
    )
    assert plan.route == "JLCPCB"
    assert plan.hand_method == "Stencil reflow only"


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
    reflow = assembly_plan(
        _key(footprint="LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm", library="Unbound"),
        17,
        "lightbar",
    )
    assert basic.route == "Hand"
    assert reflow == AssemblyPlan(
        "Hand",
        "Stencil reflow",
        "The lightbar is below JLCPCB's supported assembly size",
    )
