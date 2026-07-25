"""V2 connector, no-connect, startup, and programming checks."""

from pathlib import Path
from typing import Any

import yaml
from skidl import Circuit, Part

from hardware.pcb.erc import REVIEWED_WARNINGS
from hardware.pcb.generate import NO_CONNECTS as SCHEMATIC_NO_CONNECTS
from hardware.pcb.hub import NO_CONNECTS, build_hub
from hardware.pcb.lightbar import build_lightbar
from hardware.pcb.matrix import build_matrix


ROOT = Path(__file__).parents[2]
EVIDENCE = ROOT / "docs" / "verification" / "v2-static.yaml"


def _part(circuit: Circuit, reference: str) -> Part:
    return next(part for part in circuit.parts if str(part.ref) == reference)


def _net(circuit: Circuit, reference: str, pin: str) -> str:
    return str(_part(circuit, reference)[pin].net.name)


def _pin_map(circuit: Circuit, reference: str, count: int) -> tuple[str, ...]:
    return tuple(_net(circuit, reference, str(pin)) for pin in range(1, count + 1))


def _evidence() -> dict[str, Any]:
    document = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def test_reviewed_no_connects_are_exact_traced_and_applied() -> None:
    evidence = _evidence()
    assert set(evidence["reviewed_erc_warning_classes"]) == REVIEWED_WARNINGS
    records = evidence["no_connects"]
    assert isinstance(records, dict)
    documented = {
        reference: tuple(str(pin) for pin in record["pins"])
        for reference, record in records.items()
    }
    assert documented == NO_CONNECTS
    assert SCHEMATIC_NO_CONNECTS["hub"] == frozenset(
        f"{reference}:{pin}"
        for reference, pins in NO_CONNECTS.items()
        for pin in pins
    )

    circuit = build_hub()
    for reference, pins in NO_CONNECTS.items():
        for pin in pins:
            assert _net(circuit, reference, pin) == "__NOCONNECT"
        datasheet = ROOT / str(records[reference]["datasheet"])
        assert datasheet.is_file()
        assert datasheet.read_bytes().startswith(b"%PDF")
        assert str(records[reference]["locator"]).strip()

    matrix_records = evidence["matrix_no_connects"]
    matrix = build_matrix()
    assert SCHEMATIC_NO_CONNECTS["matrix"] == frozenset({"U2:9"})
    assert _part(matrix, "U2")["9"].net is None
    matrix_datasheet = ROOT / str(matrix_records["U2"]["datasheet"])
    assert matrix_datasheet.is_file()
    assert matrix_datasheet.read_bytes().startswith(b"%PDF")
    assert str(matrix_records["U2"]["locator"]).strip()


def test_board_to_board_connectors_match_at_both_ends() -> None:
    hub = build_hub()
    matrix = build_matrix()
    lightbar = build_lightbar()

    assert _pin_map(matrix, "J1", 7) == (
        "GND", "RF_BUS", "GND", "3V3", "SEL_SER", "SEL_SRCLK", "SEL_RCLK"
    )
    assert _pin_map(hub, "J4", 7) == (
        "GND", "RF_BUS", "GND", "3V3", "MOSI", "SCLK", "SEL_RCLK"
    )

    bar_link = ("LED_5V", "GND", "DATA_IN", "DATA_OUT")
    assert _pin_map(lightbar, "J1", 4) == bar_link
    assert _pin_map(hub, "J7", 4) == ("LED_5V", "GND", "LED_DATA_5V", "LED_RETURN")
    assert _pin_map(hub, "J8", 3) == ("LED_5V", "GND", "LED_RETURN")


def test_hub_connectors_and_usb_use_the_reviewed_pin_order() -> None:
    hub = build_hub()
    assert _pin_map(hub, "J5", 7) == (
        "3V3", "GND", "SCLK", "MOSI", "OLED1_CS_N", "OLED_DC", "OLED_RESET_N"
    )
    assert _pin_map(hub, "J6", 7) == (
        "3V3", "GND", "SCLK", "MOSI", "OLED2_CS_N", "OLED_DC", "OLED_RESET_N"
    )
    assert _pin_map(hub, "J9", 4) == ("3V3", "GND", "UART_TX", "UART_RX")
    assert _pin_map(hub, "J10", 2) == ("BUTTON_N", "GND")

    expected_usb = {
        "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
        "A4": "USB_VBUS_RAW", "A9": "USB_VBUS_RAW",
        "B4": "USB_VBUS_RAW", "B9": "USB_VBUS_RAW",
        "A5": "USB_CC1", "B5": "USB_CC2",
        "A6": "USB_D+", "B6": "USB_D+",
        "A7": "USB_D-", "B7": "USB_D-",
        "A8": "__NOCONNECT", "B8": "__NOCONNECT", "SH": "USB_SHIELD",
    }
    assert {pin: _net(hub, "J1", pin) for pin in expected_usb} == expected_usb


def test_startup_defaults_exposed_pads_and_recovery_are_defined() -> None:
    hub = build_hub()
    expected_resistors = {
        "R11": ({"POWER_EN", "GND"}, "1M"),
        "R19": ({"LED_DATA", "GND"}, "100k"),
        "R20": ({"MCU_EN", "3V3"}, "10k"),
        "R21": ({"I2C_SCL", "3V3"}, "4.7k"),
        "R22": ({"I2C_SDA", "3V3"}, "4.7k"),
        "R23": ({"OLED2_CS_N", "3V3"}, "10k"),
        "R24": ({"LED_EN", "GND"}, "100k"),
        "R25": ({"BUTTON_N", "3V3"}, "10k"),
        "R26": ({"SEL_RCLK", "GND"}, "100k"),
        "R31": ({"SEL_SRCLR_N", "3V3"}, "10k"),
    }
    for reference, (nets, value) in expected_resistors.items():
        part = _part(hub, reference)
        assert {_net(hub, reference, "1"), _net(hub, reference, "2")} == nets
        assert str(part.value) == value

    assert _net(hub, "U4", "8") == "MCU_EN"
    assert _net(hub, "U2", "11") == "GND"
    assert _net(hub, "U3", "41") == "GND"
    assert (_net(hub, "TP1", "1"), _net(hub, "TP2", "1"), _net(hub, "TP3", "1")) == (
        "I2C_SDA", "MCU_EN", "GND"
    )
