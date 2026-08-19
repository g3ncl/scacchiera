---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-19
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

## Thermal data, read 2026-07-31

Section 6.4 Thermal Information gives theta-JA as 38.8 degrees Celsius per watt on the standard
board and 29.7 on the EVM. The design uses the higher standard-board figure. Absolute maximum
junction temperature is 150 degrees, with thermal shutdown at the same 150.

## Error-amplifier and loop facts recovered 2026-08-19, datasheet Rev. D

- GEA is published as 190 uA/V in the electrical characteristics with no MIN or MAX around it;
  the table states typicals hold at VIN = 3.6 V and TJ = 25 degrees Celsius, so the figure is a
  typical, not a guaranteed minimum. [locator::Electrical Characteristics] (The -Q1 variant's
  table formats the same figure so it reads as a MIN; that document does not govern this part.)
- The datasheet publishes the compensation transfer function and defines GEA, REA, VREF, VOUT,
  fCOMP1, fCOMP2 and fCOMZ, with design equations for R5, C5 and C8, and TI support material
  confirms the loop model shape (gm stage, compensation impedance, power stage, divider).
  [locator::Application and Implementation] A nominal loop model is therefore fully
  constructible from the document, which is what the existing 4,374-corner sensitivity sweep
  already exercises.
- TI states the application-section information is not part of the component specification and
  that validation is the customer's responsibility, and publishes no GEA or REA tolerance, no
  internal compensation tolerances, and no guaranteed phase margin, gain margin, overshoot or
  undershoot. The plus-or-minus 30 percent GEA sweep therefore spans an assumed range: nominal
  and sensitivity evidence, not worst-case release evidence.
