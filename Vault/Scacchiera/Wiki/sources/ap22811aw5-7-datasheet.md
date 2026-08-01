---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/AP22811AW5-7_C3001660.pdf"
source_title: "AP22811AW5-7 manufacturer datasheet"
publisher: "Diodes Incorporated"
---

# AP22811AW5-7 datasheet

This source binds [AP22811AW5-7](../entities/ap22811aw5-7.md) to supplier order
code `C3001660`. It is used by hub U1 (AP22811AW5-7).

[mpn::AP22811AW5-7] [order_code::C3001660]
[manufacturer::Diodes Incorporated] [footprint::Package_TO_SOT_SMD:SOT-23-5]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: 2.7 to 5.5 V input, 2 A continuous current, 65 mOhm maximum on-resistance at 5 V and 25 degrees Celsius, 2.2 to 3.2 A overload limit, active-high enable, open-drain fault, reverse blocking, output discharge, UVLO and thermal shutdown.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  no distributable vendor ngspice model was identified; V3 may use only parameters enumerated in this part's filed datasheet and must sweep their full published limits; digital protocol behavior belongs to V6.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Temperature and sequencing data, read 2026-08-01

Absolute Maximum Ratings list VIN at -0.3 to 6.0 V, and VOUT and VEN at -0.3 V to VIN + 0.3 V.
**There is no row for the fault flag.** The enable that is listed is supply referenced rather than
ground referenced, so nothing in the document permits holding any pin above an unpowered VIN.

The hub does exactly that: R15 pulls the flag to 3.3 V and the board runs from the battery with
USB absent. The condition is unspecified rather than violating a stated limit. R15 bounds the pin
at 33 uA, which is smaller than leakages this sheet specifies elsewhere, but the gap is real and
belongs to the vendor or to a V8 measurement.
