"""Validate the light bar's supply loop against the routed copper in ngspice.

Builds a resistor network from every LED_5V and GND track segment in the
generated board file, loads it with all 17 pixels lit white, and reports the
worst supply-loop droop (feed drop plus ground rise) seen by any LED. The
network is solved by ngspice, not analytically, per the Milestone 3 rule.
"""

import re
import subprocess
from dataclasses import dataclass
from math import hypot
from pathlib import Path

from hardware.pcb.lightbar_geometry import CONNECTOR_X, CONNECTOR_Y, LED_COUNT, LED_Y, led_x
from hardware.sim.copper import Copper, read_copper, split_at_junctions


SUPPLY_NET = "LED_5V"
GROUND_NET = "GND"
SUPPLY_VOLTAGE_V = 5.0
# WS2812C-2020 datasheet: about 5 mA per color channel, so a white pixel
# draws all three at once. This is the worst legitimate load.
LED_WHITE_CURRENT_A = 0.015
# Floor for zero-length stubs so ngspice never sees a 0 ohm resistor.
MINIMUM_RESISTANCE_OHM = 1e-6

# A node is a track endpoint, keyed by layer and 1 um quantized position; a
# via at the same position joins the layers into one shared node.
NodeKey = tuple[str, int, int]
Resistor = tuple[NodeKey, NodeKey, float]

_VOLTAGE_LINE = re.compile(r"v\((\S+)\)\s*=\s*([-+0-9.eE]+)")


@dataclass(frozen=True)
class SupplyResult:
    droops_v: tuple[float, ...]

    @property
    def worst_droop_v(self) -> float:
        return max(self.droops_v)


def _quantize(point: tuple[float, float]) -> tuple[int, int]:
    return (round(point[0] * 1000.0), round(point[1] * 1000.0))


def _network(copper: Copper, net: str) -> tuple[list[Resistor], dict[NodeKey, tuple[float, float]]]:
    vias = {_quantize(via.position) for via in copper.vias if via.net == net}

    def key(layer: str, point: tuple[float, float]) -> NodeKey:
        quantized = _quantize(point)
        return ("via", *quantized) if quantized in vias else (layer, *quantized)

    net_segments = tuple(segment for segment in copper.segments if segment.net == net)
    junction_points = {segment.start for segment in net_segments}
    junction_points |= {segment.end for segment in net_segments}
    junction_points |= {via.position for via in copper.vias if via.net == net}

    resistors: list[Resistor] = []
    positions: dict[NodeKey, tuple[float, float]] = {}
    for segment in split_at_junctions(net_segments, junction_points):
        start = key(segment.layer, segment.start)
        end = key(segment.layer, segment.end)
        if start == end:
            continue
        resistors.append((start, end, max(segment.resistance_ohm(), MINIMUM_RESISTANCE_OHM)))
        positions[start] = segment.start
        positions[end] = segment.end
    if not resistors:
        raise ValueError(f"no routed copper found for net {net}")
    return resistors, positions


def _nearest(positions: dict[NodeKey, tuple[float, float]], point: tuple[float, float]) -> NodeKey:
    return min(
        positions,
        key=lambda node: hypot(positions[node][0] - point[0], positions[node][1] - point[1]),
    )


def _run_ngspice(deck: str, work_dir: Path) -> dict[str, float]:
    work_dir.mkdir(parents=True, exist_ok=True)
    deck_path = work_dir / "lightbar_supply.cir"
    deck_path.write_text(deck, encoding="utf-8")
    result = subprocess.run(
        ("ngspice", "-b", str(deck_path)),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ngspice failed:\n{result.stdout}\n{result.stderr}")
    return {name: float(value) for name, value in _VOLTAGE_LINE.findall(result.stdout)}


def validate_supply(board: Path, work_dir: Path) -> SupplyResult:
    copper = read_copper(board)
    supply_resistors, supply_positions = _network(copper, SUPPLY_NET)
    ground_resistors, ground_positions = _network(copper, GROUND_NET)

    names: dict[NodeKey, str] = {}
    connector = (CONNECTOR_X, CONNECTOR_Y)
    names[_nearest(ground_positions, connector)] = "0"
    for prefix, keys in (("s", supply_positions), ("g", ground_positions)):
        for node in keys:
            names.setdefault(node, f"{prefix}{len(names)}")

    lines = ["* light bar supply loop, extracted from the routed board"]
    for index, (start, end, ohm) in enumerate(supply_resistors + ground_resistors):
        lines.append(f"R{index} {names[start]} {names[end]} {ohm:.6e}")
    feed = names[_nearest(supply_positions, connector)]
    lines.append(f"Vsupply {feed} 0 DC {SUPPLY_VOLTAGE_V}")

    led_nodes: list[tuple[str, str]] = []
    for index in range(LED_COUNT):
        position = (led_x(index), LED_Y)
        supply_node = names[_nearest(supply_positions, position)]
        ground_node = names[_nearest(ground_positions, position)]
        led_nodes.append((supply_node, ground_node))
        lines.append(f"Iled{index} {supply_node} {ground_node} DC {LED_WHITE_CURRENT_A}")

    probes = sorted({node for pair in led_nodes for node in pair if node != "0"})
    lines.append(".control")
    lines.append("op")
    for probe in probes:
        lines.append(f"print v({probe})")
    lines.append(".endc")
    lines.append(".end")

    voltages = _run_ngspice("\n".join(lines) + "\n", work_dir)
    voltages["0"] = 0.0
    droops = tuple(
        (SUPPLY_VOLTAGE_V - voltages[supply_node]) + voltages[ground_node]
        for supply_node, ground_node in led_nodes
    )
    return SupplyResult(droops_v=droops)
