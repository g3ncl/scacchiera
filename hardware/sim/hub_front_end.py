"""ngspice testbench for the hub's reader front end driving the loaded matrix bus.

Builds the 16-cell matrix bus subckt from the same SKiDL objects as the
netlist, attaches the hub's TX path exactly as the hub schematic wires it
(EMC low-pass, series match, one line selected), and asks whether the combined
system still resonates in band and how much field the selected loop carries.
The PN5180 TX driver is modeled as a stiff square-wave source's fundamental:
an AC source behind its few-ohm driver resistance.
"""

from dataclasses import dataclass
from pathlib import Path

from hardware.sim.cell_metrics import parse_wrdata
from hardware.sim.matrix_rf import (
    BIAS_RAIL_V,
    BUS_SUBCKT,
    _build_bus,
    _includes,
    _run_deck,
)
from hardware.sim.spice import emit_subckt


GENERATED_DIR = Path(__file__).parent / "generated" / "hub"
# PN5180 TX driver output resistance, few ohms per datasheet drive levels.
DRIVER_OHM = 2.0
# The hub schematic's TX path values (hub.py, _build_reader).
EMC_INDUCTOR_H = 470e-9
EMC_SHUNT_F = 220e-12
MATCH_SERIES_F = 68e-12


@dataclass(frozen=True)
class FrontEndResult:
    resonance_hz: float
    coil_a: float


def deck() -> str:
    bus_circuit, bus_ports = _build_bus()
    subckt_text = emit_subckt(bus_circuit, BUS_SUBCKT, bus_ports)
    sel_nodes = " ".join(f"sel{index}" for index in range(16))
    output = GENERATED_DIR / "front_end.dat"
    lines = [
        "Hub TX front end driving the loaded 16-line matrix bus",
        _includes(),
        subckt_text.rstrip("\n"),
        f"X1 rf vbias {sel_nodes} {BUS_SUBCKT}",
        f"VBIAS vbias 0 DC {BIAS_RAIL_V}",
        "VSEL0 sel0 0 DC 0",
        *(f"VSEL{index} sel{index} 0 DC {BIAS_RAIL_V}" for index in range(1, 16)),
        "VP tx1 0 DC 0 AC 1",
        f"RDRV tx1 emc_in {DRIVER_OHM}",
        f"L0 emc_in tx_filtered {EMC_INDUCTOR_H:.3e}",
        f"C0 tx_filtered 0 {EMC_SHUNT_F:.3e}",
        f"C1 tx_filtered rf {MATCH_SERIES_F:.3e}",
        ".ac dec 200 1meg 30meg",
        ".control",
        "run",
        "let source_mag = mag(i(VP))",
        "let coil_mag = mag(l.x1.ll2#branch)",
        f"wrdata {output} source_mag coil_mag",
        "quit",
        ".endc",
        ".end",
    ]
    return "\n".join(lines) + "\n"


def run() -> FrontEndResult:
    _run_deck(deck(), GENERATED_DIR / "front_end.cir")
    points = parse_wrdata(GENERATED_DIR / "front_end.dat")
    # Through a series-capacitor feed the driver current has no usable dip
    # (it is smallest at the low sweep edge by construction), so the metric is
    # where the selected loop's field peaks: that is the frequency the system
    # actually amplifies, and it must sit in band.
    peak = max(points, key=lambda point: point.coil_a)
    if peak in (points[0], points[-1]):
        raise RuntimeError("coil-current peak is at a sweep edge")
    return FrontEndResult(resonance_hz=peak.frequency_hz, coil_a=peak.coil_a)


if __name__ == "__main__":
    result = run()
    print(f"system resonance {result.resonance_hz / 1e6:.3f} MHz")
    print(f"selected coil current {result.coil_a * 1e3:.3f} mA per volt of drive")
