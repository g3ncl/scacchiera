"""The electrical price of the split, measured rather than argued.

Two harnesses and two spines now sit between the reader and every tank. This
runs the same sixteen `matrix_cell` objects twice through one testbench, once
with that interconnect and once without, so the difference between the two
numbers is the interconnect and nothing else.

Slow by design. Sixteen lines times four interconnect cases is sixty-four
ngspice sweeps at 3000 points per decade, and the resolution is not optional:
at the matrix deck's own 200 points per decade a grid step is wider than the
entire spread being measured.

Every figure here is a bound rather than a nominal. The on-board bus is
autorouted, so each line is modelled at the whole net's routed length, which no
single tap-to-tap path can exceed.
"""

import math
import re
from pathlib import Path

import pytest
import yaml

from hardware.pcb.matrix_geometry import LINE_COUNT
from hardware.pcb.quad_geometry import LANES_PER_BOARD
from hardware.sim.interconnect import (
    CONNECTOR_INDUCTANCE_MAX_H,
    CONNECTOR_INDUCTANCE_MIN_H,
)
from hardware.sim.quad_rf import (
    ROUTED_BUS_LENGTH_MM,
    ROUTED_BUS_WIDTH_MM,
    SplitBusResult,
    run,
    run_corners,
    run_monolith_reference,
    series_inductance_h,
)


CRITERIA = yaml.safe_load(
    (Path(__file__).parent.parent.parent / "docs" / "hardware" / "criteria.yaml").read_text()
)["criteria"]


def _limit(name: str, bound: str) -> float:
    return float(CRITERIA[name]["limits"][bound])


@pytest.fixture(scope="module")
def corners() -> tuple[SplitBusResult, ...]:
    return run_corners()


@pytest.fixture(scope="module")
def reference() -> SplitBusResult:
    return run_monolith_reference()


def test_every_line_still_resonates_in_band(corners: tuple[SplitBusResult, ...]) -> None:
    """TEST-QUAD-RF-004."""
    low = _limit("QUAD-BUS-RESONANCE", "minimum")
    high = _limit("QUAD-BUS-RESONANCE", "maximum")
    for result in corners:
        for line in result.lines:
            megahertz = line.resonance_hz / 1e6
            assert low <= megahertz <= high, (
                f"line {line.line} at {megahertz:.3f} MHz with "
                f"{result.connector_inductance_h * 1e9:.0f} nH connectors"
            )


def test_the_sixteen_lines_stay_close_enough_to_trim(corners: tuple[SplitBusResult, ...]) -> None:
    """TEST-QUAD-RF-005.

    The one thing a single capacitor value cannot fix. The harness is common to
    all sixteen lines by construction, so it detunes them together and the
    nominal 220 pF absorbs it. The spine path is not common, and this is what it
    costs.
    """
    for result in corners:
        assert result.spread_fraction <= _limit(
            "QUAD-LINE-RESONANCE-SPREAD", "maximum"
        ), f"{result.spread_fraction:.4f} at {result.connector_inductance_h * 1e9:.0f} nH"


def test_the_interconnect_costs_around_one_percent_of_tuning(corners: tuple[SplitBusResult, ...], reference: SplitBusResult) -> None:
    """The controlled comparison: same cells, same sweep, interconnect removed.

    A tank behind a series inductor is not a tank with an inductor in it. The
    connector sits on the far side of the 100 nF DC block, so the harness loads
    the shared bus rather than joining the resonator, and this is the number
    that says how much.

    Bounded at 2 percent rather than 1: the worst line is modelled behind four
    harnesses and four whole-net bus lengths, which is pessimistic by
    construction, and it still lands at 0.99.
    """
    baseline = reference.lines[0].resonance_hz
    for result in corners:
        shift = abs(result.lowest_hz - baseline) / baseline
        assert shift < 0.02, f"{shift * 100:.2f} percent shift from the monolith"


def test_the_monolithic_reference_has_no_spread(reference: SplitBusResult) -> None:
    """Sanity on the control. One node means one resonance, sixteen times over,
    so any spread here would mean the testbench is measuring the testbench."""
    assert reference.spread_fraction == pytest.approx(0.0, abs=1e-9)


def test_the_connector_assumption_does_not_decide_anything(corners: tuple[SplitBusResult, ...]) -> None:
    """A11 is an assumption, so nothing may rest on its value.

    Two to eight nanohenries per mated pair is a fourfold range and it moves the
    band by less than one sweep step. That is what lets the split proceed with
    the assumption open instead of waiting on a number no connector vendor at
    this price publishes.
    """
    bands = [(result.lowest_hz, result.highest_hz) for result in corners]
    lowest = min(low for low, _ in bands)
    highest = max(high for _, high in bands)
    assert (highest - lowest) / lowest < 0.01


def test_each_board_pays_for_its_place_in_the_chain() -> None:
    """A board further down the chain sits behind more harness and more bus.

    Recorded because it is the asymmetry a reader of the schematic would not
    expect: the four boards are one design but not one bus path, and the last
    one is four harnesses away from the reader.
    """
    for board in range(1, LINE_COUNT // LANES_PER_BOARD):
        here = series_inductance_h(board * LANES_PER_BOARD, CONNECTOR_INDUCTANCE_MIN_H)
        before = series_inductance_h(
            (board - 1) * LANES_PER_BOARD, CONNECTOR_INDUCTANCE_MAX_H
        )
        assert here > before


def test_lanes_on_one_board_are_modelled_alike() -> None:
    """The bound is per board, so a board's four lanes cannot differ.

    That is the pessimism being bought: the real lanes tap the bus at different
    points, and taking all four at the whole net's length overstates three of
    them.
    """
    for board in range(LINE_COUNT // LANES_PER_BOARD):
        lanes = {
            series_inductance_h(board * LANES_PER_BOARD + lane, 4e-9)
            for lane in range(LANES_PER_BOARD)
        }
        assert len(lanes) == 1


def test_the_worst_line_is_the_far_end_of_the_second_spine() -> None:
    """Monotonic along each spine, so the extremes are where geometry says."""
    inductances = [series_inductance_h(line, 4e-9) for line in range(LINE_COUNT)]
    assert inductances == sorted(inductances)


def test_a_single_corner_matches_the_swept_corners(corners: tuple[SplitBusResult, ...]) -> None:
    """`run()` at the default is the middle corner, so the module's own entry
    point cannot drift from what the gate checks."""
    nominal = run()
    middle = corners[1]
    assert nominal.spread_fraction == pytest.approx(middle.spread_fraction, abs=1e-9)


def test_the_bus_bound_still_bounds_the_routed_copper() -> None:
    """`ROUTED_BUS_LENGTH_MM` has to keep bounding the board it came from.

    The project's rule is that a simulation reads the board rather than an
    estimate of it. Here the bus is autorouted, so the model takes the whole
    net's routed length as an upper bound on any path through it. That is only
    sound while the constant matches the copper, and a reroute moves the copper.
    """
    board = (
        Path(__file__).parent.parent / "pcb" / "generated" / "quad" / "quad.kicad_pcb"
    ).read_text(encoding="utf-8")
    # Serializers differ across pcbnew releases: net references in segments
    # are written as the name in some and as the numeric net id in others, and
    # field order inside the block is not stable. Resolve the id first, then
    # accept either spelling anywhere in the segment block.
    net_id_match = re.search(r"\(net (\d+) \"RF_BUS\"\)", board)
    assert net_id_match, "RF_BUS net is not declared on the board"
    net_ref = rf"\(net (?:{net_id_match.group(1)}|\"RF_BUS\")\)"
    segments = [
        (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
        for m in re.finditer(
            r"\(segment\s*\(start ([\d.-]+) ([\d.-]+)\)\s*\(end ([\d.-]+) ([\d.-]+)\)"
            r"\s*\(width ([\d.]+)\)(?:(?!\(segment).)*?" + net_ref,
            board,
            re.S,
        )
    ]
    assert segments, "no routed RF_BUS copper found"
    routed = sum(
        math.dist((float(x1), float(y1)), (float(x2), float(y2)))
        for x1, y1, x2, y2, _ in segments
    )
    assert routed <= ROUTED_BUS_LENGTH_MM + 0.5, (
        f"RF_BUS routes to {routed:.1f} mm, past the {ROUTED_BUS_LENGTH_MM} mm bound"
    )
    widths = {float(width) for *_, width in segments}
    assert widths == {ROUTED_BUS_WIDTH_MM}
