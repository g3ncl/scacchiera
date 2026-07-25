---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: 2026-07-25
source_count: 2
---

# ESP32-C6-MINI-1U

The WiFi and BLE module carrying the [hub board](../../../../docs/hardware/hub.md)'s
game logic, at designator **U4**. Espressif's own module, so the chip, 4 MB
flash, 40 MHz crystal, shield and RF matching are already assembled on it: the
board only has to supply 3V3, ground, EN and GPIO.

[mpn::ESP32-C6-MINI-1U-N4] [lcsc::C7558096] [board::hub] [designator::U4]
[jlc_library::Extended] [package_mm::13.2x12.5x2.4] [unit_cost_eur::2.60]

Datasheet facts: [[esp32-c6-mini-1u-datasheet]].

## Why this part

It replaced an ESP32-C3-MINI-1U-N4X that JLCPCB could not stock in quantity,
which was blocking the whole hub assembly order. Choosing the C6 rather than
simply the stocked C3-MINI-1 bought newer silicon (2023 rather than 2021),
512 KB of SRAM against 400 KB, WiFi 6 and BLE 5.3, for the same footprint and
about 0.40 EUR more.

The `1U` suffix matters as much as the C6 does. It has an external antenna
connector instead of a PCB antenna, which keeps the module at 12.5 mm rather
than 16.6 mm, needs no copper keepout, and makes the antenna a plug-in
accessory. A bad antenna then costs an antenna, not a hub board, which is why
this variant was chosen over the PCB-antenna ESP32-C6-MINI-1 (C5736265).

## The pin-compatibility trap

Vendor listings call the C6-MINI-1 "pin-to-pin compatible with the ESP32-C3-MINI
series". Against Table 3-1 that is true only for power, ground, EN and UART0.
Most GPIO numbers differ, **native USB moves from the C3's pins 26/27 to pins
17/18**, and pin 21 becomes NC. Reusing the C3 pin map would have put SCLK on
USB_D+ and the reader's chip select on a no-connect. This was caught by reading
the datasheet, and is the case that motivated the
[datasheet rule](../../../../CLAUDE.md) in the first place.

## How the hub uses it

- SPI on the FSPI-native pins: SCLK on IO6 (pin 15), MOSI on IO7 (pin 16),
  MISO on IO2 (pin 5), so the bus avoids the GPIO matrix.
- I2C stays on pins 22 and 23 (IO8, IO9) because those are the C6 boot
  strapping pins and the 4.7k bus pullups hold them high for SPI boot. That
  also makes IO9 the download-mode recovery pin at no extra cost.
- IO15 (pin 20) is deliberately unused: it is the JTAG-source strapping pin.
- Native USB to the board's USB-C, so flashing needs no programmer.
- Local decoupling of 10 uF plus 100 nF at pin 3, because WiFi TX peaks at
  **382 mA** and the regulator's own output capacitors are centimetres away.
- TP1 (IO9), TP2 (EN) and TP3 (GND) recovery pads, since the only button sits
  behind a polled expander and cannot hold IO9 low at reset.

## Open items

- Stock was never confirmed. C7558096 is a JLCPCB "New Arrivals" line that
  publishes no quantity, and LCSC returns 404 for the code. Verify before
  ordering; fallback is C5736265 (C6-MINI-1, PCB antenna, 517 in stock),
  accepting the keepout and a fixed antenna.
- The external antenna and its pigtail are purchased accessories on no BOM. The
  connector is **MHF3 / W.FL / IPEX3**, not U.FL: a U.FL pigtail will not mate.
- Firmware targets `esp32c6`, and the strapping-pin map differs from the C3, so
  the pin map wants one review pass against the datasheet before first flash.

Related: [[pn5180]], [[jlcpcb]], [[txc-7m27100009]]
