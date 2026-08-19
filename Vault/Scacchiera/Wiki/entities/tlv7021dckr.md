---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: 2026-07-29
source_count: 1
---

# TLV7021DCKR

Exact fitted component from Texas Instruments, used by power U4 (TLV7021DCKR).

[mpn::TLV7021DCKR] [supplier::JLCPCB]
[order_code::C702120] [category::semiconductor]

The immutable source is summarized in [[tlv7021dckr-datasheet]]. The complete
library, rating, availability, and model audit is machine checked from
`docs/verification/v1-components.yaml`.

Power U4 compares a divided cell-connector voltage with a low `BAT_RAW` reference. Its open-drain output and high-impedance power-on reset leave [[csd25404q3]] off until correct polarity is proven. The reverse-cell bench includes the 8 mV maximum offset, 14 mV maximum hysteresis, 20 us power-up time, cold insertion, and insertion while the charger side is already powered.
