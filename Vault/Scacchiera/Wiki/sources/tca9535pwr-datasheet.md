---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-26
source_file: "Datasheets/TCA9535PWR_C130204.pdf"
source_title: "TCA9535PWR manufacturer datasheet"
publisher: "Texas Instruments"
---

# TCA9535PWR datasheet

This source binds [TCA9535PWR](../entities/tca9535pwr.md) to supplier order
code `C130204`. It is used by hub U6 (TCA9535PWR).

[mpn::TCA9535PWR] [order_code::C130204]
[manufacturer::Texas Instruments] [footprint::Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: See the filed data sheet and structured audit..
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  no distributable vendor ngspice model was identified; V3 may use only parameters enumerated in this part's filed datasheet and must sweep their full published limits; digital protocol behavior belongs to V6.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Power-on reset, read 2026-07-31

Electrical Characteristics gives VPORR, the rising power-on reset voltage, as 1.2 V typical and
1.5 V maximum, and VPORF, the falling one, as 0.75 V minimum and 1.0 V maximum. Section 7.4.1 says
the internal circuit holds the device in reset until VCC reaches VPORR, and that VCC must then be
lowered below VPORF and brought back up for another power-reset cycle. Section 7.3 adds that all
registers return to their default values at power-on reset, and the register tables give those
defaults: both Configuration registers all ones, so every P port comes up as a high-impedance input.

The part has no reset pin, unlike the TCA9539. Nothing but a supply excursion below VPORF resets it.

Table 5-1 puts the sixteen P ports on pins 4 through 11 and 13 through 20 of the PW package, each
described as a push-pull structure configured as an input at power on. Push-pull is why a passive
pull defines these nets only until firmware first drives them: after that the driver wins, and it
keeps winning through an MCU reset because the expander never sees one.

The hub's power-off discharge case uses the 0.75 V minimum rather than the 1.0 V maximum, because
the minimum is the level that guarantees the reset rather than merely permitting it.
