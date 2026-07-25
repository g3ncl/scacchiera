"""Derive an ngspice .SUBCKT from a SKiDL circuit.

Walking the same Circuit/Part/Net objects used to emit the KiCad netlist means
the SPICE topology and the schematic topology cannot drift apart.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skidl import Circuit, Net

from hardware.pcb.matrix import COIL_FOOTPRINT
from hardware.sim.loop import loop_ac_resistance_ohm, loop_inductance_h


MODELS_DIR = Path(__file__).parent / "models"

_REF_PATTERN = re.compile(r"^(\D*)(\d*)$")


def value_to_spice(value: str) -> str:
    """Reduce a part value string such as "220p C0G 2%" to a token ngspice accepts."""
    tokens = value.split()
    token = tokens[0] if tokens else ""
    if token.endswith("H"):
        token = token[:-1]
    if token.endswith("R"):
        token = token[:-1]
    if token.endswith("M"):
        # Bare SPICE "M" means milli, not mega, so spell out the mega suffix.
        token = token[:-1] + "meg"
    if not token:
        raise ValueError(f"value {value!r} has no usable SPICE token")
    return token


@dataclass(frozen=True)
class SpiceModel:
    """A datasheet-anchored device model: its subckt/model name, ordered pin
    names, and the include file that defines it."""

    name: str
    pins: tuple[str, ...]
    include: str


MODELS: dict[str, SpiceModel] = {
    "BSS123": SpiceModel(name="BSS123", pins=("D", "G", "S"), include="bss123.lib"),
    "BSS84": SpiceModel(name="BSS84", pins=("D", "G", "S"), include="bss84.lib"),
}

# Diodes reference their .model name directly from a D card, so unlike the VDMOS
# switch models these need no .SUBCKT wrapper. Pins are ordered (anode, cathode).
DIODE_MODELS: dict[str, SpiceModel] = {
    "BAP64-02": SpiceModel(name="BAP64_02", pins=("A", "K"), include="bap64_02.lib"),
    "BAR64-02V": SpiceModel(name="BAR64_02V", pins=("A", "K"), include="bar64_02v.lib"),
}


def model_includes(*models: SpiceModel) -> str:
    """Emit deduplicated `.include` lines for the given device models, in a
    stable order, so a testbench deck can pull in exactly the libraries it uses."""
    seen: dict[str, None] = {}
    for model in models:
        seen.setdefault(model.include, None)
    return "\n".join(f'.include "{MODELS_DIR / include}"' for include in seen)


def _sanitize_net_name(name: str) -> str:
    if name == "GND":
        return "0"
    characters: list[str] = []
    for character in name:
        if character == "+":
            characters.append("P")
        elif character == "-":
            characters.append("N")
        elif character.isalnum():
            characters.append(character)
        else:
            characters.append("_")
    return "".join(characters)


def _ref_sort_key(ref: str) -> tuple[str, int]:
    match = _REF_PATTERN.match(ref)
    if match is None:
        return (ref, 0)
    prefix, digits = match.group(1), match.group(2)
    return (prefix, int(digits) if digits else 0)


def _node_by_num(part: Any, number: str) -> str:
    for pin in part.pins:
        if pin.num == number:
            return _sanitize_net_name(str(pin.net.name))
    raise ValueError(f"part {part.ref} has no pin numbered {number}")


def _node_by_name(part: Any, pin_name: str) -> str:
    for pin in part.pins:
        if pin.name == pin_name:
            return _sanitize_net_name(str(pin.net.name))
    raise ValueError(f"part {part.ref} has no pin named {pin_name}")


def _two_pin_line(prefix: str, part: Any, ref: str) -> str:
    node_1 = _node_by_num(part, "1")
    node_2 = _node_by_num(part, "2")
    value = value_to_spice(str(part.value))
    return f"{prefix}{ref} {node_1} {node_2} {value}"


def _mosfet_line(part: Any, ref: str, model: SpiceModel) -> str:
    nodes = " ".join(_node_by_name(part, pin_name) for pin_name in model.pins)
    return f"X{ref} {nodes} {model.name}"


def _diode_line(part: Any, ref: str, model: SpiceModel) -> str:
    anode, cathode = (_node_by_name(part, pin_name) for pin_name in model.pins)
    return f"D{ref} {anode} {cathode} {model.name}"


def _coil_lines(part: Any, ref: str) -> tuple[str, str]:
    node_1 = _node_by_num(part, "1")
    node_2 = _node_by_num(part, "2")
    # The footprint is copper trace, not a lumped part, so it expands to an L
    # plus its series R, both derived from the routed loop geometry.
    internal_node = _sanitize_net_name(f"{ref}_INT")
    inductor_line = f"L{ref} {node_1} {internal_node} {loop_inductance_h():.6e}"
    resistor_line = f"R{ref}_SERIES {internal_node} {node_2} {loop_ac_resistance_ohm():.4f}"
    return (inductor_line, resistor_line)


def emit_subckt(circuit: Circuit, name: str, ports: tuple[Net, ...]) -> str:
    port_nodes = " ".join(_sanitize_net_name(str(net.name)) for net in ports)
    lines: list[str] = [f".SUBCKT {name} {port_nodes}"]
    parts = sorted(circuit.parts, key=lambda part: _ref_sort_key(str(part.ref)))
    for part in parts:
        ref = str(part.ref)
        if ref.startswith("#"):
            continue
        if str(getattr(part, "fitted", "yes")) == "DNP":
            continue
        footprint = str(getattr(part, "footprint", ""))
        mpn = str(getattr(part, "manf_num", ""))
        if footprint == COIL_FOOTPRINT:
            lines.extend(_coil_lines(part, ref))
        elif mpn in MODELS:
            lines.append(_mosfet_line(part, ref, MODELS[mpn]))
        elif mpn in DIODE_MODELS:
            lines.append(_diode_line(part, ref, DIODE_MODELS[mpn]))
        elif ref[:1] == "R":
            lines.append(_two_pin_line("R", part, ref))
        elif ref[:1] == "C":
            lines.append(_two_pin_line("C", part, ref))
        elif ref[:1] == "L":
            # A bare inductor (RF bias choke); the coil footprint is handled above.
            lines.append(_two_pin_line("L", part, ref))
        else:
            raise ValueError(f"unsupported part for spice emission: {ref}")
    lines.append(f".ends {name}")
    return "\n".join(lines) + "\n"
