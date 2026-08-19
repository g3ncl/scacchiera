---
type: concept
date_updated: 2026-07-25
source_count: 3
confidence: medium
tags:
  - wiki/concept
---

# JLCPCB Basic-part sourcing

[applies_to::[[jlcpcb]]] [project_record::[[../../../../docs/hardware/jlcpcb-sourcing.md|JLCPCB assembly sourcing]]]

Select a JLCPCB Basic part only when it preserves the circuit's required value, package, electrical
limits, and function. A catalog match on package or nominal value alone is insufficient for RF
dielectrics, magnetics, protection devices, semiconductors, and feedback networks. Record unresolved
items explicitly, so a cheaper or newer candidate can be reviewed without quietly weakening the
validated design.

The catalog is an availability snapshot, so the selection remains medium confidence until the
actual JLCPCB quote confirms stock and price.

The upload BOM must use the selected manufacturer's exact MPN as its comment. Mapping an original
MPN to an electrically equivalent part from another manufacturer still triggers a mismatch and
hides which device is being purchased. Keep the human-readable value in the engineering BOM and
bind the upload with the exact MPN plus JLC code. See [[jlcpcb-matrix-bom-review]] for the validated
matrix application of this rule.

For [[jlcpcb]] Standard PCB Assembly, each unique Extended component currently adds a 2.70 EUR
feeder-change labor fee. Search Basic first and minimize Extended BOM lines. Keep an Extended
selection only when no Basic part preserves the required function, package, and electrical limits.
Use Pre-Order or Global Sourcing only after safe public-stock choices are exhausted, and submit the
PCBA order only after those parts appear in My Parts Lib.

Assembly routing is separate from electrical sourcing. Keep Basic parts with JLCPCB because their
placement avoids the Extended fee. For an Extended part, prefer hand fitting only when its pads are
accessible, the quantity is low, and inspection or rework is realistic. Fine-pitch packages,
underside thermal pads, 0402 RF networks, and repeated arrays stay with factory reflow. The project
records this decision per BOM line in the engineering BOM rather than silently dropping parts from
the JLCPCB upload.

Board-level manufacturing limits override part-level routing. The 120 by 8.5 mm lightbar is below
JLCPCB's supported assembly size, so all of its components remain hand or local-reflow work even
when an individual part is Basic.

Board-level surcharges can outweigh component sourcing. The matrix hybrid quote charged 50.47 EUR
for large-size assembly while its components cost only 7.56 EUR. Once any PCBA placement keeps that
surcharge active, moving a few additional parts to hand assembly has little economic effect. The
relevant comparison becomes full factory placement versus completely manual population.

Release an order only after a final DFM review against the chosen JLCPCB options. Check the board
outline and assembly-size limit, selected layer stack-up and copper, trace and clearance margins,
via annular rings and drill sizes, copper-to-edge clearance, solder-mask dams, and legible
silkscreen. Then run the project DRC and inspect JLCPCB's Gerber preview. The numerical guide is
[[schemalyzer-jlcpcb-design-rules-2025]]; final capability confirmation belongs to JLCPCB because
the limits and pricing are time-sensitive.

## Sources

- [[jlcpcb-economic-parts-2026-07-24]]
- [[jlcpcb-matrix-live-stock-2026-07-25]]
- [[jlcpcb-matrix-bom-review]]
- [[schemalyzer-jlcpcb-design-rules-2025]]

## Related

- [[jlcpcb]]
- [[pcba-cost-structure]], which puts these part-level rules in the context of the per-order fixed
  costs that outweigh them at one-unit quantity
