---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/TPS2553DBVR-1_C111738.pdf"
source_title: "TPS2553DBVR-1 manufacturer datasheet"
publisher: "Texas Instruments"
---

# TPS2553DBVR-1 datasheet

This source binds [TPS2553DBVR-1](../entities/tps2553dbvr-1.md) to supplier order
code `C111738`. It is used by hub U7 (TPS2553DBVR-1).

[mpn::TPS2553DBVR-1] [order_code::C111738]
[manufacturer::Texas Instruments] [footprint::Package_TO_SOT_SMD:SOT-23-6]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: See the filed data sheet and structured audit..
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: vendor, valid only for
  TI unencrypted transient PSpice model; V3 must prove ngspice compatibility and sweep datasheet input, load, temperature and external-component limits.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Thermal data, read 2026-07-31

Section 7.4 Thermal Information gives theta-JA as 182.6 degrees Celsius per watt for the DBV
SOT-23 package. The Electrical Characteristics power-switch rows give rDS(on) as 135 mOhm
maximum over minus 40 to 125 degrees in DBV, and the junction maximum is 150 degrees.

## Temperature and sequencing data, read 2026-08-01

Absolute Maximum Ratings cover IN, OUT, EN, ILIM and FAULT in one row at -0.3 to 7 V, with note 2
stating that voltages are referenced to GND. Enable and fault may therefore sit at 3.3 V while the
part's own input is unpowered.

The FAULT deglitch is 5 ms minimum and 10 ms maximum for an overcurrent condition, and the -1
suffix latches off when it expires. Response time to a short circuit is 2 us, typical only.
