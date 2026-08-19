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
from math import pi
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


PLANE_LAYER = "B.Cu"


def rf_segments(board: Path = HUB_BOARD, net: str = "RF_BUS") -> tuple[TrackSegment, ...]:
    """Every routed segment of the net, on whichever layer it was routed.

    Filtering to one layer here is what made the first version of this module
    report a path that was not the routed path: RF_BUS drops to the back layer
    for 18.35 mm, and silently leaving that out produced an inductance for a
    net that does not exist.
    """
    return tuple(
        segment for segment in read_copper(board).segments if segment.net == net
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
    on_plane = tuple(s for s in segments if s.layer == PLANE_LAYER)
    if on_plane:
        raise NotImplementedError(
            f"{len(on_plane)} segment(s) of this net are routed on {PLANE_LAYER}, "
            "the same layer as the return plane, so it cannot be modelled as a "
            "trace over a plane. Slot the plane and place those segments in the "
            "slot before trusting any number from here."
        )
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
    # FastHenry's exit status is undefined: its K&R main falls off the end, so
    # the code varies with build and deck. Success is judged by the artifact:
    # a fresh impedance matrix that parses, not a register's leftovers.
    matrix_path = GENERATED_DIR / "Zc.mat"
    matrix_path.unlink(missing_ok=True)
    completed = subprocess.run(
        (FASTHENRY, deck_path.name),
        cwd=GENERATED_DIR,
        check=False,
        capture_output=True,
    )
    if not matrix_path.is_file():
        tail = completed.stdout.decode(errors="replace")[-400:]
        raise RuntimeError(f"fasthenry produced no impedance matrix: {tail}")
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


def routed_return(
    reserve: tuple[float, float, float, float] = RESERVE, name: str = "reserve"
) -> ReturnPath:
    return solve(deck(rf_segments(), reserve), name)
