---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/SL2S2602_NXP.pdf"
source_title: "SL2S2602 ICODE SLIX2 product data sheet, Rev. 4.2, 1 December 2021"
publisher: "NXP Semiconductors"
---

# SL2S2602 (ICODE SLIX2) datasheet

This source binds [SL2S2602](../entities/sl2s2602.md), the ISO/IEC 15693 tag IC proposed for the
piece transponders. It is not a fitted board component: it arrives inside the
[[ad-circus-slix2-datasheet|AD Circus SLIX2 inlay]] that sits in each piece's 22 mm recess. The
values below are what the matrix RF design and the V4 coupling model depend on.

[mpn::SL2S2602] [manufacturer::NXP Semiconductors] [standard::ISO/IEC 15693]
[nfc_forum_type::Type 5]

## Design facts reviewed

- Air interface: ISO/IEC 15693 and ISO/IEC 18000-3 Mode 1, 13.56 MHz carrier, up to 53 kbit/s,
  quoted operating distance up to 1.5 m at gate width (section 1, General description).
- Input capacitance between LA and LB: **23.5 pF typical, 22.3 pF minimum, 24.7 pF maximum**,
  measured on an HP4285A LCR meter at 13.56 MHz and 1.5 V RMS (Table 84, Interface
  characteristics). This is the tag-side capacitance the antenna coil must resonate against, and
  its 22.3 to 24.7 pF spread is the tolerance V4 must sweep.
- Minimum input power, operating: **40 uW**, including losses in the resonant capacitor and
  rectifier (Table 84, note 2).
- Minimum RMS input voltage, operating read/write: **1.1 V typical, 1.3 V maximum** (Table 84).
- Input frequency: 13.553 to 13.567 MHz, the ISM bandwidth limit of plus or minus 7 kHz
  (Table 84, note 1).
- User memory: 2528 bit, segmentable into two pages with separate read/write access conditions
  (section 1).
- UID: 8 byte, factory programmed, cannot be altered (section 1.3). This is what the row and
  column reports are joined on under [[row-column-antenna-matrix-technique]].
- `READ MULTIPLE BLOCKS` and `(FAST) INVENTORY READ` are present and compatible with ICODE SLI
  and ICODE SLIX (section 1.3). These are the commands [[bitwiseid-method]] needs.
- Persistent time: 2 s minimum, strongly ambient-temperature dependent (Table 84, note 4).
- Anti-collision: standard ISO/IEC 15693 slotted algorithm, several tags in the field
  simultaneously (section 1.2).
- Limiting values are specified for the bare wafer only (Table 82). The fitted part is a
  converted inlay, so the inlay datasheet governs handling and temperature.

## Simulation treatment

The chip enters V4 as a lumped shunt load across the tag coil terminals: 23.5 pF nominal input
capacitance swept 22.3 to 24.7 pF, with the 40 uW minimum input power as the extraction's pass
criterion at every cell position. No vendor SPICE or EM model is published for the die, so this
is a substitute model and must be recorded as such.

## Conflicts and gaps

- The datasheet gives no equivalent parallel resistance for the chip at minimum operating power,
  so the loaded Q of the tag resonator cannot be derived from this document alone. V4 either
  bounds it from the 40 uW figure or measures it at V8. Flag it as derived, not datasheet.
- The 1.5 m operating distance is a long-range gate figure and has no bearing on a 21 mm inlay
  over a 280 mm line antenna. Do not carry it into any criterion.

## Sources

- `Datasheets/SL2S2602_NXP.pdf`, retrieved 2026-08-01 from
  <https://www.nxp.com/docs/en/data-sheet/SL2S2602.pdf>

## Related

- [[ad-circus-slix2-datasheet]]
- [[pn5180a0hn-c3e-datasheet]]
- [[bitwiseid-method]]
- [[row-column-antenna-matrix-technique]]
