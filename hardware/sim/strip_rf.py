"""What the harnesses and the spines do to the shared bus.

The monolithic matrix board's sixteen cells hang off one node. The split puts a
harness and a length of spine between the reader and every one of them, and this
deck is the only place that says how much that costs.

Two things are being asked, and they are not the same question:

1. **Does the bus still resonate in band at all?** The harness is common to all
   sixteen lines by construction (equal-length harnesses, see
   `strip_geometry.HARNESS_LENGTH_MM`), so it detunes every line together, which
   is what a tuning capacitor is for.
2. **How far apart do the sixteen lines end up?** The spine ladder is *not*
   common: line 0 taps the bus beside the feed and line 15 taps it two spines
   away. That spread cannot be tuned out with one capacitor value, and the
   answer decides whether the DNP trim pads already on every strip are enough or
   whether the topology has to change.

The cells themselves are the same `matrix_cell` objects the matrix board and its
own SPICE deck build, so nothing about the switch is being re-modelled here.
Only the interconnect between them is new.
"""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from skidl import Circuit, Net

from hardware.pcb.matrix import matrix_cell
from hardware.pcb.matrix_geometry import LINE_COUNT, ROW_COUNT
from hardware.pcb.strip_geometry import (
    HARNESS_LENGTH_MM,
    SPINE_LINK_IN_X,
    SPINE_LINK_LENGTH_MM,
    SPINE_RF_PIN_OFFSET,
    SPINE_RF_WIDTH,
    spine_bus_span_mm,
    spine_bus_tap_x,
)
from hardware.sim.cell_metrics import SweepPoint, parse_wrdata, resonance_dip
from hardware.sim.interconnect import (
    CONNECTOR_INDUCTANCE_MAX_H,
    CONNECTOR_INDUCTANCE_MIN_H,
    CONNECTOR_INDUCTANCE_NOMINAL_H,
    harness_inductance_h,
    microstrip_inductance_per_mm,
)
from hardware.sim.spice import DIODE_MODELS, MODELS, emit_subckt, model_includes


GENERATED_DIR = Path(__file__).parent / "generated" / "strip"
BUS_SUBCKT = "strip_bus16"
BIAS_RAIL_V = 3.3
# The spine's back copper is a solid pour 1.0 mm under its bus.
SPINE_DIELECTRIC_MM = 1.0

# 0.115 percent per grid step, an order of magnitude finer than the spread.
SWEEP_POINTS_PER_DECADE = 3000
SWEEP_LOW_HZ = 8.0e6
SWEEP_HIGH_HZ = 20.0e6


@dataclass(frozen=True)
class LineResult:
    line: int
    resonance_hz: float
    series_inductance_h: float


@dataclass(frozen=True)
class SplitBusResult:
    """One sweep of all sixteen lines at one connector-inductance corner."""

    connector_inductance_h: float
    lines: tuple[LineResult, ...]

    @property
    def lowest_hz(self) -> float:
        return min(line.resonance_hz for line in self.lines)

    @property
    def highest_hz(self) -> float:
        return max(line.resonance_hz for line in self.lines)

    @property
    def spread_fraction(self) -> float:
        """Peak-to-peak resonance spread as a fraction of the mean.

        This is the number the trim pads have to cover, and the number one
        capacitor value cannot.
        """
        mean = (self.highest_hz + self.lowest_hz) / 2.0
        return (self.highest_hz - self.lowest_hz) / mean


def spine_segment_inductance_h(length_mm: float) -> float:
    return microstrip_inductance_per_mm(SPINE_RF_WIDTH, SPINE_DIELECTRIC_MM) * length_mm


def series_inductance_h(line: int, connector_inductance_h: float) -> float:
    """Everything in series between the reader and one strip's DC block.

    The path is: hub link, then along the first spine to the socket, and for the
    upper eight lines the whole of the first spine plus the spine-to-spine link
    as well, then the strip's own harness.
    """
    link = harness_inductance_h(SPINE_LINK_LENGTH_MM, connector_inductance_h)
    harness = harness_inductance_h(HARNESS_LENGTH_MM, connector_inductance_h)
    socket = line % ROW_COUNT
    # Tap positions, not placement positions. Pin 2 sits 2.5 mm off a housing's
    # centre, and the link out is rotated, so a centre-to-centre reading would
    # under-count the drawn bus by 5 mm.
    feed = SPINE_LINK_IN_X - SPINE_RF_PIN_OFFSET
    along = spine_segment_inductance_h(spine_bus_tap_x(socket) - feed)
    total = link + along + harness
    if line >= ROW_COUNT:
        # Through the whole of the first spine and the link to the second.
        total += spine_segment_inductance_h(spine_bus_span_mm()) + link
    return total


def _build_bus() -> tuple[Circuit, tuple[Net, ...]]:
    """Sixteen cells, each on its own tap rather than a shared node.

    The deck then wires the taps together through the interconnect, which is the
    whole point: on the monolith they really are one node, and pretending they
    still are is exactly the error this deck exists to avoid.
    """
    circuit = Circuit(name=BUS_SUBCKT)
    gnd = Net("GND", circuit=circuit)
    vbias = Net("VBIAS", circuit=circuit)
    taps = tuple(Net(f"TAP{index}", circuit=circuit) for index in range(LINE_COUNT))
    sel_lines = tuple(Net(f"SEL{index}_N", circuit=circuit) for index in range(LINE_COUNT))
    for index in range(LINE_COUNT):
        matrix_cell(circuit, index, taps[index], gnd, vbias, sel_lines[index])
    return circuit, (*taps, vbias, *sel_lines)


def _includes() -> str:
    return model_includes(
        MODELS["BSS123-7-F"], MODELS["BSS84-7-F"], DIODE_MODELS["BAR64-02V"]
    )


# A stand-in for "no interconnect at all", used by the monolithic reference.
# Not zero: ngspice will take a zero-henry inductor, but a value six orders
# below the smallest real one keeps the element in the same place in the matrix
# so the two decks differ in one number and nothing else.
NEGLIGIBLE_H = 1.0e-15


def bus_deck(
    subckt_text: str,
    selected: int,
    series_h: Callable[[int], float],
    output: Path,
) -> str:
    """One line selected, fifteen deselected, behind a given interconnect."""
    tap_nodes = " ".join(f"tap{index}" for index in range(LINE_COUNT))
    sel_nodes = " ".join(f"sel{index}" for index in range(LINE_COUNT))
    lines = [
        f"Split sensing plane, line {selected} selected",
        _includes(),
        subckt_text.rstrip("\n"),
        f"X1 {tap_nodes} vbias {sel_nodes} {BUS_SUBCKT}",
        f"VBIAS vbias 0 DC {BIAS_RAIL_V}",
        "VP vpsrc 0 DC 0 AC 1",
        "RSRC vpsrc rf 1",
    ]
    for index in range(LINE_COUNT):
        volts = 0.0 if index == selected else BIAS_RAIL_V
        lines.append(f"VSEL{index} sel{index} 0 DC {volts}")
    # The interconnect as a lumped series inductor per line. A ladder would
    # share the spine segments between neighbouring taps; a per-line series
    # element does not, and the difference is that a ladder also lets one tank
    # load another through the shared copper. That coupling is second order
    # against a 0.2 ohm segment, and modelling each path independently is what
    # makes series_inductance_h readable straight off the geometry.
    for index in range(LINE_COUNT):
        lines.append(f"LNK{index} rf tap{index} {series_h(index):.6e}")
    coil = f"l.x1.ll{selected * 2 + 2}#branch"
    lines += [
        # dec 3000 over a narrow band, not the matrix deck's dec 200 over
        # 1 to 30 MHz. At 200 points per decade a grid step is 1.16 percent,
        # which is larger than the whole spread this deck exists to measure: the
        # first run quantised every line onto one of two adjacent grid points.
        f".ac dec {SWEEP_POINTS_PER_DECADE} {SWEEP_LOW_HZ:.0f} {SWEEP_HIGH_HZ:.0f}",
        ".control",
        "run",
        "let source_mag = mag(i(VP))",
        f"let coil_mag = mag({coil})",
        f"wrdata {output} source_mag coil_mag",
        "quit",
        ".endc",
        ".end",
    ]
    return "\n".join(lines) + "\n"


def _run_deck(deck_text: str, deck_path: Path) -> str:
    deck_path.parent.mkdir(parents=True, exist_ok=True)
    deck_path.write_text(deck_text, encoding="utf-8")
    completed = subprocess.run(
        ("ngspice", "-b", str(deck_path)), check=True, capture_output=True, text=True
    )
    return completed.stdout


def _sweep(
    series_h: Callable[[int], float], tag: str, connector_inductance_h: float
) -> SplitBusResult:
    circuit, ports = _build_bus()
    subckt = emit_subckt(circuit, BUS_SUBCKT, ports)
    results: list[LineResult] = []
    for line in range(LINE_COUNT):
        data = GENERATED_DIR / f"{tag}_line{line}.dat"
        _run_deck(
            bus_deck(subckt, line, series_h, data),
            GENERATED_DIR / f"{tag}_line{line}.cir",
        )
        points: list[SweepPoint] = parse_wrdata(data)
        results.append(
            LineResult(
                line=line,
                resonance_hz=resonance_dip(points).frequency_hz,
                series_inductance_h=series_h(line),
            )
        )
    return SplitBusResult(
        connector_inductance_h=connector_inductance_h, lines=tuple(results)
    )


def run(
    connector_inductance_h: float = CONNECTOR_INDUCTANCE_NOMINAL_H,
) -> SplitBusResult:
    return _sweep(
        lambda line: series_inductance_h(line, connector_inductance_h),
        f"split{connector_inductance_h * 1e9:.0f}",
        connector_inductance_h,
    )


def run_monolith_reference() -> SplitBusResult:
    """The same sixteen cells with the interconnect removed.

    This is the controlled comparison the whole partition rests on. Running the
    matrix board's own deck instead would compare two sweep grids and two
    testbenches as well as two topologies; here the circuit, the models, the
    sweep and the analysis are identical and the interconnect is the only
    difference between the two numbers.
    """
    return _sweep(lambda _: NEGLIGIBLE_H, "monolith", 0.0)


def run_corners() -> tuple[SplitBusResult, ...]:
    """The bounding connector-inductance corners of assumption A11."""
    return tuple(
        run(value)
        for value in (
            CONNECTOR_INDUCTANCE_MIN_H,
            CONNECTOR_INDUCTANCE_NOMINAL_H,
            CONNECTOR_INDUCTANCE_MAX_H,
        )
    )


if __name__ == "__main__":
    reference = run_monolith_reference()
    print(
        f"monolithic reference {reference.lowest_hz / 1e6:.3f} to"
        f" {reference.highest_hz / 1e6:.3f} MHz,"
        f" spread {reference.spread_fraction * 100:.2f} percent"
    )
    for result in run_corners():
        print(f"connector {result.connector_inductance_h * 1e9:.0f} nH per mated pair")
        for line in result.lines:
            print(
                f"  line {line.line:2d}  series {line.series_inductance_h * 1e9:6.1f} nH"
                f"  resonance {line.resonance_hz / 1e6:.3f} MHz"
            )
        print(
            f"  band {result.lowest_hz / 1e6:.3f} to {result.highest_hz / 1e6:.3f} MHz,"
            f" spread {result.spread_fraction * 100:.2f} percent"
        )
