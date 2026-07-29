"""Conservative interpretation of USB Type-C source-current advertisement.

The hub measures both CC pins after their independent Rd terminations. Values
between defined advertisement bands are deliberately assigned to the lower
current so ADC error or a changing source can never increase the load.
"""

from enum import Enum


class TypeCCurrent(Enum):
    DETACHED = 0.0
    DEFAULT = 0.5
    A1_5 = 1.5
    A3_0 = 3.0


VRD_CONNECT_MIN_V = 0.25
VRD_USB_THRESHOLD_V = 0.66
VRD_1_5_THRESHOLD_V = 1.23
VRD_MAX_V = 2.04


def advertised_current(cc1_v: float, cc2_v: float) -> TypeCCurrent:
    """Return the safe current class from the higher of the two CC readings."""
    cc_v = max(cc1_v, cc2_v)
    if cc_v < VRD_CONNECT_MIN_V or cc_v > VRD_MAX_V:
        return TypeCCurrent.DETACHED
    if cc_v <= VRD_USB_THRESHOLD_V:
        return TypeCCurrent.DEFAULT
    if cc_v <= VRD_1_5_THRESHOLD_V:
        return TypeCCurrent.A1_5
    return TypeCCurrent.A3_0
