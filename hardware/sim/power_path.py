"""Data-sheet-bounded averaged model of the power-board source handover.

The BQ25895 has no public transistor-level model. This model covers its NVDC
source priority, external input-current ceiling, charge-current setting,
BATFET current limits and the independent hub temperature gate. It does not
claim switching-loop stability or safe behavior with a reversed cell.
"""

from dataclasses import dataclass
from enum import Enum


INPUT_CURRENT_CEILING_A = 390.0 / (200.0 * 0.99)
DEFAULT_INPUT_LIMIT_A = 0.5
QUALIFIED_INPUT_LIMIT_A = 1.95
PROGRAMMED_CHARGE_A = 1.472
CHARGE_CURRENT_MAX_A = PROGRAMMED_CHARGE_A * 1.05
CHARGER_EFFICIENCY_FLOOR = 0.85
BOOST_EFFICIENCY_FLOOR = 0.80
BATFET_CONTINUOUS_A = 6.0
BATFET_PEAK_A = 9.0
BOOST_CUTOFF_V = 2.87


class SourceMode(Enum):
    OFF = "off"
    BATTERY = "battery"
    ADAPTER = "adapter"
    SUPPLEMENT = "supplement"
    FAULT = "fault"


@dataclass(frozen=True)
class PowerPathCase:
    adapter_v: float | None
    battery_v: float | None
    output_w: float
    source_qualified: bool = True
    temperature_ok: bool = True
    charge_commanded: bool = True
    stuck_charge_command: bool = False
    battery_short: bool = False
    battery_reversed: bool = False


@dataclass(frozen=True)
class PowerPathResult:
    mode: SourceMode
    input_a: float
    charge_a: float
    battery_discharge_a: float
    output_supported: bool
    boost_enabled: bool
    critical_fault: str | None = None


def evaluate(case: PowerPathCase) -> PowerPathResult:
    if case.battery_reversed:
        return PowerPathResult(
            SourceMode.FAULT, 0.0, 0.0, 0.0, False, False,
            "reversed cell exceeds the charger's negative BAT rating",
        )
    if case.battery_short:
        return PowerPathResult(
            SourceMode.FAULT, 0.0, 0.0, 0.0, False, False, "battery short",
        )

    battery_available = case.battery_v is not None and case.battery_v >= BOOST_CUTOFF_V
    adapter_available = case.adapter_v is not None and case.adapter_v >= 3.9
    if not adapter_available and not battery_available:
        return PowerPathResult(SourceMode.OFF, 0.0, 0.0, 0.0, case.output_w == 0.0, False)

    load_at_sys_w = case.output_w / BOOST_EFFICIENCY_FLOOR
    input_limit = QUALIFIED_INPUT_LIMIT_A if case.source_qualified else DEFAULT_INPUT_LIMIT_A
    input_limit = min(input_limit, INPUT_CURRENT_CEILING_A)
    available_input_w = (
        case.adapter_v * input_limit * CHARGER_EFFICIENCY_FLOOR
        if adapter_available and case.adapter_v is not None
        else 0.0
    )
    charge_allowed = (
        adapter_available
        and battery_available
        and case.temperature_ok
        and (case.charge_commanded or case.stuck_charge_command)
    )
    charge_a = 0.0
    if charge_allowed and case.battery_v is not None:
        spare_w = max(0.0, available_input_w - load_at_sys_w)
        charge_a = min(CHARGE_CURRENT_MAX_A, spare_w / case.battery_v)

    deficit_w = max(0.0, load_at_sys_w + charge_a * (case.battery_v or 0.0) - available_input_w)
    battery_discharge_a = deficit_w / case.battery_v if battery_available and case.battery_v else 0.0
    supported = deficit_w == 0.0 or (
        battery_available and battery_discharge_a <= BATFET_CONTINUOUS_A
    )
    if adapter_available and battery_discharge_a > 0.0:
        mode = SourceMode.SUPPLEMENT
    elif adapter_available:
        mode = SourceMode.ADAPTER
    else:
        mode = SourceMode.BATTERY
        battery_discharge_a = load_at_sys_w / case.battery_v if case.battery_v else 0.0
        supported = battery_discharge_a <= BATFET_CONTINUOUS_A
    return PowerPathResult(
        mode,
        min(input_limit, (load_at_sys_w + charge_a * (case.battery_v or 0.0)) / (
            (case.adapter_v or 1.0) * CHARGER_EFFICIENCY_FLOOR
        )) if adapter_available else 0.0,
        charge_a,
        battery_discharge_a,
        supported,
        battery_available,
    )
