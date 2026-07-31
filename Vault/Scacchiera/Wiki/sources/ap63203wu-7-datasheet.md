---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-31
source_file: "Datasheets/AP63203WU-7_C780769.pdf"
source_title: "AP63203WU-7 manufacturer datasheet"
publisher: "Diodes Incorporated"
---

# AP63203WU-7 datasheet

This source binds [AP63203WU-7](../entities/ap63203wu-7.md) to supplier order
code `C780769`. It is used by hub U5 (AP63203WU-7).

[mpn::AP63203WU-7] [order_code::C780769]
[manufacturer::Diodes Incorporated] [footprint::Package_TO_SOT_SMD:SOT-23-6]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: 3.8 to 32 V input, fixed 3.3 V output, 2 A continuous current, 1.1 MHz switching, 4.7 uH selected inside the 2.2 to 10 uH range, 10 uF input, two 22 uF output and 100 nF bootstrap.
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  no distributable vendor ngspice model was identified; V3 may use only parameters enumerated in this part's filed datasheet and must sweep their full published limits; digital protocol behavior belongs to V6.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Thermal data, read 2026-07-31

Thermal Resistance (Note 6) gives theta-JA as 89 degrees Celsius per watt for the TSOT26
package, and the Absolute Maximum table puts the junction limit at 160 degrees with thermal
shutdown at 150. The design uses 150.
