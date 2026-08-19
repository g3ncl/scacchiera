"""Temperature corners for the parts whose data sheets actually specify one.

Both inductors are rated over minus 40 to 125 degrees Celsius *including their
own self heating*, and both define their rated RMS current as the current that
raises them 40 degrees above a 20 degree ambient. That pair of statements is
enough to corner them: the rise scales with the square of the current, so the
ambient a coil tolerates follows from the current it carries.

The same data sheets date their DC resistance to 20 degrees, which matters
because copper gains about four tenths of a percent per degree. The hot
resistance is what the buck's dropout actually sees.

What cannot be cornered here is the converter itself. Diodes publishes the
AP63203's switch resistance as a typical with no limits and no temperature
coefficient, so its contribution to a hot dropout is not derivable from any
filed document and stays open rather than being invented.
"""

from dataclasses import dataclass

from hardware.verification.junction_temperature import AMBIENT_ALLOWANCE_C


# Both inductor data sheets: operating range to 125 degrees Celsius including
# the coil's own rise, rated RMS current defined at a 40 degree rise from a
# 20 degree ambient.
COIL_LIMIT_C = 125.0
RATED_RISE_C = 40.0
RATING_AMBIENT_C = 20.0

# Annealed copper's resistance coefficient, referenced to the same 20 degrees
# the data sheets quote their DC resistance at.
COPPER_TEMPCO_PER_C = 0.00393


@dataclass(frozen=True)
class InductorThermal:
    """One coil, the current it carries, and the ambient it therefore allows."""

    designator: str
    part: str
    current_a: float
    rated_rms_a: float
    dcr_20c_ohm: float

    @property
    def self_rise_c(self) -> float:
        """Rise at the working current.

        Heating is the coil's resistance times the square of the current, and
        the data sheet fixes one point on that curve, so the rise scales with
        the square of the current relative to the rated one.
        """
        return RATED_RISE_C * (self.current_a / self.rated_rms_a) ** 2

    @property
    def maximum_ambient_c(self) -> float:
        return COIL_LIMIT_C - self.self_rise_c

    def hot_dcr_ohm(self, ambient_c: float = AMBIENT_ALLOWANCE_C) -> float:
        """Winding resistance at the ambient plus its own rise."""
        hot_c = ambient_c + self.self_rise_c
        return self.dcr_20c_ohm * (
            1.0 + COPPER_TEMPCO_PER_C * (hot_c - RATING_AMBIENT_C)
        )


# The 3.3 V converter is swept to a 2.0 A load and its peak is held under
# 2.5 A, so the ripple on top of that load contributes at most 1.0 A peak to
# peak. A triangular ripple that size adds 0.02 A RMS, which 2.1 A covers.
HUB_BUCK_COIL = InductorThermal(
    designator="hub L1",
    part="NR6045S4R7MT",
    current_a=2.1,
    rated_rms_a=3.30,
    dcr_20c_ohm=0.034,
)

# The boost stage's recorded bound at the full 10 W obligation is under 4.5 A
# RMS, against a coil rated 12.9 A.
POWER_BOOST_COIL = InductorThermal(
    designator="power L1",
    part="CDMC8D28NP-1R2MC",
    current_a=4.5,
    rated_rms_a=12.9,
    dcr_20c_ohm=0.007,
)

COILS = (HUB_BUCK_COIL, POWER_BOOST_COIL)


# AP63203WU-7 data sheet, Electrical Characteristics: 125 mOhm high-side switch,
# typical only. Carried here unchanged, which is exactly the part of a hot
# dropout that is not evidence.
BUCK_HIGH_SIDE_TYPICAL_OHM = 0.125
REGULATED_V = 3.30
INTERFACE_LOAD_A = 1.34


def hot_dropout_input_v(ambient_c: float = AMBIENT_ALLOWANCE_C) -> float:
    """Dropout with the coil hot and the switch at its only published value."""
    return REGULATED_V + INTERFACE_LOAD_A * (
        BUCK_HIGH_SIDE_TYPICAL_OHM + HUB_BUCK_COIL.hot_dcr_ohm(ambient_c)
    )
