"""V3 current-limit latch timing and open-cable behaviour."""

from hardware.verification.criteria import load_criterion
from hardware.verification.fault_response import (
    DEGLITCH_MAX_MS,
    DEGLITCH_MIN_MS,
    LightbarLimiterFault,
    floating_nets_when_a_cable_is_absent,
    led_rail_capacitance_f,
)


def test_a_cold_start_leaves_current_limit_before_the_latch_arms() -> None:
    fault = LightbarLimiterFault(led_rail_capacitance_f())
    limit = load_criterion("HUB-LED-RAIL-STARTUP-CURRENT-LIMIT").limits
    assert fault.current_limit_ms <= limit["maximum"]
    assert fault.current_limit_ms < DEGLITCH_MIN_MS


def test_the_rail_carries_far_less_than_the_capacitance_that_would_latch() -> None:
    fault = LightbarLimiterFault(led_rail_capacitance_f())
    assert led_rail_capacitance_f() < fault.capacitance_ceiling_f / 2.0


def test_a_short_is_bounded_by_the_latch_rather_than_by_the_supply() -> None:
    fault = LightbarLimiterFault(led_rail_capacitance_f())
    limit = load_criterion("HUB-LED-RAIL-LATCH-LATENCY").limits
    assert DEGLITCH_MAX_MS <= limit["maximum"]
    assert fault.short_circuit_energy_mj < 50.0


def test_more_capacitance_spends_longer_in_current_limit() -> None:
    nominal = led_rail_capacitance_f()
    assert (
        LightbarLimiterFault(nominal * 2.0).current_limit_ms
        > LightbarLimiterFault(nominal).current_limit_ms
    )


def test_no_hub_net_floats_when_a_harness_is_unplugged() -> None:
    # LED_RETURN used to: the second bar's data input arrives from the first
    # bar, and both stay powered from the same limiter, so unplugging the first
    # left a pixel input floating at 5 V. R37 defines it.
    assert floating_nets_when_a_cable_is_absent() == ()
