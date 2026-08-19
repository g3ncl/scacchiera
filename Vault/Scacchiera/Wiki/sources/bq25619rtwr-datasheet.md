---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-29
source_file: "Datasheets/BQ25619RTWR_C2864534.pdf"
source_title: "BQ25619RTWR manufacturer datasheet"
publisher: "Texas Instruments"
---

# BQ25619RTWR datasheet

This source bound [BQ25619RTWR](../entities/bq25619rtwr.md) to supplier order
code `C2864534` in the superseded 5 A battery-path design. Power U1 now uses
[[bq25895rtwr-datasheet|BQ25895RTWR]].

[mpn::BQ25619RTWR] [order_code::C2864534]
[manufacturer::Texas Instruments] [footprint::Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: 3.9 to 13.5 V input operating range, 1.5 A charge-current capability, NVDC power path, 5 A RMS BATFET discharge path, 1.5 MHz switching and RTW WQFN-24 pinout.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  no distributable vendor ngspice model was identified; V3 may use only parameters enumerated in this part's filed datasheet and must sweep their full published limits; digital protocol behavior belongs to V6.
- Conflicts: the part remains electrically valid, but its 5 A continuous path did not leave enough
  margin for the efficiency-bounded 10 W boost corner. It is no longer fitted.
