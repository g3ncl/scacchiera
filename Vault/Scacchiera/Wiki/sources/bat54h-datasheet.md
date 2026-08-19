---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-29
source_file: "Datasheets/BAT54H_C475620.pdf"
source_title: "BAT54H manufacturer datasheet"
publisher: "Jiangsu Changjing Electronics Technology"
---

# BAT54H datasheet

This source binds [BAT54H](../entities/bat54h.md) to supplier order
code `C475620`. It is used by power D1 (BAT54H).

[mpn::BAT54H] [order_code::C475620]
[manufacturer::Jiangsu Changjing Electronics Technology] [footprint::Diode_SMD:D_SOD-323]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: 30 V repetitive reverse voltage, 300 mA average forward current, 0.37 V maximum forward drop at 20 mA, 5 uA maximum reverse leakage and SOD-323 pin 1 cathode pinout.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  ngspice functional polarity model sweeps cold and already-powered insertion; comparator offset, hysteresis, power-on reset, MOSFET body diode and hot on-resistance are bounded from the filed component data sheets.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.
