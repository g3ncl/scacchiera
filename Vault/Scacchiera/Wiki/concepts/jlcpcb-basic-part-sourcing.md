---
type: concept
date_updated: 2026-07-25
source_count: 2
confidence: medium
tags:
  - wiki/concept
---

# JLCPCB Basic-part sourcing

[applies_to::[[jlcpcb]]] [project_record::[[../../../docs/hardware/jlcpcb-sourcing.md|JLCPCB assembly sourcing]]]

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

For [[jlcpcb]] Standard PCB Assembly, each unique Extended component adds a fee. Search Basic first
and minimize Extended BOM lines. Keep an Extended selection only when no Basic part preserves the
required function, package, and electrical limits. Use Pre-Order or Global Sourcing only after safe
public-stock choices are exhausted, and submit the PCBA order only after those parts appear in My
Parts Lib.

## Sources

- [[jlcpcb-economic-parts-2026-07-24]]
- [[jlcpcb-matrix-live-stock-2026-07-25]]
- [[jlcpcb-matrix-bom-review]]

## Related

- [[jlcpcb]]
