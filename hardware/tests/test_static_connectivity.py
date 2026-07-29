"""V2 connector, no-connect, startup, programming, and stackup checks."""

from functools import cache
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from skidl import Circuit, Part

from hardware.pcb.erc import REVIEWED_WARNINGS
from hardware.pcb.fab import copper_layers, gerber_layers
from hardware.pcb.generate import NO_CONNECTS as SCHEMATIC_NO_CONNECTS
from hardware.pcb.hub import NO_CONNECTS, build_hub
from hardware.pcb.lightbar import build_lightbar
from hardware.pcb.matrix import build_matrix


ROOT = Path(__file__).parents[2]
EVIDENCE = ROOT / "docs" / "verification" / "v2-static.yaml"
HUB_BOARD = ROOT / "hardware" / "pcb" / "generated" / "hub" / "hub.kicad_pcb"


def _hub_board() -> Path:
    # A bare pytest run regenerates the board; `make check` has already built
    # it through the schematic and layout targets.
    if not HUB_BOARD.exists():
        subprocess.run(
            (sys.executable, "-m", "hardware.pcb.generate", "hub"),
            check=True, cwd=ROOT, env=os.environ,
        )
        subprocess.run(
            ("/usr/bin/python3", "-m", "hardware.pcb.hub_layout", "--route"),
            check=True, cwd=ROOT, env=os.environ,
        )
    return HUB_BOARD


def _part(circuit: Circuit, reference: str) -> Part:
    return next(part for part in circuit.parts if str(part.ref) == reference)


def _net(circuit: Circuit, reference: str, pin: str) -> str:
    return str(_part(circuit, reference)[pin].net.name)


def _pin_map(circuit: Circuit, reference: str, count: int) -> tuple[str, ...]:
    return tuple(_net(circuit, reference, str(pin)) for pin in range(1, count + 1))


def _assert_filed_source(path: Path) -> None:
    assert path.is_file()
    if path.suffix == ".pdf":
        assert path.read_bytes().startswith(b"%PDF")
    else:
        assert path.suffix == ".md"
        assert path.read_text(encoding="utf-8").strip()


def _evidence() -> dict[str, Any]:
    document = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


@cache
def _power_connectivity() -> dict[str, dict[str, list[str]]]:
    result = subprocess.run(
        (sys.executable, "-m", "hardware.verification.power_connectivity"),
        check=True,
        cwd=ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )
    snapshot = json.loads(result.stdout)
    assert isinstance(snapshot, dict)
    return snapshot


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
        _assert_filed_source(datasheet)
        assert str(records[reference]["locator"]).strip()

    matrix_records = evidence["matrix_no_connects"]
    matrix = build_matrix()
    assert SCHEMATIC_NO_CONNECTS["matrix"] == frozenset({"U2:9"})
    assert _part(matrix, "U2")["9"].net is None
    matrix_datasheet = ROOT / str(matrix_records["U2"]["datasheet"])
    _assert_filed_source(matrix_datasheet)

    power_records = evidence["power_no_connects"]
    power_no_connects = {"U1": ("2", "3", "4", "7", "12"), "U2": ("13",), "J2": ("8",)}
    assert SCHEMATIC_NO_CONNECTS["power"] == frozenset(
        f"{reference}:{pin}"
        for reference, pins in power_no_connects.items()
        for pin in pins
    )
    snapshot = _power_connectivity()["no_connects"]
    for reference, pins in power_no_connects.items():
        assert snapshot[reference] == ["__NOCONNECT"] * len(pins)
        datasheet = ROOT / str(power_records[reference]["datasheet"])
        _assert_filed_source(datasheet)
        assert str(power_records[reference]["locator"]).strip()
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

    power_connectors = _power_connectivity()["connectors"]
    assert tuple(power_connectors["J1"]) == _pin_map(hub, "J2", 7)
    assert tuple(power_connectors["J2"]) == (
        "MODULE_5V", "MODULE_5V", "GND", "GND", "I2C_SCL", "I2C_SDA", "BAT_RAW", "__NOCONNECT"
    )
    assert _pin_map(hub, "J3", 8) == (
        "MODULE_5V", "MODULE_5V", "GND", "GND", "I2C_SCL", "I2C_SDA", "BAT_RAW", "__NOCONNECT"
    )
    assert tuple(power_connectors["J3"]) == ("BAT_RAW", "GND")


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
    assert _pin_map(hub, "J11", 2) == ("THERM_SENSE", "GND")
    # The GH charge-input contacts are paralleled. The return uses Micro-Fit
    # contacts sized for the complete 10 W load.
    assert _pin_map(hub, "J2", 7) == (
        "CHARGE_5V", "CHARGE_5V", "CHARGE_5V", "GND", "GND", "GND", "GND"
    )
    assert _pin_map(hub, "J3", 8) == (
        "MODULE_5V", "MODULE_5V", "GND", "GND", "I2C_SCL", "I2C_SDA", "BAT_RAW", "__NOCONNECT"
    )

    expected_usb = {
        "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
        "A4": "USB_VBUS", "A9": "USB_VBUS",
        "B4": "USB_VBUS", "B9": "USB_VBUS",
        "A5": "USB_CC1", "B5": "USB_CC2",
        "A6": "__NOCONNECT", "B6": "__NOCONNECT",
        "A7": "__NOCONNECT", "B7": "__NOCONNECT",
        "A8": "__NOCONNECT", "B8": "__NOCONNECT", "SH": "USB_SHIELD",
    }
    assert {pin: _net(hub, "J1", pin) for pin in expected_usb} == expected_usb


def test_startup_defaults_exposed_pads_and_recovery_are_defined() -> None:
    hub = build_hub()
    expected_resistors = {
        "R1": ({"USB_CC1", "GND"}, "5.1k"),
        "R2": ({"USB_CC2", "GND"}, "5.1k"),
        "R34": ({"USB_CC1", "USB_CC1_ADC"}, "10k"),
        "R35": ({"USB_CC2", "USB_CC2_ADC"}, "10k"),
        "R12": ({"CHARGE_TEMP_OK", "USB_VBUS"}, "100k"),
        "R15": ({"CHARGE_INPUT_FAULT_N", "3V3"}, "100k"),
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
    assert _net(hub, "U4", "12") == "USB_CC1_ADC"
    assert _net(hub, "U4", "13") == "USB_CC2_ADC"
    assert _net(hub, "U4", "16") == "NFC_IRQ"
    assert _net(hub, "U4", "19") == "LED_DATA"
    assert _net(hub, "U3", "41") == "GND"
    assert (_net(hub, "TP1", "1"), _net(hub, "TP2", "1"), _net(hub, "TP3", "1")) == (
        "I2C_SDA", "MCU_EN", "GND"
    )


def test_power_boundary_and_temperature_gate_are_hardware_defined() -> None:
    hub = build_hub()
    assert _pin_map(hub, "U1", 5) == (
        "CHARGE_5V", "GND", "CHARGE_INPUT_FAULT_N", "CHARGE_TEMP_OK", "USB_VBUS"
    )
    assert _pin_map(hub, "U2", 8) == (
        "CHARGE_TEMP_OK", "THERM_SENSE", "THERM_COLD_REF", "GND",
        "THERM_SENSE", "THERM_HOT_REF", "CHARGE_TEMP_OK", "USB_VBUS",
    )
    assert _pin_map(hub, "U5", 6) == (
        "3V3", "MODULE_5V", "MODULE_5V", "GND", "BUCK_SW", "BUCK_BST"
    )
    assert _pin_map(hub, "L1", 2) == ("BUCK_SW", "3V3")
    assert _net(hub, "U4", "5") == "TEMP_SENSE_ADC"
    assert _net(hub, "U4", "17") == "__NOCONNECT"
    assert _net(hub, "U4", "18") == "__NOCONNECT"


def test_battery_level_is_measured_on_board_not_read_from_the_module() -> None:
    """The product reports battery level, and no purchased module has to be
    trusted for it: the cell arrives on J3 and is divided into the MCU's ADC."""
    hub = build_hub()
    for reference, nets in (
        ("R32", {"BAT_RAW", "BAT_SENSE_ADC"}),
        ("R33", {"BAT_SENSE_ADC", "GND"}),
        ("C18", {"BAT_SENSE_ADC", "GND"}),
    ):
        assert {_net(hub, reference, "1"), _net(hub, reference, "2")} == nets
    # Equal halves keep a 4.2 V cell at 2.1 V, under the 2.5 V the sensor tap
    # already presents to the same ADC when its thermistor opens.
    assert str(_part(hub, "R32").value) == str(_part(hub, "R33").value) == "1M"
    assert _net(hub, "U4", "9") == "BAT_SENSE_ADC"


def test_hub_board_matches_its_recorded_stackup() -> None:
    """Every board is two layers, and the Gerber export has to carry them all.

    The layer count is a cost decision as much as an electrical one, so it is
    asserted against the board rather than described only in prose."""
    recorded = _evidence()["hub_layout"]
    assert (ROOT / str(recorded["reviewed_route"])).is_file()
    board = _hub_board()
    layers = copper_layers(board)
    assert layers == ("F.Cu", "B.Cu")
    assert len(layers) == recorded["copper_layers"]
    assert set(layers).issubset(gerber_layers(board).split(","))
    thickness = re.search(r"\(thickness ([\d.]+)\)", board.read_text(encoding="utf-8"))
    assert thickness is not None
    assert float(thickness.group(1)) == recorded["board_thickness_mm"]
    # The envelope is what buys two layers, so it is read off the board outline
    # rather than trusted to the record it is checked against.
    corners = re.findall(r"\(gr_line\s+\(start ([-\d.]+) ([-\d.]+)\)", board.read_text(encoding="utf-8"))
    assert corners
    extent = [max(float(x) for x, _ in corners), max(float(y) for _, y in corners)]
    assert extent == [float(value) for value in recorded["envelope_mm"]]
