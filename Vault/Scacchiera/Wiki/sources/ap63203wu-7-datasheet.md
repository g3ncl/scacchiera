---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-19
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

## Loop and switch facts recovered 2026-08-19, current datasheet Rev. 3-2 (2024-11)

A targeted search of the current manufacturer document, beyond the originally filed extract,
recovered nominal internal-loop values the V3 gap statements previously called unpublished.

- Switch resistance: 125 mOhm high side, 68 mOhm low side, both typical with no MIN or MAX
  column, limits stated to apply from -40 to +85 degrees Celsius. [locator::Electrical
  Characteristics]
- A typical RDS(on)-versus-temperature curve exists. [locator::Figure 9, Typical Performance
  Characteristics] It supports a typical hot-dropout estimate; no maximum RDS(on), temperature
  coefficient, or temperature-cornered value is published anywhere in the document, so worst-case
  hot dropout still cannot be established from it.
- Internal compensation nominals are published on the functional block diagram: 7.6 nF, 18 kOhm,
  20 kOhm, slope compensation SE = 0.84 V per T, current-sense ratio RT = 0.2 V per A, with the
  error amplifier, COMP node, current-sense amplifier and PWM comparator identified.
  [locator::Functional Block Diagram] The application section confirms peak-current-mode control
  with internal loop compensation and shows a typical 1 A to 2 A load-transient plot.
  [locator::Application Information; Figure 17]
- Still absent: any tolerance or corner for those internal components, a small-signal
  control-to-output transfer function, loop-gain plots, guaranteed phase or gain margin, and any
  vendor SPICE or average model exposing the loop. A nominal loop model is now constructible; a
  cornered one is not.
- Filed-copy check: the extract above cites Rev. 3-2; if the filed PDF is an earlier revision,
  the conflict rule applies and the current PDF should be filed beside it.
