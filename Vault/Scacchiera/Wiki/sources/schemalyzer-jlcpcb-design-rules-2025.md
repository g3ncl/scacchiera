---
type: source-summary
date_updated: 2026-07-25
tags:
  - wiki/source
---

# Schemalyzer JLCPCB design rules (2025)

[source_url::https://www.schemalyzer.com/en/blog/manufacturing/jlcpcb/jlcpcb-design-rules]
[source_date::2025-12-05] [captured::2026-07-25]

The captured third-party manufacturing guide collects JLCPCB fabrication capabilities and a
pre-order DFM checklist. It states that critical figures can change and should be verified against
JLCPCB's official capability pages before an order.

For ordinary two-layer, 1 oz work it recommends a conservative 6 mil trace and clearance target,
even though it reports a 5 mil minimum. It reports 0.3 mm as the two-layer minimum via drill and
recommends 0.8 mm pad / 0.4 mm drill for normal two-layer vias. It also lists 0.3 mm copper-to-edge
clearance, 0.1 mm solder-mask dams, 1.0 mm minimum silkscreen character height, and 0.15 mm
silkscreen line width.

The guide's release checklist covers trace and clearance rules, annular rings and drill increments,
board dimensions, silkscreen, solder-mask clearance, copper-to-edge clearance, and a final DRC.
It separately states that JLCPCB assembly has a 10 by 10 mm minimum board size. This supports the
project rule that the 120 by 8.5 mm lightbar is bare-board-only at JLCPCB.

## Project use

[[jlcpcb]] fabrication exports must be reviewed against the selected JLCPCB stack-up, copper,
finish, and assembly options at ordering time. The checklist below is general guidance, not
authority for a time-sensitive quote or capability decision.

## Pre-order checklist

- [ ] Run `make pcb-fab` from a clean tree. Use only the generated Gerbers and the matched BOM/CPL
  pair.
- [ ] Select the intended layer count, finished thickness, copper, finish, mask colour, and
  panelization. Check the JLCPCB Gerber preview for the intended outline, layers, drills, slots,
  cut-outs, and silkscreen.
- [ ] Run DRC against the chosen fabrication rules. For ordinary two-layer 1 oz work, retain a 6
  mil trace and clearance target where the layout allows. Check annular rings, drill sizes,
  0.3 mm copper-to-edge clearance, solder-mask dams, and silkscreen clearance and legibility.
- [ ] Confirm the board and panel fit bare-board and PCBA limits. The reported PCBA minimum is 10
  by 10 mm, which excludes the 120 by 8.5 mm lightbar from JLCPCB assembly.
- [ ] Upload exactly one matching pair: full BOM plus full CPL, or hybrid BOM plus hybrid CPL.
  Verify the exact selected MPN, LCSC code, footprint, side, rotation, stock, and fitted
  designators on every matched row.
- [ ] Review the total before payment, including Extended, large-size PCBA, setup, stencil, and
  nitrogen charges. Re-match Pre-Order or Global Sourcing parts only after they appear in My Parts
  Lib, then re-check live stock and price immediately before payment.

## Related

- [[jlcpcb]]
- [[jlcpcb-basic-part-sourcing]]
