---
type: concept
date_updated: 2026-07-26
source_count: 5
confidence: high
tags: [wiki/concept, wiki/safety, wiki/battery]
---

# Fail-safe cell-temperature window

The hub qualifies external 5 V before it reaches [[pisugar3-plus]]. A cell-bonded
[[ntcle317e4103sba]] and [[tlv7042]] form independent hot and cold comparisons. Their open-drain
outputs wire together and directly enable [[ap22811aw5-7]], so firmware cannot force charging when
the analog window is false.

The 10 kohm sensor bias and existing E96 resistor values produce conservative nominal trip points
near 5 degrees Celsius and 34 degrees Celsius. This narrower window absorbs thermistor, comparator,
and resistor error while staying inside the manufacturer's 0 to 40 degree operating boundary. An
open sensor reads cold and a shorted sensor reads hot, so either wiring fault disables the input.

Firmware receives a divided copy of sensor voltage for status and calibration, but that measurement
is not in the safety-control path.

The corner sweep V3 asked for is done, in [[v3-charge-interlock]]. Simulated against the filed
[[ntcle317e4103sba-rt-curve|resistance curve]], the window holds between 2.17 and 36.43 degrees
Celsius at its widest over 384 published tolerance corners, so the claim that the narrower window
absorbs component error is now measured rather than argued. The two sensor faults were simulated
as well: both leave the enable pin at 6.3 mV against a 0.5 V guaranteed low, so charging is
inhibited either way. [permitted_window_worst::2.17 to 36.43 C]

V8 still has to verify both trip directions and both sensor faults on received hardware, because
the thresholds rest on a curve and a substitute comparator model rather than on a measurement.
