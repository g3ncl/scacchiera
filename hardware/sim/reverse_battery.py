"""Datasheet-bounded reverse-cell protection checks for the power board."""

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess


GENERATED_DIR = Path(__file__).parent / "generated" / "power" / "reverse_battery"
COMPARATOR_POWER_ON_S = 20e-6
COMPARATOR_MIN_SUPPLY_V = 1.6
COMPARATOR_ERROR_V = 0.015
PASS_FET_RDS_25C_OHM = 0.0121
PASS_FET_HOT_MULTIPLIER = 1.4
PASS_FET_HOT_RDS_OHM = PASS_FET_RDS_25C_OHM * PASS_FET_HOT_MULTIPLIER
PASS_FET_RMS_A = 4.422


@dataclass(frozen=True)
class ReverseBatteryCase:
    name: str
    cell_v: float
    adapter_present: bool


@dataclass(frozen=True)
class ReverseBatteryResult:
    raw_final_v: float
    cell_final_v: float
    gate_control_final_v: float
    raw_min_v: float
    raw_max_v: float


def minimum_correct_polarity_margin_v(cell_v: float) -> float:
    """Worst comparator overdrive with all divider resistors at 1 percent."""
    sense = cell_v * (0.99e6 / (1.01e6 + 0.99e6))
    # The reference numerator is the lower resistor. Maximize it against turn-on.
    reference = cell_v * (101e3 / (0.99e6 + 101e3))
    return sense - reference - COMPARATOR_ERROR_V


def hot_pass_fet_loss_w(rms_a: float = PASS_FET_RMS_A) -> float:
    return rms_a * rms_a * PASS_FET_HOT_RDS_OHM


def _deck(case: ReverseBatteryCase) -> str:
    adapter = "VADAPTER adapter 0 4.2\nRADAPTER adapter bat_raw 0.2" if case.adapter_present else ""
    return f"""* CSD25404Q3 and TLV7021 bounded functional protection model
.option noacct
VCELL cell_source 0 PWL(0 0 1u 0 2u {case.cell_v})
RCELL cell_source cell_pos 0.05
{adapter}
RREF_TOP bat_raw ref 1.01meg
RREF_BOTTOM ref 0 99k
RSENSE_TOP cell_pos sense 1.01meg
RSENSE_BOTTOM sense 0 0.99meg
DCLAMP 0 sense DCLAMP_MODEL
DBODY cell_pos bat_raw DBODY_MODEL
* TLV7021 POR is high impedance. The control enables only after its 20 us
* maximum functional delay and with the worst offset plus hysteresis allowed.
BCTRL control 0 V=(time>{COMPARATOR_POWER_ON_S})*(v(bat_raw)>{COMPARATOR_MIN_SUPPLY_V})*(v(sense)>v(ref)+{COMPARATOR_ERROR_V})
SFET cell_pos bat_raw control 0 PASS_SWITCH
RLEAK bat_raw 0 100meg
.model PASS_SWITCH SW(Ron={PASS_FET_HOT_RDS_OHM} Roff=1g Vt=0.5 Vh=0.1)
.model DBODY_MODEL D(Is=1n N=1 Rs=0.01 Bv=20)
.model DCLAMP_MODEL D(Is=2u N=1.05 Rs=1 Bv=30)
.tran 0.2u 200u uic
.meas tran raw_final_v FIND v(bat_raw) AT=199u
.meas tran cell_final_v FIND v(cell_pos) AT=199u
.meas tran gate_control_final_v FIND v(control) AT=199u
.meas tran raw_min_v MIN v(bat_raw) FROM=0 TO=200u
.meas tran raw_max_v MAX v(bat_raw) FROM=0 TO=200u
.end
"""


def run_case(case: ReverseBatteryCase) -> ReverseBatteryResult:
    work_dir = GENERATED_DIR / case.name
    work_dir.mkdir(parents=True, exist_ok=True)
    deck_path = work_dir / "reverse_battery.cir"
    deck_path.write_text(_deck(case), encoding="utf-8")
    completed = subprocess.run(
        ("ngspice", "-b", deck_path.name), cwd=work_dir,
        check=True, capture_output=True, text=True,
    )
    measurements: dict[str, float] = {}
    for key in (
        "raw_final_v", "cell_final_v", "gate_control_final_v", "raw_min_v", "raw_max_v",
    ):
        match = re.search(rf"^{key}\s*=\s*([-+0-9.eE]+)", completed.stdout, re.MULTILINE)
        if match is None:
            raise RuntimeError(f"ngspice reported no {key}\n{completed.stdout}")
        measurements[key] = float(match.group(1))
    return ReverseBatteryResult(**measurements)
