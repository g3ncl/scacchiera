---
type: source-summary
date_updated: 2026-07-25
tags:
  - wiki/source
---

# JLCPCB matrix live stock, 2026-07-25

[source::JLCPCB public parts inventory API] [captured_at::2026-07-25T08:25:53+02:00]
[raw::[[../../Clippings/jlcpcb/matrix-live-stock-2026-07-25.csv]]]

The live query checked all 11 exact JLC codes in the matrix assembly BOM. Every selected Basic or
Extended part had public stock above JLCPCB's required quantity for five assembled boards. The
smallest absolute inventory was 25,001 BAR64-02V PIN diodes against a requirement of 160. The
smallest stock ratio was therefore still more than 156 times the order requirement.

This is a point-in-time inventory capture. The later cost review replaced Extended C273642 with
Basic C5947 in a pin-compatible SOIC-16 footprint, so the immutable raw capture is historical for
that one line. Re-run JLCPCB matching immediately before payment.

## Related

- [[jlcpcb]]
- [[jlcpcb-basic-part-sourcing]]
- [[jlcpcb-matrix-bom-review]]
