---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: 2026-07-31
source_count: 1
---

# TCA9535PWR

Exact fitted component from Texas Instruments, used by hub U6 (TCA9535PWR).

[mpn::TCA9535PWR] [supplier::JLCPCB]
[order_code::C130204] [category::semiconductor]

The immutable source is summarized in [[tca9535pwr-datasheet]]. The complete
library, rating, availability, and model audit is machine checked from
`docs/verification/v1-components.yaml`.

Its power-on reset behaviour shapes the hub's power-off case. The part has no reset pin, and it
resets again only after its supply falls below VPORF, 0.75 V minimum. Without a discharge path the
3.3 V rail decayed only through unspecified leakage, so hub R36 was added to make that decay a
specified 1.46 s. A warm reset does not reach the expander at all, so its ten driven nets survive
at whatever firmware last wrote.
