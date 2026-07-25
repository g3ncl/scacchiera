"""Generate schematics, netlists, and costed BOMs for the boards."""

import sys
from collections.abc import Callable
from pathlib import Path

from skidl import Circuit

from hardware.pcb.bom import missing_manufacturer_parts, write_bom
from hardware.pcb.erc import add_reviewed_no_connects, run_error_erc
from hardware.pcb.hub import build_hub
from hardware.pcb.lightbar import build_lightbar
from hardware.pcb.matrix import build_matrix


OUTPUT = Path(__file__).parent / "generated"
DESIGNS: dict[str, Callable[[], Circuit]] = {
    "lightbar": build_lightbar,
    "matrix": build_matrix,
    "hub": build_hub,
}
# Pins reviewed as legitimately unused, per design. Matrix U2:9 is the end of
# the selection daisy chain; the hub pins are the SKiDL no-connects (module
# spares, reader n.c. pins, unused expander ports) that KiCad still reports.
NO_CONNECTS: dict[str, frozenset[str]] = {
    "matrix": frozenset({"U2:9"}),
    "hub": frozenset(
        {
            "J1:6", "J1:14", "J8:4", "SW1:3",
            *(f"U3:{pin}" for pin in (2, 11, 14, 20, 23, 24, 31, 32, 33, 34, 35, 40)),
            *(f"U4:{pin}" for pin in (4, 7, 9, 10, 15, 17, 24, 25, 28, 29, 32, 33, 34, 35)),
            *(f"U6:{pin}" for pin in (1, 18, 19, 20)),
        }
    ),
}


def generate_design(name: str, circuit: Circuit) -> None:
    design_dir = OUTPUT / name
    design_dir.mkdir(parents=True, exist_ok=True)
    circuit.generate_netlist(file_=str(design_dir / f"{name}.net"), tool="kicad9", do_backup=False)
    circuit.generate_schematic(
        filepath=str(design_dir),
        top_name=name,
        title=f"Smart Chessboard {name.title()}",
        tool="kicad9",
        flatness=1.0,
        auto_stub=True,
        auto_stub_fanout=1,
        auto_stub_max_wire_pins=1,
        auto_stub_fallback="labels",
        retries=1,
    )
    reviewed = NO_CONNECTS.get(name)
    if reviewed:
        add_reviewed_no_connects(
            design_dir / f"{name}.kicad_sch", design_dir / f"{name}-erc.rpt", reviewed
        )
    run_error_erc(design_dir / f"{name}.kicad_sch", design_dir / f"{name}_errors.rpt")
    write_bom(circuit, design_dir / f"{name}_engineering_bom.csv")
    missing = missing_manufacturer_parts(circuit)
    if missing:
        raise RuntimeError(f"fitted parts without an MPN in {name}: {', '.join(missing)}")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in DESIGNS:
        raise SystemExit(f"Usage: python -m hardware.pcb.generate {{{'|'.join(DESIGNS)}}}")
    name = sys.argv[1]
    generate_design(name, DESIGNS[name]())


if __name__ == "__main__":
    main()
