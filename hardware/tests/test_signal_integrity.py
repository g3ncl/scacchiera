"""V3 waveform integrity on the buses that leave the hub on a cable."""

from hardware.verification.criteria import load_criterion
from hardware.verification.signal_integrity import (
    I2C_RISE_LIMIT_FAST_NS,
    I2cBusBudget,
    LedSignalBudget,
    SerialLinkBudget,
)


def test_pixel_sees_the_high_time_the_hub_sent() -> None:
    budget = LedSignalBudget()
    limit = load_criterion("LB-DATA-PULSE-DISTORTION").limits
    assert budget.pulse_width_distortion_s * 1e9 <= limit["maximum"]


def test_distortion_comes_from_asymmetry_not_delay() -> None:
    """Both edges are slow; only their difference reaches the pixel as error."""
    budget = LedSignalBudget()
    assert budget.rise_to_threshold_s > budget.fall_to_threshold_s
    assert budget.pulse_width_distortion_s < budget.rise_to_threshold_s


def test_a_longer_harness_costs_margin() -> None:
    assert (
        LedSignalBudget(cable_pf=150.0).pulse_width_distortion_s
        > LedSignalBudget(cable_pf=0.0).pulse_width_distortion_s
    )


def test_i2c_is_a_standard_mode_bus() -> None:
    budget = I2cBusBudget()
    limit = load_criterion("HUB-I2C-RISE-TIME").limits
    assert budget.rise_time_s * 1e9 <= limit["maximum"]
    assert budget.fits_standard_mode


def test_fast_mode_does_not_fit_and_is_recorded_as_such() -> None:
    """Asserted as a constraint, so firmware cannot quietly assume 400 kHz.

    Reaching fast mode with these pull-ups would need the bus under about
    70 pF, which a cable to the power module does not leave.
    """
    assert not I2cBusBudget().fits_fast_mode
    assert I2cBusBudget(bus_pf=50.0).rise_time_s * 1e9 <= I2C_RISE_LIMIT_FAST_NS


def test_shift_registers_see_a_clean_enough_edge() -> None:
    budget = SerialLinkBudget()
    limit = load_criterion("MATRIX-SERIAL-TRANSITION-RATE").limits
    assert budget.transition_rate_ns_per_v <= limit["maximum"]


def test_the_serial_edge_is_a_third_of_a_half_period_at_the_cable_bound() -> None:
    """Recorded because the sourced limit and the rule of thumb disagree here.

    A third of a half period sounds tight, and it is what a general rule about
    edge rates would flag. The register's own transition-rate specification is
    the limit that actually applies, and it is met eight times over. The
    observation stays so that raising the clock is a decision rather than an
    accident.
    """
    budget = SerialLinkBudget()
    assert 0.3 < budget.edge_fraction_of_half_period < 0.4
