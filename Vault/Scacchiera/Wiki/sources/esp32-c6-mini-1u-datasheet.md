---
type: source-summary
tags:
  - wiki/source
date_updated: 2026-07-25
source_file: "Datasheets/ESP32-C6-MINI-1U-N4_C7558096.pdf"
source_title: "ESP32-C6-MINI-1 & ESP32-C6-MINI-1U Datasheet v1.5"
publisher: Espressif Systems
---

# ESP32-C6-MINI-1U datasheet v1.5

Facts extracted from Espressif's module datasheet, filed because [[esp32-c6-mini-1u]]
replaced the ESP32-C3-MINI-1U on the [hub board](../../../../docs/hardware/hub.md).
Interpretation of the swap lives in the entity page, not here.

[mpn::ESP32-C6-MINI-1U-N4] [lcsc::C7558096] [datasheet_version::v1.5]

## Variants and dimensions (section 1, section 10.1)

| Variant | Antenna | Dimensions |
| --- | --- | --- |
| ESP32-C6-MINI-1 | PCB antenna | 13.2 x 16.6 x 2.4 mm |
| ESP32-C6-MINI-1U | external connector | 13.2 x 12.5 x 2.4 mm |

The 1U has no antenna keepout zone. Module body width is 13.20 ± 0.2 mm.

## Pin definitions (Table 3-1)

53 pins. The pin diagram applies to both variants.

- `GND`: 1, 2, 11, 14, 36 to 53
- `3V3`: 3
- `NC`: 4, 7, 21, 32, 33, 34, 35
- `EN`: 8, with the note "Do not leave the EN pin floating"
- GPIOs by pin: 5 = IO2, 6 = IO3, 9 = IO4, 10 = IO5, 12 = IO0, 13 = IO1,
  15 = IO6, 16 = IO7, 17 = IO12, 18 = IO13, 19 = IO14, 20 = IO15, 22 = IO8,
  23 = IO9, 24 = IO18, 25 = IO19, 26 = IO20, 27 = IO21, 28 = IO22, 29 = IO23,
  30 = RXD0 (GPIO17), 31 = TXD0 (GPIO16)

**Native USB is IO12 and IO13, on pins 17 and 18.** [usb_pins::17,18]

Alternate functions relevant to this design: IO12 = `USB_D-`, IO13 = `USB_D+`,
IO6 = `FSPICLK`, IO7 = `FSPID`, IO2 = `FSPIQ`, IO4 = `FSPIHD`, IO5 = `FSPIWP`.

## Boot configuration (section 4)

- Chip boot mode strapping pins: GPIO8 and GPIO9 (Table 4-3). SPI boot needs
  GPIO9 = 1 with GPIO8 any value; joint download boot needs GPIO8 = 1, GPIO9 = 0.
- Joint download boot supports USB-Serial-JTAG, UART and SDIO download.
- Default strapping levels (Table 4-1): GPIO9 has a weak pull-up (bit 1);
  MTMS, MTDI, GPIO8 and GPIO15 float.
- Other strapping pins: MTMS and MTDI (SDIO clock edge), GPIO8 (ROM message
  printing), GPIO15 (JTAG signal source).
- Strapping hold time after CHIP_PU goes high: 3 ms minimum (Table 4-2).

## Current consumption (Table 6-4, Table 6-5, Table 6-8)

| Condition | Peak |
| --- | --- |
| TX 802.11b, 1 Mbps DSSS @ 20.5 dBm | **382 mA** |
| TX 802.11g, 54 Mbps OFDM @ 19.0 dBm | 316 mA |
| TX 802.11n HT20 MCS7 @ 18.0 dBm | 295 mA |
| TX 802.11ax MCS9 @ 15.5 dBm | 251 mA |
| RX 802.11b/g/n HT20 | 78 mA |
| Bluetooth LE TX @ 19.0 dBm | 309 mA |

Modem-sleep at 160 MHz: 27 mA running, 17 mA idle (clocks disabled).
Light-sleep 180 uA, deep-sleep 7 uA, power off 1 uA.

[peak_tx_current_ma::382]

## RF (section 7)

WiFi 2412 to 2484 MHz, IEEE 802.11b/g/n/ax. External antennas used for
Espressif's tests present **50 ohm** impedance, and the quoted RF data is
measured at the antenna port including front-end loss.

## Flash (Table 6-9)

4 MB on the N4 variant. 100,000 program/erase cycles, 20 year retention,
80 MHz maximum clock.

## Contradiction with vendor marketing

Third-party listings describe the C6-MINI-1 as "pin-to-pin compatible with the
ESP32-C3-MINI series". Against Table 3-1 that holds only for power, ground, EN
and UART0. The GPIO numbers behind most pins differ, and native USB moves from
the C3's pins 26/27 to pins 17/18 while pin 21 becomes NC. Recorded as a
contradiction rather than silently accepted: see [[esp32-c6-mini-1u]].

Related: [[jlcpcb]], [[pn5180]]
