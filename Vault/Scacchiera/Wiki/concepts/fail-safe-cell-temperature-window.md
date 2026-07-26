---
type: concept
date_updated: 2026-07-26
source_count: 4
confidence: high
tags: [wiki/concept, wiki/safety, wiki/battery]
---

# Fail-safe cell-temperature window

The hub qualifies external 5 V before it reaches [[pisugar3-plus]]. A cell-bonded
[[ntcle317e4103sba]] and [[tlv7042]] form independent hot and cold comparisons. Their open-drain
outputs wire together and directly enable [[ap22811aw5-7]], so firmware cannot force charging when
the analog window is false.

The 10 kohm sensor bias and existing E96 resistor values produce conservative nominal trip points
near 8 degrees Celsius and 34 degrees Celsius. This narrower window absorbs thermistor, comparator,
and resistor error while staying inside the manufacturer's 0 to 40 degree operating boundary. An
open sensor reads cold and a shorted sensor reads hot, so either wiring fault disables the input.

Firmware receives a divided copy of sensor voltage for status and calibration, but that measurement
is not in the safety-control path. V3 must sweep component corners, and V8 must verify both trip
directions and sensor open/short faults on the received hardware.
