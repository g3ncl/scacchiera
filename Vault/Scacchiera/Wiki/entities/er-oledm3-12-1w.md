---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: 2026-08-01
source_count: 3
---

# ER-OLEDM3.12-1W

Exact EastRising 256 by 64 white OLED display module used twice, one per player rail.

[mpn::ER-OLEDM3.12-1W] [supplier::BuyDisplay] [availability::in stock 2026-07-29]

The manufacturer evidence is summarized in [[er-oledm3-12-1w-manufacturer-evidence]]. Its internal
[[ssd1362]] controller supplies the four-wire SPI timing and reset limits that the module document
omits.

The 320 mA versus 2 mA current contradiction is resolved in favour of 320 mA, the figure the load
budget already used: see [[er-oledm3-12-1w-display-current]], corroborated by
[[w256064-xalg-datasheet]].

## Open V1 items

- Original manufacturer PDF not filed; the supplier download path is bot-blocked with HTTP 403.
- Datasheet revision 1.0 is **preliminary** (2025-08-07), which V1 treats as a release blocker in
  its own right.
- The 16-to-7-pin cable and module interface straps are unbound.
