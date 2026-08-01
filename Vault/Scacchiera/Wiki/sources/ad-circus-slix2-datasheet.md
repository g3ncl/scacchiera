---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/AD-CIRCUS-SLIX2_AVERYDENNISON.pdf"
source_title: "AD Circus SLIX SLIX 2 product data sheet, AD-Circus-ICODE-SLIX - SLIX2 -11-23-EN-DS"
publisher: "Avery Dennison Smartrac"
---

# AD Circus SLIX2 inlay datasheet

This source binds [AD Circus SLIX2](../entities/ad-circus-slix2.md), the converted 21 mm round
inlay proposed as the piece transponder. It carries the
[[sl2s2602-datasheet|NXP SL2S2602 ICODE SLIX2]] die. It is the physical article that sits in the
22 mm piece recess defined in `docs/functional/physical.md`.

[mpn::AD Circus SLIX 2 wet inlay+] [product_code::3006370] [alt_code::IL-603074]
[manufacturer::Avery Dennison Smartrac] [chip::SL2S2602] [standard::ISO 15693]

## Design facts reviewed

- **Antenna diameter: 18 mm.** This, not the 21 mm die-cut, is the coupling geometry V4 must
  model (Overview, Antenna Dimensions).
- **Die-cut diameter: 21 mm**, leaving 0.5 mm radial clearance in the 22 mm nominal recess
  (Technical features, Die-Cut Dimension).
- **Total thickness: 141 um** for both wet-inlay variants; 172 um for the white-PET label variant
  (Technical features, Total Thickness).
- Inlay substrate PET, face sheet clear PET on the wet inlay+ variant.
- Operating temperature: -40 to +85 degrees Celsius (Technical features).
- Delivery: 5000 pcs per reel, 10000 per box, 27 mm pitch on a 26 mm web, 76 mm core. Reel
  quantity vastly exceeds the 32 pieces a set needs, so buy cut singles from a reseller rather
  than a reel.
- Standards: ISO 15693, RoHS 2011/65/EU and 2015/863, REACH 1907/2006.

## Variant selection

Three SLIX2 rows share the Ø 21 mm die-cut and 18 mm antenna:

| Variant | Product code | Face sheet | Thickness |
| --- | --- | --- | --- |
| Wet inlay + | 3003285 / IL-602803 | Clear PET | 141 um |
| Label | 3003286 / IL-610376 | White PET 50 | 172 um |
| Wet inlay + | 3006370 / IL-603074 | Clear PET | 141 um |

The two wet-inlay+ codes are listed with identical published specifications in this revision;
which one a given reseller ships is a purchasing question, not an electrical one. Any of the
three is electrically the same tag. The 31 um thickness difference is the only design-visible
distinction and is absorbed by the recess depth.

## Simulation treatment

The 18 mm antenna diameter is the datasheet input to V4's tag geometry. Turn count, track width,
and coil inductance are **not published**, so the tag coil must be back-solved from the
resonance condition against the SL2S2602's 23.5 pF input capacitance, or measured at V8. That
back-solve is a derived value, not a datasheet one.

## Conflicts and gaps

- No coil inductance, turn count, resonant frequency, or Q figure is published. This is the
  single largest gap between the bound tag and a complete V4 model, and it is inherent to
  converted inlays: Avery Dennison does not publish coil geometry.
- The reseller (Shop NFC, SKU 724) states 316 bytes available memory against the datasheet's
  2500 bit (312.5 bytes) and NXP's 2528 bit. These are the same part described with different
  overhead accounting, not a contradiction of substance, but quote the NXP figure.
- Avery Dennison's own terms disclaim fitness and reserve the right to discontinue without
  notice. A second-source tag should be identified before the design depends on this exact inlay.

## Sources

- `Datasheets/AD-CIRCUS-SLIX2_AVERYDENNISON.pdf`, retrieved 2026-08-01 from
  <https://rfid.averydennison.com/content/dam/rfid/en/products/rfid-products/data-sheets/datasheet-Circus-ICODE-SLIX.pdf>
- Reseller listing, Shop NFC SKU 724, retrieved 2026-08-01:
  <https://shopnfc.com/en/nfc-stickers/724-nfc-stickers-slix2-round-21mm.html>

## Related

- [[sl2s2602-datasheet]]
- [[row-column-antenna-matrix-technique]]
