---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
  - wiki/power
---

# Chessboard quick-charge architecture

The former 4400 mAh pack and 500 mA linear USB charger made recharge time roughly equal to useful
play time. The first replacement study proposed a custom [[tps25730s]] and [[bq25638]] PD charger
around [[inr-21700-m65a]]. That design is now superseded because reproducing the lithium charger and
pack protection conflicts with the project's safety boundary.

[[commercial-power-subsystem-selection]] selects [[pisugar3-plus]] as a complete purchased
subsystem. It supplies a qualified 5,000 mAh pouch cell, charger, protection, uninterrupted power
path, regulated 5 V, and I2C state reporting. The chessboard hub now begins at 5 V and only creates
3.3 V for logic.

The normal source is ordinary 5 V/2 A USB. The module can accept 5 V/3 A, but USB Power Delivery is
not required. The product still targets at least ten hours of representative play; V3 predicts it
from the 18.5 Wh source and V8 measures the complete operating and recharge profiles.

The former [[rbs18634]] article and custom PD controller pair remain historical evidence. They are
not ordered, fitted, or used to justify the selected subsystem. Mechanical ventilation,
cell-temperature gating, and the seven-millimetre rail-width conflict remain open release checks.
