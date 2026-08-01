"""The firmware's pin map must not drift from the hub schematic."""

from hardware.pcb.firmware_pins import HEADER_PATH, render


def test_committed_header_matches_the_netlist() -> None:
    """Fails whenever the hub changes and `make firmware-pins` has not run.

    A stale pin map is not a compile error, it is a board that boots and does
    the wrong thing, so it has to be caught here instead.
    """
    committed = HEADER_PATH.read_text(encoding="utf-8")
    assert committed == render(), (
        "software/firmware/port/board_pins.h is stale; run `make firmware-pins`"
    )


def test_no_gpio_is_assigned_twice() -> None:
    gpios: dict[int, str] = {}
    for line in render().splitlines():
        if not line.startswith("#define PIN_"):
            continue
        macro, value = line.removeprefix("#define ").split()
        gpio = int(value)
        assert gpio not in gpios, f"{macro} and {gpios[gpio]} share GPIO {gpio}"
        gpios[gpio] = macro


def test_no_expander_bit_is_assigned_twice() -> None:
    seen: dict[tuple[int, int], str] = {}
    ports: dict[str, int] = {}
    bits: dict[str, int] = {}
    for line in render().splitlines():
        if not line.startswith("#define EXP_"):
            continue
        macro, value = line.removeprefix("#define ").split()
        if macro.endswith("_PORT"):
            ports[macro.removesuffix("_PORT")] = int(value)
        elif macro.endswith("_BIT"):
            bits[macro.removesuffix("_BIT")] = int(value)
    for signal, port in ports.items():
        location = (port, bits[signal])
        assert location not in seen, f"{signal} and {seen[location]} share P{port}.{bits[signal]}"
        seen[location] = signal


def test_boot_straps_carry_only_the_pullup_bus() -> None:
    """IO8 and IO9 must stay on I2C.

    The hub relies on the 4.7 k bus pullups to hold the C6's strapping pins
    high for SPI boot. Anything else driving them low at reset makes the board
    unbootable, which is a respin, not a bug fix.
    """
    header = render()
    assert "#define PIN_I2C_SCL        8" in header
    assert "#define PIN_I2C_SDA        9" in header
