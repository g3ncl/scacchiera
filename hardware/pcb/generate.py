"""Generate schematics, netlists, and costed BOMs for the boards."""

import sys
from collections.abc import Callable
from pathlib import Path

from skidl import Circuit

from hardware.pcb.bom import missing_manufacturer_parts, write_bom
from hardware.pcb.erc import add_reviewed_no_connects, run_reviewed_erc
from hardware.pcb.hub import NO_CONNECTS as HUB_NO_CONNECTS
from hardware.pcb.hub import build_hub
from hardware.pcb.lightbar import build_lightbar
from hardware.pcb.matrix import build_matrix
from hardware.pcb.power import NO_CONNECTS as POWER_NO_CONNECTS
from hardware.pcb.power import build_power
from hardware.pcb.schematic_placement import install_nonoverlap_placer


OUTPUT = Path(__file__).parent / "generated"
DESIGNS: dict[str, Callable[[], Circuit]] = {
    "lightbar": build_lightbar,
    "matrix": build_matrix,
    "hub": build_hub,
    "power": build_power,
}
SCHEMATIC_SEEDS = {"lightbar": 0, "matrix": 6, "hub": 3, "power": 9}
# Pins reviewed as legitimately unused, per design. Matrix U2:9 is the end of
# the selection daisy chain; the hub pins are the SKiDL no-connects (module
# spares, reader n.c. pins, unused expander ports) that KiCad still reports.
NO_CONNECTS: dict[str, frozenset[str]] = {
    "matrix": frozenset({"U2:9"}),
    "power": frozenset(
        f"{reference}:{pin}"
        for reference, pins in POWER_NO_CONNECTS.items()
        for pin in pins
    ),
    "hub": frozenset(
        f"{reference}:{pin}"
        for reference, pins in HUB_NO_CONNECTS.items()
        for pin in pins
    ),
}


def generate_design(name: str, circuit: Circuit) -> None:
    design_dir = OUTPUT / name
    design_dir.mkdir(parents=True, exist_ok=True)
    circuit.nets.sort(key=lambda net: str(net.name))
    circuit.parts.sort(key=lambda part: str(part.ref))
    install_nonoverlap_placer()
    circuit.generate_schematic(
        filepath=str(design_dir),
        top_name=name,
        title=f"Smart Chessboard {name.title()}",
        tool="kicad9",
        flatness=1.0,
        auto_stub=True,
        auto_stub_fanout=1,
        auto_stub_max_wire_pins=0,
        auto_stub_max_wire_dist=0,
        auto_stub_fallback="labels",
        seed=SCHEMATIC_SEEDS[name],
        retries=1,
    )
    _write_library_tables(circuit, design_dir)
    circuit.generate_netlist(file_=str(design_dir / f"{name}.net"), tool="kicad9", do_backup=False)
    reviewed = NO_CONNECTS.get(name)
    if reviewed:
        add_reviewed_no_connects(
            design_dir / f"{name}.kicad_sch", design_dir / f"{name}-erc.rpt", reviewed
        )
    run_reviewed_erc(design_dir / f"{name}.kicad_sch", design_dir / f"{name}_erc.rpt")
    write_bom(circuit, design_dir / f"{name}_engineering_bom.csv")
    missing = missing_manufacturer_parts(circuit)
    if missing:
        raise RuntimeError(f"fitted parts without an MPN in {name}: {', '.join(missing)}")


def _write_library_tables(circuit: Circuit, design_dir: Path) -> None:
    """Give standalone KiCad CLI runs the same libraries used by SKiDL."""
    symbol_libraries = sorted({str(part.lib.filename) for part in circuit.parts})
    footprint_libraries = sorted(
        {
            str(part.footprint).split(":", maxsplit=1)[0]
            for part in circuit.parts
            if getattr(part, "footprint", "")
        }
    )
    symbol_rows = "\n".join(
        f'  (lib (name "{library}")(type "KiCad")(uri "${{KICAD9_SYMBOL_DIR}}/{library}.kicad_sym")(options "")(descr ""))'
        for library in symbol_libraries
    )
    footprint_rows = "\n".join(
        f'  (lib (name "{library}")(type "KiCad")(uri "{_footprint_table_uri(library)}")(options "")(descr ""))'
        for library in footprint_libraries
    )
    (design_dir / "sym-lib-table").write_text(f"(sym_lib_table\n{symbol_rows}\n)\n", encoding="utf-8")
    (design_dir / "fp-lib-table").write_text(f"(fp_lib_table\n{footprint_rows}\n)\n", encoding="utf-8")


def _footprint_table_uri(library: str) -> str:
    if library == "Chessboard":
        return "${KIPRJMOD}/../footprints/Chessboard.pretty"
    return f"${{KICAD_FOOTPRINT_DIR}}/{library}.pretty"


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in DESIGNS:
        raise SystemExit(f"Usage: python -m hardware.pcb.generate {{{'|'.join(DESIGNS)}}}")
    name = sys.argv[1]
    generate_design(name, DESIGNS[name]())


if __name__ == "__main__":
    main()
