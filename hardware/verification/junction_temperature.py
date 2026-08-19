"""How hot the dissipating parts get, expressed as the ambient they tolerate.

V3 asks for junction-temperature estimates. Stating one temperature would need
an ambient, and the ambient inside the enclosure is not measured yet. So each
case is inverted: given the part's dissipation bound and its data sheet thermal
resistance, what is the highest ambient at which its junction still stays under
the limit? That number is a property of the design alone, and comparing it with
an ambient allowance keeps the assumption in one visible place.

Every dissipation here is an upper bound, not an estimate. For the two
switching converters the whole stage's accepted efficiency floor is charged to
the controller, which also hands it the inductor's loss. That is pessimistic on
purpose: a bound that is too high still proves the margin.
"""

from dataclasses import dataclass

from hardware.sim.reverse_battery import hot_pass_fet_loss_w
from hardware.verification.load_budget import (
    BUCK_EFFICIENCY,
    LIGHTBAR_A,
    LoadBudget,
    RAIL_3V3_V,
)


# docs/functional/power.md states the product's conditions as 20 to 25 degrees
# Celsius. The air around a part is warmer than the room, and by how much is a
# V8 measurement, so 20 degrees of enclosure rise is an acceptance limit on the
# enclosure rather than a measured value. Together they are the ambient every
# case below has to tolerate.
ROOM_MAX_C = 25.0
ENCLOSURE_RISE_ALLOWANCE_C = 20.0
AMBIENT_ALLOWANCE_C = ROOM_MAX_C + ENCLOSURE_RISE_ALLOWANCE_C


@dataclass(frozen=True)
class ThermalCase:
    """One dissipating part, its bound, and the ambient it can survive."""

    designator: str
    part: str
    dissipation_w: float
    theta_ja_c_per_w: float
    junction_limit_c: float

    @property
    def rise_c(self) -> float:
        return self.dissipation_w * self.theta_ja_c_per_w

    @property
    def maximum_ambient_c(self) -> float:
        return self.junction_limit_c - self.rise_c


# AP63203WU-7 data sheet: 89 degrees Celsius per watt in TSOT26, thermal
# shutdown at 150. The stage's loss uses the same 85 percent efficiency floor
# the load budget uses, which the data sheet's own curves sit well above.
_BUCK_OUTPUT_W = RAIL_3V3_V * LoadBudget().rail_3v3_a
HUB_BUCK = ThermalCase(
    designator="hub U5",
    part="AP63203WU-7",
    dissipation_w=_BUCK_OUTPUT_W * (1.0 / BUCK_EFFICIENCY - 1.0),
    theta_ja_c_per_w=89.0,
    junction_limit_c=150.0,
)

# TPS2553DBVR-1 data sheet: 135 mOhm maximum rDS(on) over minus 40 to 125
# degrees Celsius in DBV, 182.6 degrees per watt, 150 degree junction maximum.
# A pass switch dissipates nothing but conduction, so this bound is complete.
LIGHTBAR_LIMITER_RDS_OHM = 0.135
HUB_LIGHTBAR_LIMITER = ThermalCase(
    designator="hub U7",
    part="TPS2553DBVR-1",
    dissipation_w=LIGHTBAR_A * LIGHTBAR_A * LIGHTBAR_LIMITER_RDS_OHM,
    theta_ja_c_per_w=182.6,
    junction_limit_c=150.0,
)

# TPS61088RHLR data sheet: 38.8 degrees per watt on the standard board, the
# higher of its two figures, and a 150 degree junction maximum. The stage owes
# 10 W out at the 80 percent efficiency floor the boost bench accepts.
BOOST_OUTPUT_W = 10.0
BOOST_EFFICIENCY_FLOOR = 0.80
POWER_BOOST = ThermalCase(
    designator="power U2",
    part="TPS61088RHLR",
    dissipation_w=BOOST_OUTPUT_W / BOOST_EFFICIENCY_FLOOR - BOOST_OUTPUT_W,
    theta_ja_c_per_w=38.8,
    junction_limit_c=150.0,
)

# BQ25895RTWR data sheet: 31.8 degrees per watt in RTW WQFN-24 and a 150 degree
# junction maximum. The charger's worst input is the qualified 1.95 A limit at
# 5 V, and the path's accepted efficiency floor is 85 percent.
CHARGER_INPUT_W = 5.0 * 1.95
CHARGER_EFFICIENCY_FLOOR = 0.85
POWER_CHARGER = ThermalCase(
    designator="power U1",
    part="BQ25895RTWR",
    dissipation_w=CHARGER_INPUT_W * (1.0 - CHARGER_EFFICIENCY_FLOOR),
    theta_ja_c_per_w=31.8,
    junction_limit_c=150.0,
)

# CSD25404Q3 data sheet: 55 degrees per watt on one square inch of two-ounce
# copper, 160 on minimum pad copper. The higher figure is used because the
# power board does not reserve a square inch for this part. Its loss is the
# reverse-battery bench's hot conduction bound at the same 4.442 A.
REVERSE_FET_MINIMUM_COPPER_THETA = 160.0
POWER_REVERSE_FET = ThermalCase(
    designator="power Q1",
    part="CSD25404Q3",
    dissipation_w=hot_pass_fet_loss_w(),
    theta_ja_c_per_w=REVERSE_FET_MINIMUM_COPPER_THETA,
    junction_limit_c=150.0,
)

CASES = (
    HUB_BUCK,
    HUB_LIGHTBAR_LIMITER,
    POWER_BOOST,
    POWER_CHARGER,
    POWER_REVERSE_FET,
)
