---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: 2026-08-01
source_count: 1
---

# AD Circus SLIX2

Avery Dennison Smartrac's 21 mm round HF inlay carrying the [[sl2s2602]] die. Proposed as the
piece transponder: one per piece, 32 per set, seated in the 22 mm centered recess defined in
`docs/functional/physical.md`.

[mpn::AD Circus SLIX 2 wet inlay+] [product_code::3006370] [alt_code::IL-603074]
[manufacturer::Avery Dennison Smartrac] [supplier::Shop NFC] [order_code::724]
[category::rfid-inlay] [status::candidate, not yet purchased]

The immutable source is summarized in [[ad-circus-slix2-datasheet]].

## Fit

| Constraint | Value | Source |
| --- | --- | --- |
| Recess diameter | 22.0 mm nominal | `criteria.yaml` PHY-TAG-RECESS-DIAMETER |
| Inlay die-cut | 21 mm | inlay datasheet |
| Radial clearance | 0.5 mm | derived |
| Inlay thickness | 141 um | inlay datasheet |
| Antenna coil | 18 mm diameter | inlay datasheet |

It is the smallest round HF inlay Avery Dennison publishes, which is why it fits at all. A 25 mm
tag, the far more common size, does not.

## Cost

At Shop NFC, EUR 0.69 each in ones, EUR 0.49 at 50+, EUR 0.34 at 100+. A 32 piece set is about
EUR 22 at the 1-49 tier or EUR 16 buying 50. Negligible against the board, and cheap enough that
buying 50 to have spares for destructive V8 testing is the obvious call.

## Open V1 items

- Not purchased, so no dated availability record.
- Coil inductance and turn count are unpublished, so the V4 tag model is back-solved or measured
  rather than read off a datasheet. See [[ad-circus-slix2-datasheet]].
- No second source identified. Avery Dennison disclaims continued availability.

## Related

- [[sl2s2602]]
- [[row-column-antenna-matrix-technique]]
