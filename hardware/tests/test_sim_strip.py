"""The electrical price of the split, measured rather than argued.

Two harnesses and two spines now sit between the reader and every tank. This
runs the same sixteen `matrix_cell` objects twice through one testbench, once
with that interconnect and once without, so the difference between the two
numbers is the interconnect and nothing else.

Slow by design. Sixteen lines times four interconnect cases is sixty-four
ngspice sweeps at 3000 points per decade, and the resolution is not optional:
at the matrix deck's own 200 points per decade a grid step is wider than the
entire spread being measured.
"""

import re
from pathlib import Path

import pytest
import yaml

from hardware.pcb.matrix_geometry import LINE_COUNT, ROW_COUNT
from hardware.pcb.strip_geometry import spine_bus_span_mm
from hardware.sim.interconnect import (
    CONNECTOR_INDUCTANCE_MAX_H,
    CONNECTOR_INDUCTANCE_MIN_H,
)
from hardware.sim.strip_rf import (
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
    """TEST-STRIP-RF-004."""
    low = _limit("STRIP-BUS-RESONANCE", "minimum")
    high = _limit("STRIP-BUS-RESONANCE", "maximum")
    for result in corners:
        for line in result.lines:
            megahertz = line.resonance_hz / 1e6
            assert low <= megahertz <= high, (
                f"line {line.line} at {megahertz:.3f} MHz with "
                f"{result.connector_inductance_h * 1e9:.0f} nH connectors"
            )


def test_the_sixteen_lines_stay_close_enough_to_trim(corners: tuple[SplitBusResult, ...]) -> None:
    """TEST-STRIP-RF-005.

    The one thing a single capacitor value cannot fix. The harness is common to
    all sixteen lines by construction, so it detunes them together and the
    nominal 220 pF absorbs it. The spine path is not common, and this is what it
    costs.
    """
    for result in corners:
        assert result.spread_fraction <= _limit(
            "STRIP-LINE-RESONANCE-SPREAD", "maximum"
        ), f"{result.spread_fraction:.4f} at {result.connector_inductance_h * 1e9:.0f} nH"


def test_the_interconnect_costs_less_than_one_percent_of_tuning(corners: tuple[SplitBusResult, ...], reference: SplitBusResult) -> None:
    """The controlled comparison: same cells, same sweep, interconnect removed.

    A tank behind a series inductor is not a tank with an inductor in it. The
    connector sits on the far side of the 100 nF DC block, so the harness loads
    the shared bus rather than joining the resonator, and this is the number
    that says how much.
    """
    baseline = reference.lines[0].resonance_hz
    for result in corners:
        shift = abs(result.lowest_hz - baseline) / baseline
        assert shift < 0.01, f"{shift * 100:.2f} percent shift from the monolith"


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
    assert (highest - lowest) / lowest < 0.005


def test_the_upper_bank_pays_for_the_daisy_chain() -> None:
    """Lines 8 to 15 reach the bus through the whole of the first spine.

    Recorded because it is the asymmetry a reader of the schematic would not
    expect: the two banks are identical boards but not identical bus paths, and
    if that ever stopped being true the topology has changed.
    """
    for line in range(ROW_COUNT, LINE_COUNT):
        assert series_inductance_h(line, CONNECTOR_INDUCTANCE_MIN_H) > series_inductance_h(
            line - ROW_COUNT, CONNECTOR_INDUCTANCE_MAX_H
        )


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


def test_the_bus_model_matches_the_routed_copper() -> None:
    """The simulated spine length is the drawn spine length.

    The project's rule is that a simulation reads the board rather than an
    estimate of it, and this is the one place the split could quietly break it.
    The bus is the only track the spine layout draws itself, and the tap sits
    2.5 mm off a connector's placement position with the link out rotated, so a
    centre-to-centre reading is 5 mm short. Parsing the routed board is what
    keeps `series_inductance_h` honest about which of the two it used.
    """
    board = (
        Path(__file__).parent.parent
        / "pcb" / "generated" / "spine" / "spine.kicad_pcb"
    ).read_text(encoding="utf-8")
    drawn = re.findall(
        r"\(segment\s*\(start ([\d.]+) [\d.]+\)\s*\(end ([\d.]+) [\d.]+\)"
        r"\s*\(width 3\)",
        board,
    )
    assert len(drawn) == 1, "the spine should draw exactly one 3 mm bus segment"
    start, end = (float(value) for value in drawn[0])
    assert abs(end - start) == pytest.approx(spine_bus_span_mm(), abs=0.01)
