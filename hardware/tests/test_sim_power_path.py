"""V3 averaged state and fault checks for the power-board NVDC path."""

from hardware.sim.power_path import (
    BATFET_CONTINUOUS_A,
    CHARGE_CURRENT_MAX_A,
    INPUT_CURRENT_CEILING_A,
    PowerPathCase,
    SourceMode,
    evaluate,
)


def test_battery_alone_supports_the_full_ten_watts() -> None:
    result = evaluate(PowerPathCase(None, 2.87, 10.0))
    assert result.mode is SourceMode.BATTERY
    assert result.output_supported
    assert result.battery_discharge_a < BATFET_CONTINUOUS_A


def test_qualified_source_charges_an_idle_cell() -> None:
    result = evaluate(PowerPathCase(5.0, 3.6, 0.0))
    assert result.mode is SourceMode.ADAPTER
    assert result.charge_a == CHARGE_CURRENT_MAX_A
    assert result.input_a < INPUT_CURRENT_CEILING_A


def test_system_load_has_priority_over_charging() -> None:
    result = evaluate(PowerPathCase(5.0, 3.6, 6.0))
    assert result.mode is SourceMode.ADAPTER
    assert result.output_supported
    assert result.charge_a < CHARGE_CURRENT_MAX_A


def test_battery_supplements_a_full_load_without_a_drop() -> None:
    result = evaluate(PowerPathCase(5.0, 3.6, 10.0))
    assert result.mode is SourceMode.SUPPLEMENT
    assert result.output_supported
    assert 0.0 < result.battery_discharge_a < BATFET_CONTINUOUS_A


def test_unqualified_source_keeps_the_safe_default() -> None:
    result = evaluate(PowerPathCase(5.0, 3.6, 0.0, source_qualified=False))
    assert result.input_a <= 0.5


def test_external_temperature_gate_wins_over_a_stuck_charge_command() -> None:
    result = evaluate(
        PowerPathCase(
            5.0, 3.6, 0.0, temperature_ok=False,
            charge_commanded=False, stuck_charge_command=True,
        )
    )
    assert result.charge_a == 0.0


def test_adapter_removal_hands_the_same_load_to_the_battery() -> None:
    before = evaluate(PowerPathCase(5.0, 3.6, 5.0))
    after = evaluate(PowerPathCase(None, 3.6, 5.0))
    assert before.output_supported and after.output_supported
    assert after.mode is SourceMode.BATTERY


def test_missing_battery_runs_only_loads_the_adapter_can_supply() -> None:
    light = evaluate(PowerPathCase(5.0, None, 5.0))
    full = evaluate(PowerPathCase(5.0, None, 10.0))
    assert light.output_supported
    assert not full.output_supported


def test_depleted_cell_turns_the_boost_off() -> None:
    result = evaluate(PowerPathCase(None, 2.86, 1.0))
    assert result.mode is SourceMode.OFF
    assert not result.boost_enabled


def test_battery_short_is_a_latched_fault_case() -> None:
    result = evaluate(PowerPathCase(5.0, 3.6, 0.0, battery_short=True))
    assert result.mode is SourceMode.FAULT
    assert result.critical_fault == "battery short"


def test_reverse_battery_is_isolated_like_a_missing_cell() -> None:
    result = evaluate(PowerPathCase(None, 3.6, 0.0, battery_reversed=True))
    assert result.mode is SourceMode.OFF
    assert result.critical_fault is None


def test_reverse_battery_does_not_prevent_adapter_only_operation() -> None:
    result = evaluate(PowerPathCase(5.0, 3.6, 5.0, battery_reversed=True))
    assert result.mode is SourceMode.ADAPTER
    assert result.output_supported
    assert result.charge_a == 0.0
