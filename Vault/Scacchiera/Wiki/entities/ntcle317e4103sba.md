---
type: entity
date_updated: 2026-07-26
source_count: 2
tags: [wiki/entity, wiki/safety, wiki/battery]
---

# NTCLE317E4103SBA

Vishay wire-leaded 10 kohm NTC selected as the chessboard's cell-contact temperature sensor. It
connects to hub J11 and is bonded to the supplied PiSugar pouch cell. See
[[ntcle317e4103sba-datasheet]] for the part itself and [[ntcle317e4103sba-rt-curve]] for the
resistance curve, which the part data sheet does not print.

[mpn::NTCLE317E4103SBA] [order_code::C3154341] [manufacturer::Vishay]
[r25_ohm::10000] [b25_85_k::3984] [accuracy_k::1.0]

`hardware/sim/thermistor.py` holds the filed curve as the single place the design reads it from, and
[[v3-charge-interlock]] is the corner sweep that rests on it.

Substitution requires an insulated wire-leaded sensor with a filed resistance curve and equal or
better temperature accuracy. Firmware calibration and comparator thresholds must be regenerated.
