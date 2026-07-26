---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
  - wiki/power
---

# Quick-charge module evaluation

Cheap 1S fast-charge boards exist. The most useful named candidate found for the chessboard is the
6.76 EUR [[rbs18634]], based on [[sw6106]]. It negotiates USB-C PD, can request a voltage above
5 V, and advertises up to 4 A cell charging. An ideal 4 A constant-current interval supplies 70
percent of a 6.5 Ah [[inr-21700-m65a]] in 68.25 minutes, which is close enough to the 90-minute
product requirement to justify measurement.

It does not replace the final [[chessboard-quick-charge-architecture]]. Its seller sheet recommends
an external protection board, and it omits module-level proof of NTC wiring, thermal performance,
dimensions, revision control, and uninterrupted output handover. The controller supports
simultaneous charge and output, but multiple active ports fall back to 5 V. The resulting 2.5 A
nominal charge current would need 109.2 ideal minutes for the same 10-to-80 interval before losses,
so simultaneous play and fast charging are different test cases.

The module is therefore a bounded V8 article for four measurements: sustained idle-board charge
current and time, cell and board temperature, safe NTC interruption, and output continuity during
source insertion and removal. A passing charge cycle validates the battery operating point. It
does not validate the final hub power path. A failed handover confirms that the final hub needs the
NVDC [[bq25638]] path or an equivalent qualified charger.
