---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-31
source_file: "Datasheets/CSD25404Q3_C2865523.pdf"
source_title: "CSD25404Q3 manufacturer datasheet"
publisher: "Texas Instruments"
---

# CSD25404Q3 datasheet

This source binds [CSD25404Q3](../entities/csd25404q3.md) to supplier order
code `C2865523`. It is used by power Q1 (CSD25404Q3).

[mpn::CSD25404Q3] [order_code::C2865523]
[manufacturer::Texas Instruments] [footprint::Chessboard:CSD25404Q3_DQG]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: minus 20 V drain-to-source, plus or minus 12 V gate-to-source, 12.1 mOhm maximum on-resistance at minus 2.5 V gate drive, 1 V maximum body-diode drop at 10 A and DQG VSON-CLIP-8 pinout.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  ngspice functional polarity model sweeps cold and already-powered insertion; comparator offset, hysteresis, power-on reset, MOSFET body diode and hot on-resistance are bounded from the filed component data sheets.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Thermal data, read 2026-07-31

The Thermal Information table gives theta-JA as 55 degrees Celsius per watt on one square inch
of two-ounce copper, and the safe-operating-area plot labels 160 degrees per watt for minimum
pad copper. The design uses 160 because the power board reserves no such area. Operating
junction and storage temperature run from minus 55 to 150 degrees.
