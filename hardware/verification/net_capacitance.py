"""Sum the capacitance a generated circuit puts on one net.

Reading it from the schematic rather than restating it means a capacitor added
to a rail changes the numbers that depend on it, instead of leaving them to
drift quietly out of date.
"""

from skidl import Circuit


_SUFFIX_SCALE = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3}


def farads(value: str) -> float:
    """Read a part value string such as "22u 25V" as a capacitance."""
    token = value.split()[0]
    scale = _SUFFIX_SCALE.get(token[-1])
    if scale is None:
        raise ValueError(f"capacitor value {value!r} has no recognised suffix")
    return float(token[:-1]) * scale


def net_capacitance_f(circuit: Circuit, net_name: str) -> float:
    return sum(
        farads(str(pin.part.value))
        for net in circuit.nets
        if str(net.name) == net_name
        for pin in net.pins
        if str(pin.part.ref).startswith("C")
    )
