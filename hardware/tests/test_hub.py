"""Schematic-level checks for the hub board."""

from hardware.pcb.bom import fitted_cost_eur, missing_manufacturer_parts
from hardware.pcb.hub import build_hub


def test_hub_bom_is_complete_and_cheap() -> None:
    circuit = build_hub()
    assert missing_manufacturer_parts(circuit) == ()
    # boards.md targets 30 EUR including fabrication.
    assert fitted_cost_eur(circuit) <= 20.0


def test_hub_matrix_link_mirrors_the_matrix_connector() -> None:
    circuit = build_hub()
    connector = next(part for part in circuit.parts if str(part.ref) == "J4")
    expected = ("GND", "RF_BUS", "GND", "3V3", "MOSI", "SCLK", "SEL_RCLK")
    for pin, net_name in enumerate(expected, start=1):
        assert str(connector[str(pin)].net.name) == net_name


def test_hub_shares_one_spi_bus() -> None:
    circuit = build_hub()
    sclk = next(net for net in circuit.nets if net.name == "SCLK")
    # Reader, two displays, matrix link, and the MCU all clock from one bus.
    assert len(sclk.pins) == 5
