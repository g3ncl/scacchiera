---
type: concept
date_updated: 2026-07-26
source_count: 6
confidence: high
tags:
  - wiki/concept
  - wiki/power
---

# USB-C PD fast charging

The chessboard's quick-charge architecture uses [[tps25730s]] to establish an explicit USB-C PD
contract and [[bq25638]] to convert that power efficiently into a controlled single-cell charge
while maintaining the system rail. This replaces the MCP73871 linear charger, whose USB mode caps
the whole input at 500 mA.

The target is 9 V/3 A input and 4 A battery charging into a protected assembly based on
[[inr-21700-m65a]]. The charger reduces battery current when system load, input current,
temperature, or voltage regulation requires it. A 5 V or lower-current source is a safe fallback,
not a fast-charge source.

[[pmp23456-reference-design]] proves the selected controller pair at 5 V/3 A and 9 V/3 A and around
93 percent measured 3 A charge efficiency. The 4 A chessboard operating point remains a V3 and V8
obligation rather than an inference from that measurement.

Low-cost power-bank modules are useful measurement articles but have a different evidence boundary.
The [[rbs18634]] and its [[sw6106]] controller advertise the required charge current, yet only the
controller data sheet documents the NTC and simultaneous-output features. The module document does
not establish their exact implementation or prove uninterrupted rail handover. A module may
calibrate charge-current and thermal models without becoming the final qualified power path.
