---
type: entity
date_updated: 2026-07-26
source_count: 2
tags:
  - wiki/entity
  - wiki/power
  - wiki/battery
---

# PiSugar 3 Plus

Commercial 5 V UPS and 5,000 mAh battery module selected as the chessboard's power subsystem. It
combines the battery, charger, 5 V converter, uninterrupted power path, fuel-state
estimation, controls, and I2C telemetry. See the [[pisugar3-plus-manufacturer-docs|manufacturer
documentation]] and the supplied cell's [[955465-un38-3|UN 38.3 report]].

[product::PiSugar-3-Plus] [manufacturer::Shenzhen-Non-linear-Technology]
[battery_model::955465] [capacity_mah::5000] [energy_wh::18.5]

The hub connects only to the module's 5 V output, ground, and I2C slave interface. USB charging and
the battery remain wholly inside the purchased subsystem. A July 2026 manufacturer-shop snapshot
listed the complete battery module at 49.99 USD.

Substitution is not component-level. Any replacement must provide an included qualified battery,
at least 5 V/2 A continuous output, use while charging, no restart on input removal, battery state
telemetry, and equivalent transport and protection evidence.
