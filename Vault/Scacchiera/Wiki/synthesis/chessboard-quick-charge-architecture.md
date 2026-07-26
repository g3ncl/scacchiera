---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
  - wiki/power
---

# Chessboard quick-charge architecture

The former 4400 mAh pack and 500 mA linear USB charger made recharge time roughly equal to useful
play time. The replacement combines a 6.5 Ah [[inr-21700-m65a]] cell assembly with
[[usb-c-pd-fast-charging]], targeting at least ten hours of representative play, 10-to-80 percent
charging within 90 minutes, and full termination from 10 percent within 150 minutes.

The exact implementation is [[tps25730s]] plus [[bq25638]], based on
[[pmp23456-reference-design]]. The 9 V/3 A contract provides enough input power for a 4 A battery
setting while retaining system priority. Fast charge requires the negotiated contract, acceptable
cell temperature, and the board's charge-priority load policy. Every other case folds back safely.

The readily available [[rbs18634]] module is a bounded V8 charge test article, not a replacement
for that final implementation. Its [[sw6106]] controller can charge at 4 A above 5 V input and can
charge while supplying a load. The module sheet does not prove NTC wiring, sustained thermal
performance, uninterrupted handover, or revision control. See [[quick-charge-module-evaluation]].

The remaining critical uncertainty is the battery assembly rather than the cell chemistry. A bare
21700 is not an acceptable product battery. V1 remains reopened until a protected assembly and
qualified source are exact, and V7 must prove the thicker cylinder, insulation, connector, strain
relief, and service access fit the rail.
