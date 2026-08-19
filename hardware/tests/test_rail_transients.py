"""V3 warm reset, power-off discharge and repeated brownout on the 3.3 V rail."""

from hardware.verification.criteria import load_criterion
from hardware.verification.rail_transients import (
    PowerOffDischarge,
    expander_driven_nets,
    rail_capacitance_f,
    reset_domain_refs,
)


def test_power_off_reaches_the_expander_reset_floor_in_time() -> None:
    discharge = PowerOffDischarge(rail_capacitance_f())
    limit = load_criterion("HUB-3V3-POR-DISCHARGE").limits
    assert discharge.time_to_por_floor_s <= limit["maximum"]


def test_the_bleeder_costs_a_negligible_share_of_the_rail() -> None:
    discharge = PowerOffDischarge(rail_capacitance_f())
    limit = load_criterion("HUB-3V3-BLEED-FRACTION").limits
    assert discharge.bleed_percent_of_load <= limit["maximum"]


def test_a_repeated_brownout_only_resets_once_the_rail_has_decayed() -> None:
    discharge = PowerOffDischarge(rail_capacitance_f())
    interval = discharge.time_to_por_floor_s
    assert discharge.resets_after_off_time(interval)
    assert not discharge.resets_after_off_time(interval * 0.99)


def test_more_capacitance_is_the_slow_direction() -> None:
    nominal = rail_capacitance_f()
    assert (
        PowerOffDischarge(nominal * 1.5).time_to_por_floor_s
        > PowerOffDischarge(nominal).time_to_por_floor_s
    )


def test_a_warm_reset_reaches_no_peripheral() -> None:
    # The MCU's enable line goes to its own pull-up, its delay capacitor and
    # the recovery pad, and nowhere else. No peripheral shares a reset with it.
    assert reset_domain_refs() == ("C6", "R20", "TP2", "U4")


def test_every_net_that_survives_a_warm_reset_is_enumerated() -> None:
    # The expander has no reset pin and the rail does not move, so each of
    # these comes back driven at its last written level rather than at the
    # level its passive pull gives at cold start. Firmware owns restoring
    # them, which is a V6 obligation, and this list is what V6 must cover.
    assert expander_driven_nets() == (
        "BUTTON_N",
        "CHARGE_INPUT_FAULT_N",
        "LED_EN",
        "LED_FAULT_N",
        "NFC_GPO1",
        "NFC_RESET_N",
        "OLED_DC",
        "OLED_RESET_N",
        "SEL_RCLK",
        "SEL_SRCLR_N",
    )
