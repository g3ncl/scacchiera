---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
source_file: "Datasheets/W256064-XALG_ELECTRONIC-ASSEMBLY.pdf"
source_title: "EA W256064-XALG 3.12 inch 256x64 OLED, product specification"
publisher: "Electronic Assembly (lcd-module.de)"
---

# EA W256064-XALG datasheet

**This is not a bound part.** It is a comparable third-party panel filed as corroborating evidence
for the [[er-oledm3-12-1w-display-current|display supply-current contradiction]]. It is a 3.12
inch 256 by 64 passive-matrix OLED, the same size, resolution and drive duty as the bound
[[er-oledm3-12-1w]], from a different manufacturer with an independently published current table.

[mpn::EA W256064-XALG] [manufacturer::Electronic Assembly] [controller::SSD1322]
[role::corroborating evidence, not fitted]

## Design facts reviewed

From section 5, Electrical Characteristics:

| Item | Symbol | Condition | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| Operating current | ICC | VCC = 12 V, 50% checkerboard | 24 | 32 | mA |
| Operating current | ICC | VCC = 14.5 V, 50% checkerboard | 32 | 42.5 | mA |
| Display supply | VCC | - | 14.5 | 15 | V |
| Logic supply | VDD | - | 2.5 | 2.6 | V |
| Low voltage supply | VCI | - | 3.0 | 3.5 | V |

Section 1: passive matrix, 1/64 duty, SSD1322 controller, 256 by 64 dots at 0.3 by 0.3 mm.

## Differences from the bound part

Different controller (SSD1322 rather than SSD1362), yellow rather than white, and it is a bare
panel exposing VCC directly rather than a module with an onboard boost from 3.3 V. It is
comparable on the only axis this evidence is used for: the power a 3.12 inch 256 by 64 PMOLED
takes to light its pixels.

## Related

- [[er-oledm3-12-1w-display-current]]
- [[er-oledm3-12-1w]]
