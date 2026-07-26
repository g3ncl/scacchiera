---
type: source-summary
date_updated: 2026-07-26
tags:
  - wiki/source
  - wiki/power
  - wiki/battery
---

# PiSugar 3 Plus manufacturer documentation

Manufacturer documentation for the [[pisugar3-plus]] battery UPS. The immutable sources are
[[../../Datasheets/PISUGAR3_PLUS_product.md|product documentation]],
[[../../Datasheets/PISUGAR3_PLUS_i2c.md|I2C documentation]],
[[../../Datasheets/PISUGAR3_PLUS_safety.md|safety instructions]], and the
[[../../Datasheets/PISUGAR3_PLUS.step|vendor STEP model]].

## Electrical and mechanical values

| Parameter | Published value | Locator |
| --- | ---: | --- |
| Input | 5 V, 3 A maximum | Product documentation, Electrical Specifications |
| Output | 5 V, 3 A maximum | Product documentation, Electrical Specifications |
| Battery | Included 1S 5,000 mAh Li-ion polymer pack | Product documentation and shop package list |
| PCB size | 65 x 56 mm nominal | Product documentation, Electrical Specifications |
| Vendor-model envelope | 65 x 57 x 9.22 mm | STEP bounding box |
| Main I2C address | 0x57, configurable | I2C documentation |
| RTC I2C address | 0x68 | Product documentation |
| Battery output | 3.0 to 4.2 V | Product documentation, PCB instructions |

[input_v::5] [input_max_a::3] [output_v::5] [output_max_a::3]
[capacity_mah::5000] [pcb_width_mm::56] [pcb_length_mm::65]

The manufacturer calls the product a full UPS and states that the output keeps working when
external power is connected or disconnected. Charging and output at the same time are supported.
The extension header exposes 5 V, ground, and the I2C slave bus, so the chessboard does not need to
use the Raspberry Pi pogo contacts.

I2C exposes external-power presence, charge enable, output enable, delayed output shutdown, battery
voltage, calculated battery percentage, and charger-chip temperature. The temperature register is
explicitly not battery temperature. Charging briefly pauses every three seconds to obtain a less
biased battery-voltage reading.

At a 2 A charge setting the published charger-chip temperature is about 50 to 60 degrees Celsius;
at 3 A it may peak near 80 degrees Celsius. The safety instructions require 5 V input, ventilation,
0 to 40 degree Celsius battery operation, inspection for swelling or damage, and use of the official
replacement battery. They prohibit relying on an unqualified fast-charge adapter and warn against
heat accumulation in an enclosed case. These constraints require a ventilated service cassette and
measured V8 thermal evidence.

The documentation does not identify a battery thermistor or a hardware cell-temperature cutoff.
Chip temperature cannot substitute for cell temperature. The final integration therefore retains a
separate cell-temperature gate as an open safety obligation.
