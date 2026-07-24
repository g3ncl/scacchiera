"""ngspice testbenches for the matrix switch cell and the 16-cell shared bus.

Three questions, per docs/hardware/criteria.yaml: does a selected line resonate
in band, how suppressed is a deselected line, and does the steering deliver the
forward bias current from the 3V3 rail alone. The bus deck answers the first
question in the only configuration the board ever runs: one line selected, the
other fifteen presenting their off-state capacitance to the same bus.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from skidl import Circuit, Net

from hardware.pcb.matrix import matrix_cell
from hardware.pcb.matrix_geometry import LINE_COUNT
from hardware.sim.cell_metrics import SwitchCellResult, analyze, parse_wrdata
from hardware.sim.spice import DIODE_MODELS, MODELS, emit_subckt, model_includes


GENERATED_DIR = Path(__file__).parent / "generated" / "matrix"
CELL_SUBCKT = "matrix_cell_se"
BUS_SUBCKT = "matrix_bus16"
BIAS_RAIL_V = 3.3
STATES: tuple[Literal["on"], Literal["off"]] = ("on", "off")

_RAIL_CURRENT = re.compile(r"i\(vbias\)\s*=\s*([-\d.eE+]+)")


@dataclass(frozen=True)
class MatrixRfResult:
    cell: SwitchCellResult
    bias_on_a: float
    bias_off_a: float
    bus_resonance_hz: float


def _build_cell() -> tuple[Circuit, tuple[Net, ...]]:
    circuit = Circuit(name=CELL_SUBCKT)
    rf = Net("RF_BUS", circuit=circuit)
    gnd = Net("GND", circuit=circuit)
    vbias = Net("VBIAS", circuit=circuit)
    sel_n = Net("SEL0_N", circuit=circuit)
    matrix_cell(circuit, 0, rf, gnd, vbias, sel_n)
    return circuit, (rf, vbias, sel_n)


def _build_bus() -> tuple[Circuit, tuple[Net, ...]]:
    circuit = Circuit(name=BUS_SUBCKT)
    rf = Net("RF_BUS", circuit=circuit)
    gnd = Net("GND", circuit=circuit)
    vbias = Net("VBIAS", circuit=circuit)
    sel_lines = tuple(Net(f"SEL{index}_N", circuit=circuit) for index in range(LINE_COUNT))
    for index in range(LINE_COUNT):
        matrix_cell(circuit, index, rf, gnd, vbias, sel_lines[index])
    return circuit, (rf, vbias, *sel_lines)


def _includes() -> str:
    return model_includes(MODELS["BSS123"], MODELS["BSS84"], DIODE_MODELS["BAP64-02"])


def _testbench_tail(output: Path) -> list[str]:
    return [
        ".ac dec 200 1meg 30meg",
        ".control",
        "run",
        "let source_mag = mag(i(VP))",
        "let coil_mag = mag(l.x1.ll2#branch)",
        f"wrdata {output} source_mag coil_mag",
        "op",
        "print i(VBIAS)",
        "quit",
        ".endc",
        ".end",
    ]


def cell_deck(state: Literal["on", "off"], subckt_text: str) -> str:
    sel_volts = 0.0 if state == "on" else BIAS_RAIL_V
    lines = [
        f"Matrix switch cell, {state} state",
        _includes(),
        subckt_text.rstrip("\n"),
        f"X1 rf vbias seln {CELL_SUBCKT}",
        f"VBIAS vbias 0 DC {BIAS_RAIL_V}",
        f"VSEL seln 0 DC {sel_volts}",
        "VP vpsrc 0 DC 0 AC 1",
        "RSRC vpsrc rf 1",
        *_testbench_tail(GENERATED_DIR / f"cell_{state}.dat"),
    ]
    return "\n".join(lines) + "\n"


def bus_deck(subckt_text: str) -> str:
    # Line 0 selected, fifteen lines deselected: the only legal bus state.
    sel_nodes = " ".join(f"sel{index}" for index in range(LINE_COUNT))
    lines = [
        "Matrix 16-line shared bus, line 0 selected",
        _includes(),
        subckt_text.rstrip("\n"),
        f"X1 rf vbias {sel_nodes} {BUS_SUBCKT}",
        f"VBIAS vbias 0 DC {BIAS_RAIL_V}",
        "VSEL0 sel0 0 DC 0",
        *(
            f"VSEL{index} sel{index} 0 DC {BIAS_RAIL_V}"
            for index in range(1, LINE_COUNT)
        ),
        "VP vpsrc 0 DC 0 AC 1",
        "RSRC vpsrc rf 1",
        *_testbench_tail(GENERATED_DIR / "bus.dat"),
    ]
    return "\n".join(lines) + "\n"


def _run_deck(deck_text: str, deck_path: Path) -> str:
    deck_path.parent.mkdir(parents=True, exist_ok=True)
    deck_path.write_text(deck_text, encoding="utf-8")
    completed = subprocess.run(
        ("ngspice", "-b", str(deck_path)), check=True, capture_output=True, text=True
    )
    return completed.stdout


def _rail_current(stdout: str) -> float:
    match = _RAIL_CURRENT.search(stdout.lower())
    if match is None:
        raise RuntimeError("ngspice output did not report i(VBIAS)")
    return abs(float(match.group(1)))


def run() -> MatrixRfResult:
    cell_circuit, cell_ports = _build_cell()
    cell_subckt = emit_subckt(cell_circuit, CELL_SUBCKT, cell_ports)
    rail: dict[str, float] = {}
    for state in STATES:
        rail[state] = _rail_current(
            _run_deck(cell_deck(state, cell_subckt), GENERATED_DIR / f"cell_{state}.cir")
        )
    cell_result = analyze(
        parse_wrdata(GENERATED_DIR / "cell_on.dat"),
        parse_wrdata(GENERATED_DIR / "cell_off.dat"),
    )

    bus_circuit, bus_ports = _build_bus()
    bus_subckt = emit_subckt(bus_circuit, BUS_SUBCKT, bus_ports)
    _run_deck(bus_deck(bus_subckt), GENERATED_DIR / "bus.cir")
    bus_points = parse_wrdata(GENERATED_DIR / "bus.dat")
    bus_resonance = min(bus_points, key=lambda point: point.source_a)

    return MatrixRfResult(
        cell=cell_result,
        bias_on_a=rail["on"],
        bias_off_a=rail["off"],
        bus_resonance_hz=bus_resonance.frequency_hz,
    )


if __name__ == "__main__":
    result = run()
    print(f"cell resonance {result.cell.resonance_hz / 1e6:.3f} MHz")
    print(f"off/on suppression {result.cell.suppression_db:.1f} dB")
    print(f"bias on {result.bias_on_a * 1e3:.2f} mA, off {result.bias_off_a * 1e6:.2f} uA")
    print(f"bus resonance {result.bus_resonance_hz / 1e6:.3f} MHz")
