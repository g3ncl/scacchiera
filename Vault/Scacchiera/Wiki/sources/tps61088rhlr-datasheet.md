---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-29
source_file: "Datasheets/TPS61088RHLR_C87357.pdf"
source_title: "TPS61088RHLR manufacturer datasheet"
publisher: "Texas Instruments"
---

# TPS61088RHLR datasheet

This source binds [TPS61088RHLR](../entities/tps61088rhlr.md) to supplier order
code `C87357`. It is used by power U2 (TPS61088RHLR).

[mpn::TPS61088RHLR] [order_code::C87357]
[manufacturer::Texas Instruments] [footprint::Package_DFN_QFN:Texas_VQFN-RHL-20]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: 2.7 to 12 V input, 4.5 to 12.6 V output, programmable 200 kHz to 2.2 MHz switching, 11 A switch capability, 1.204 V feedback reference and RHL VQFN-20 pinout.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: vendor, valid only for
  official TI transient model is filed; its two-expression ngspice compatibility copy parses but does not switch, so V3 uses a datasheet-bounded switching stage and leaves control-loop evidence open.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.
