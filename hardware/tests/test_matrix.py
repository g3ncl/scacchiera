"""Schematic-level checks for the matrix board."""

from skidl import Circuit

from hardware.pcb.bom import fitted_cost_eur, missing_manufacturer_parts
from hardware.pcb.matrix import COIL_FOOTPRINT, build_matrix
from hardware.pcb.matrix_geometry import LINE_COUNT


def test_matrix_has_sixteen_line_antennas() -> None:
    circuit = build_matrix()
    antennas = [
        part for part in circuit.parts if str(getattr(part, "footprint", "")) == COIL_FOOTPRINT
    ]
    assert len(antennas) == LINE_COUNT == 16


def test_matrix_selection_is_one_line_per_register_output(sel_prefix: str = "SEL") -> None:
    circuit = build_matrix()
    sel_nets = {net.name for net in circuit.nets if net.name.startswith(sel_prefix) and net.name.endswith("_N")}
    assert sel_nets == {f"SEL{index}_N" for index in range(LINE_COUNT)}


def test_matrix_bom_is_complete_and_cheap() -> None:
    circuit = build_matrix()
    assert missing_manufacturer_parts(circuit) == ()
    # boards.md targets 25 EUR for the board including fabrication; the
    # area-dominated fab is most of that, parts must stay under 8.
    assert fitted_cost_eur(circuit) <= 8.0


def test_matrix_every_cell_reaches_the_shared_bus() -> None:
    circuit = build_matrix()
    rf_pins = next(net for net in circuit.nets if net.name == "RF_BUS").pins
    # One DC block per cell plus the connector pin.
    assert len(rf_pins) == LINE_COUNT + 1
