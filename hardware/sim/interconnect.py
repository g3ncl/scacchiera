"""Series inductance of the cabling and spine copper the split plane adds.

The monolithic matrix board has one shared bus on one substrate. Splitting it
puts a harness and a length of spine between the reader and every tank, and that
inductance lands in series with the loop. It is the whole electrical cost of the
split, so it is modelled from geometry here rather than guessed at once in a
deck.

Two closed forms, both standard and both magnetoquasistatic, which is the right
regime: at 13.56 MHz a 300 mm spine is 0.014 of a wavelength.

**The connector term is an assumption, not a datasheet value.** JST publishes no
contact inductance for the GH series, and no connector vendor at this price
publishes one. See A11 in `docs/hardware/assumptions.md`. Everything that
depends on it is swept over a bounding range rather than reported at a point.
"""

from math import acosh, log, pi


MU0 = 4e-7 * pi

# JST GH, 28 AWG stranded: 0.32 mm conductor diameter, 1.25 mm contact pitch, so
# the RF conductor and the ground beside it form a two-wire line at that spacing.
HARNESS_CONDUCTOR_RADIUS_MM = 0.16
HARNESS_PAIR_SPACING_MM = 1.25

# One mated contact pair, both ends of a harness. Bounded rather than known: 2 nH
# is about a 2 mm straight contact, 8 nH allows for the housing's full mated
# length plus the pad transitions at both boards. A11.
CONNECTOR_INDUCTANCE_MIN_H = 2.0e-9
CONNECTOR_INDUCTANCE_NOMINAL_H = 4.0e-9
CONNECTOR_INDUCTANCE_MAX_H = 8.0e-9
MATED_PAIRS_PER_HARNESS = 2


def two_wire_inductance_per_mm(
    spacing_mm: float = HARNESS_PAIR_SPACING_MM,
    radius_mm: float = HARNESS_CONDUCTOR_RADIUS_MM,
) -> float:
    """Loop inductance per mm of a two-wire line, signal against its return.

    The return is the ground contact beside the RF one in the same housing, which
    is why the strip and spine pinouts both put a ground either side of the bus.
    """
    return (MU0 / pi) * acosh(spacing_mm / (2.0 * radius_mm)) * 1e-3


def microstrip_inductance_per_mm(width_mm: float, height_mm: float) -> float:
    """Inductance per mm of a microstrip over a solid return plane.

    Wheeler's two forms, selected on width over height. Both are needed here: a
    deliberately drawn bus is wider than the dielectric is thick, and an
    autorouted 0.2 mm track on 0.6 mm stock is not. The narrow form gives about
    twice the inductance per mm, which is exactly why a bus worth caring about
    gets drawn rather than routed.
    """
    ratio = width_mm / height_mm
    if ratio >= 1.0:
        return (MU0 / (ratio + 1.393 + 0.667 * log(ratio + 1.444))) * 1e-3
    return (MU0 / (2.0 * pi)) * log(8.0 / ratio + ratio / 4.0) * 1e-3


def harness_inductance_h(
    length_mm: float, connector_inductance_h: float = CONNECTOR_INDUCTANCE_NOMINAL_H
) -> float:
    """One strip's harness: cable plus a mated pair at each end."""
    return (
        two_wire_inductance_per_mm() * length_mm
        + MATED_PAIRS_PER_HARNESS * connector_inductance_h
    )
