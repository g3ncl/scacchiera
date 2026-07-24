"""Schematic-level checks for the light bar board."""

from skidl import Circuit

from hardware.pcb.bom import fitted_cost_eur, missing_manufacturer_parts
from hardware.pcb.lightbar import build_lightbar
from hardware.pcb.lightbar_geometry import LED_COUNT


def _net_of(circuit: Circuit, reference: str, pin: str) -> str:
    part = next(part for part in circuit.parts if str(part.ref) == reference)
    return str(part[pin].net.name)


def test_lightbar_has_seventeen_pixels() -> None:
    circuit = build_lightbar()
    leds = [part for part in circuit.parts if str(part.ref).startswith("D")]
    assert len(leds) == LED_COUNT == 17


def test_lightbar_data_chain_is_ordered() -> None:
    circuit = build_lightbar()
    assert _net_of(circuit, "J1", "3") == _net_of(circuit, "D1", "3")
    for index in range(1, LED_COUNT):
        assert _net_of(circuit, f"D{index}", "1") == _net_of(circuit, f"D{index + 1}", "3")
    assert _net_of(circuit, f"D{LED_COUNT}", "1") == _net_of(circuit, "J1", "4")


def test_lightbar_bom_is_complete_and_cheap() -> None:
    circuit = build_lightbar()
    assert missing_manufacturer_parts(circuit) == ()
    # boards.md targets 5 EUR per bar including fab; parts must stay well under.
    assert fitted_cost_eur(circuit) <= 2.0
