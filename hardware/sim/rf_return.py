"""Extract the hub's 13.56 MHz return path from the routed copper.

V4 asks whether the back-copper region reserved under the reader's match and
the run to the matrix connector is wide enough, since on a two-layer board it
is the whole return path. That is a magnetoquasistatic question, not a
radiating one: at 13.56 MHz the wavelength is 22 m and the board is 162 mm, so
there is nothing on it that is electrically large. FastHenry solves exactly
that case, and `hardware/tests/test_rf_return.py` first checks it against the
Grover model already used for the matrix loop before trusting it here.

The trace geometry is read from the generated board, so the extraction is of
the copper that will be fabricated rather than of a sketch of it.
"""

import os
import re
import subprocess
from dataclasses import dataclass
from math import hypot, pi
from pathlib import Path

from hardware.sim.copper import COPPER_THICKNESS_M, TrackSegment, read_copper


FASTHENRY = os.environ.get("FASTHENRY", str(Path.home() / ".local" / "bin" / "fasthenry"))
GENERATED_DIR = Path(__file__).parent / "generated" / "hub" / "rf"
HUB_BOARD = Path(__file__).parent.parent / "pcb" / "generated" / "hub" / "hub.kicad_pcb"

CARRIER_HZ = 13.56e6

# docs/verification/v2-static.yaml records the hub as two copper layers in a
# 1.0 mm board, so the dielectric between the trace and its return plane is the
# board less both claddings.
BOARD_THICKNESS_MM = 1.0
COPPER_THICKNESS_MM = COPPER_THICKNESS_M * 1e3
DIELECTRIC_MM = BOARD_THICKNESS_MM - 2.0 * COPPER_THICKNESS_MM

# FastHenry works in siemens per its length unit, so mm.
COPPER_SIGMA_PER_MM = 5.8e4

# The reserve as recorded in docs/verification/v2-static.yaml.
RESERVE = (122.0, 10.0, 156.0, 40.0)

# Enough plane discretisation that the return current can concentrate under the
# trace instead of being forced to spread across a coarse cell.
PLANE_SEG1 = 68
PLANE_SEG2 = 60


@dataclass(frozen=True)
class ReturnPath:
    inductance_h: float
    resistance_ohm: float


def rf_segments(board: Path = HUB_BOARD, net: str = "RF_BUS") -> tuple[TrackSegment, ...]:
    return tuple(
        segment
        for segment in read_copper(board).segments
        if segment.net == net and segment.layer == "F.Cu"
    )


def _endpoints(segments: tuple[TrackSegment, ...]) -> tuple[tuple[float, float], ...]:
    """The two ends of the run: the points only one segment touches."""
    counts: dict[tuple[float, float], int] = {}
    for segment in segments:
        for point in (segment.start, segment.end):
            counts[point] = counts.get(point, 0) + 1
    leaves = tuple(point for point, count in counts.items() if count == 1)
    if len(leaves) != 2:
        raise ValueError(f"expected a two-ended run, found {len(leaves)} ends")
    return leaves


def _node_name(point: tuple[float, float]) -> str:
    return f"N{str(point[0]).replace('.', '_').replace('-', 'm')}x{str(point[1]).replace('.', '_').replace('-', 'm')}"


def deck(
    segments: tuple[TrackSegment, ...],
    reserve: tuple[float, float, float, float] = RESERVE,
) -> str:
    """A FastHenry input placing the routed trace over the reserved plane."""
    x_min, y_min, x_max, y_max = reserve
    source, sink = _endpoints(segments)
    points = sorted({point for s in segments for point in (s.start, s.end)})
    lines = [
        "* Hub RF run over its reserved back-copper return, from the routed board.",
        ".units mm",
        f".default sigma={COPPER_SIGMA_PER_MM} nhinc=1 nwinc=3 h={COPPER_THICKNESS_MM}",
        "",
    ]
    for point in points:
        lines.append(f"{_node_name(point)} x={point[0]} y={point[1]} z={DIELECTRIC_MM}")
    lines.append("")
    for index, segment in enumerate(segments, start=1):
        lines.append(
            f"E{index} {_node_name(segment.start)} {_node_name(segment.end)}"
            f" w={segment.width_mm} h={COPPER_THICKNESS_MM}"
        )
    lines += [
        "",
        f"G1 x1={x_min} y1={y_min} z1=0 x2={x_max} y2={y_min} z2=0"
        f" x3={x_max} y3={y_max} z3=0",
        f"+ thick={COPPER_THICKNESS_MM} seg1={PLANE_SEG1} seg2={PLANE_SEG2}",
        f"+ sigma={COPPER_SIGMA_PER_MM}",
        f"+ Nsrc ({source[0]},{source[1]},0)",
        f"+ Nsink ({sink[0]},{sink[1]},0)",
        "",
        f".equiv {_node_name(sink)} Nsink",
        f".external {_node_name(source)} Nsrc",
        f".freq fmin={CARRIER_HZ} fmax={CARRIER_HZ} ndec=1",
        ".end",
        "",
    ]
    return "\n".join(lines)


_IMPEDANCE = re.compile(r"([-\d.eE+]+)\s+([-\d.eE+]+)j")


def solve(text: str, name: str) -> ReturnPath:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    deck_path = GENERATED_DIR / f"{name}.inp"
    deck_path.write_text(text, encoding="utf-8")
    if not Path(FASTHENRY).is_file():
        raise FileNotFoundError(
            f"fasthenry not found at {FASTHENRY}; set FASTHENRY to its path"
        )
    subprocess.run(
        (FASTHENRY, deck_path.name),
        cwd=GENERATED_DIR,
        check=True,
        capture_output=True,
    )
    matrix = (GENERATED_DIR / "Zc.mat").read_text(encoding="utf-8")
    match = None
    for line in matrix.splitlines():
        found = _IMPEDANCE.search(line)
        if found is not None:
            match = found
    if match is None:
        raise ValueError("no impedance row in Zc.mat")
    resistance = float(match.group(1))
    reactance = float(match.group(2))
    return ReturnPath(
        inductance_h=reactance / (2.0 * pi * CARRIER_HZ),
        resistance_ohm=resistance,
    )


def return_corridor_mm() -> float:
    """How far the return current spreads either side of the trace.

    In a plane the return concentrates under its trace with a 1/(1+(x/h)^2)
    distribution, so about 97 percent of it is inside three dielectric
    thicknesses. That is the width of copper the reserve has to keep intact.
    """
    return 3.0 * DIELECTRIC_MM


def _segment_distance_mm(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> float:
    def point_to_segment(
        point: tuple[float, float],
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> float:
        dx, dy = end[0] - start[0], end[1] - start[1]
        length_sq = dx * dx + dy * dy
        t = (
            0.0
            if length_sq == 0.0
            else max(
                0.0,
                min(
                    1.0,
                    ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy)
                    / length_sq,
                ),
            )
        )
        return hypot(point[0] - (start[0] + t * dx), point[1] - (start[1] + t * dy))

    return min(
        point_to_segment(first[0], *second),
        point_to_segment(first[1], *second),
        point_to_segment(second[0], *first),
        point_to_segment(second[1], *first),
    )


def nearest_return_interruption_mm(board: Path = HUB_BOARD) -> float:
    """Distance from the RF run to the closest back-copper signal track.

    Anything on the back layer that is not ground is a slot in the return, and
    a slot inside the corridor forces the return current to detour around it.
    """
    back_signal = tuple(
        segment
        for segment in read_copper(board).segments
        if segment.layer == "B.Cu" and segment.net != "GND"
    )
    return min(
        _segment_distance_mm((rf.start, rf.end), (other.start, other.end))
        for rf in rf_segments(board)
        for other in back_signal
    )


def routed_return(
    reserve: tuple[float, float, float, float] = RESERVE, name: str = "reserve"
) -> ReturnPath:
    return solve(deck(rf_segments(), reserve), name)
