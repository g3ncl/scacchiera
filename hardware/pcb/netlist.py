"""Read the small subset of KiCad netlists needed by layout generators.

The s-expression parser is public: the SPICE validations reuse it to read the
generated .kicad_pcb files, extracting the real routed copper.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


SExpr: TypeAlias = str | list["SExpr"]


@dataclass(frozen=True)
class ComponentRecord:
    reference: str
    value: str
    footprint: str


@dataclass(frozen=True)
class NetRecord:
    name: str
    nodes: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Netlist:
    components: tuple[ComponentRecord, ...]
    nets: tuple[NetRecord, ...]

    def pad_nets(self) -> dict[tuple[str, str], str]:
        return {
            node: net.name
            for net in self.nets
            for node in net.nodes
        }


def _tokens(text: str) -> tuple[str, ...]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character.isspace():
            index += 1
        elif character in "()":
            tokens.append(character)
            index += 1
        elif character == '"':
            index += 1
            value: list[str] = []
            while index < len(text) and text[index] != '"':
                if text[index] == "\\" and index + 1 < len(text):
                    index += 1
                value.append(text[index])
                index += 1
            if index == len(text):
                raise ValueError("unterminated quoted string")
            tokens.append("".join(value))
            index += 1
        else:
            end = index
            while end < len(text) and not text[end].isspace() and text[end] not in "()":
                end += 1
            tokens.append(text[index:end])
            index = end
    return tuple(tokens)


def _parse(tokens: tuple[str, ...]) -> SExpr:
    stack: list[list[SExpr]] = []
    root: list[SExpr] = []
    current = root
    for token in tokens:
        if token == "(":
            child: list[SExpr] = []
            current.append(child)
            stack.append(current)
            current = child
        elif token == ")":
            if not stack:
                raise ValueError("unexpected closing parenthesis")
            current = stack.pop()
        else:
            current.append(token)
    if stack:
        raise ValueError("unterminated list")
    if len(root) != 1:
        raise ValueError("netlist must contain one root expression")
    return root[0]


def parse_sexpr(text: str) -> SExpr:
    return _parse(_tokens(text))


def sexpr_children(expression: list[SExpr], name: str) -> tuple[list[SExpr], ...]:
    return tuple(
        child
        for child in expression[1:]
        if isinstance(child, list) and child and child[0] == name
    )


def sexpr_value(expression: list[SExpr], name: str) -> str:
    matches = sexpr_children(expression, name)
    if len(matches) != 1 or len(matches[0]) < 2 or not isinstance(matches[0][1], str):
        raise ValueError(f"missing {name}")
    return matches[0][1]


def read_netlist(path: Path) -> Netlist:
    root = parse_sexpr(path.read_text(encoding="utf-8"))
    if not isinstance(root, list) or not root or root[0] != "export":
        raise ValueError("not a KiCad export netlist")
    components_section = sexpr_children(root, "components")[0]
    components = tuple(
        ComponentRecord(
            reference=sexpr_value(component, "ref"),
            value=sexpr_value(component, "value"),
            footprint=sexpr_value(component, "footprint"),
        )
        for component in sexpr_children(components_section, "comp")
    )
    nets_section = sexpr_children(root, "nets")[0]
    nets: list[NetRecord] = []
    for net in sexpr_children(nets_section, "net"):
        nodes = tuple(
            (sexpr_value(node, "ref"), sexpr_value(node, "pin"))
            for node in sexpr_children(net, "node")
        )
        nets.append(NetRecord(name=sexpr_value(net, "name"), nodes=nodes))
    return Netlist(components=components, nets=tuple(nets))
