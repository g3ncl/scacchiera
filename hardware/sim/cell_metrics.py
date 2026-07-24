"""Shared resonance and suppression analysis for antenna switch-cell testbenches.

Every switch-cell revision drives the cell differentially, sweeps it in an "on"
(selected) and "off" (deselected) state, and asks the same two questions: does
the selected antenna resonate in band, and how well is a deselected antenna
suppressed. This module is the one place that answers them, so
`pin_switch_cell.py` and any future revision cannot drift on what "resonance"
or "suppression" means.
"""

import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SweepPoint:
    frequency_hz: float
    source_a: float
    coil_a: float


@dataclass(frozen=True)
class SwitchCellResult:
    resonance_hz: float
    on_coil_a: float
    off_coil_a: float

    @property
    def suppression_db(self) -> float:
        return 20.0 * math.log10(self.on_coil_a / self.off_coil_a)


def parse_wrdata(path: Path) -> list[SweepPoint]:
    """Read wrdata's whitespace-separated columns.

    ngspice pairs every requested vector with its own x-axis column, so the two
    requested magnitudes arrive as four columns: frequency, source magnitude,
    frequency again, coil magnitude.
    """
    points: list[SweepPoint] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        tokens = line.split()
        if len(tokens) < 2:
            continue
        try:
            values = [float(token) for token in tokens]
        except ValueError:
            continue
        points.append(SweepPoint(values[0], values[1], values[-1]))
    return points


def resonance_dip(points: list[SweepPoint]) -> SweepPoint:
    """Locate the tuned frequency as the parallel-resonance dip in source current.

    At parallel resonance the tank impedance peaks, so the current the reader
    drives into the antenna is at a minimum. This is the same anti-resonance the
    ST25R200 sees through its antenna measurement, so it is the tuning target.
    An edge minimum means the resonance is outside the swept band, which is a
    setup or design error rather than a reading.
    """
    index = min(range(len(points)), key=lambda i: points[i].source_a)
    if index in (0, len(points) - 1):
        raise RuntimeError(
            "source-current dip is at a sweep edge; the resonance is outside the swept band"
        )
    return points[index]


def _nearest(points: list[SweepPoint], frequency_hz: float) -> SweepPoint:
    return min(points, key=lambda point: abs(point.frequency_hz - frequency_hz))


def analyze(on_points: list[SweepPoint], off_points: list[SweepPoint]) -> SwitchCellResult:
    # Suppression compares the field (coil current) at the tuned frequency between
    # the selected and deselected states, so a well shunted off cell reads as a
    # large ratio.
    resonance = resonance_dip(on_points)
    return SwitchCellResult(
        resonance_hz=resonance.frequency_hz,
        on_coil_a=resonance.coil_a,
        off_coil_a=_nearest(off_points, resonance.frequency_hz).coil_a,
    )


def evaluate(result: SwitchCellResult, criteria: dict[str, dict[str, float]]) -> list[tuple[str, bool, str]]:
    """Check the result against the spec-layer criteria, returning one row per limit."""
    resonance_mhz = result.resonance_hz / 1e6
    band = criteria["resonance_mhz"]
    resonance_ok = band["min"] <= resonance_mhz <= band["max"]
    suppression_min = criteria["off_on_suppression_db"]["min"]
    suppression_ok = result.suppression_db >= suppression_min
    return [
        (
            "resonance",
            resonance_ok,
            f"{resonance_mhz:.3f} MHz vs {band['min']}-{band['max']} MHz",
        ),
        (
            "off/on suppression",
            suppression_ok,
            f"{result.suppression_db:.2f} dB vs >= {suppression_min} dB",
        ),
    ]


def report_text(result: SwitchCellResult, criteria: dict[str, dict[str, float]]) -> str:
    rows = evaluate(result, criteria)
    verdicts = "\n".join(
        f"- {name}: {'PASS' if ok else 'FAIL'} ({detail})" for name, ok, detail in rows
    )
    return (
        "# Switch cell simulation report\n\n"
        f"- On-state resonance frequency: {result.resonance_hz / 1e6:.4f} MHz\n"
        f"- On-state coil current at resonance: {result.on_coil_a:.6e} A\n"
        f"- Off-state coil current at resonance: {result.off_coil_a:.6e} A\n"
        f"- Off/on coil-current suppression: {result.suppression_db:.2f} dB\n\n"
        "## Acceptance criteria\n\n"
        f"{verdicts}\n"
    )
