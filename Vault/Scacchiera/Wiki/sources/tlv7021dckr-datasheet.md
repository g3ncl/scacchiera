---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-20
source_file: "Datasheets/TLV7021DCKR_C702120.pdf"
source_title: "TLV7021DCKR manufacturer datasheet"
publisher: "Texas Instruments"
---

# TLV7021DCKR datasheet

This source binds [TLV7021DCKR](../entities/tlv7021dckr.md) to supplier order
code `C702120`. It is used by power U4 (TLV7021DCKR).

[mpn::TLV7021DCKR] [order_code::C702120]
[manufacturer::Texas Instruments] [footprint::Package_TO_SOT_SMD:SOT-353_SC-70-5]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: 1.6 to 5.5 V supply, open-drain output, high-impedance power-on reset, 8 mV maximum input offset, 14 mV maximum internal hysteresis, 20 us power-up time and DCK SC70-5 pinout.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  ngspice functional polarity model sweeps cold and already-powered insertion; comparator offset, hysteresis, power-on reset, MOSFET body diode and hot on-resistance are bounded from the filed component data sheets.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Land pattern, read 2026-08-20

The DCK (SC70-5) land pattern example, drawing 4214834/G: five pads of 0.95 x 0.4 mm on a 0.65 mm
pitch with a 2.2 mm outer span, solder mask notes 0.07 min/max, and note 7 stating IPC-7351
alternates are acceptable. [locator::Mechanical, page 37] Filed because KiCad 9.0.9's generic
SOT-353 uses 1.325 x 0.4 mm pads on a 3.1 mm span, 0.45 mm further out per side than this
recommendation; the power board's reviewed route was drawn against the bound footprint and clears
it, and this drawing is what makes the bound pattern the manufacturer-consistent one rather than
merely the older one.
