---
type: concept
date_updated: 2026-07-29
source_count: 2
confidence: high
tags:
  - wiki/concept
  - wiki/power
---

# USB Type-C 5 V current advertisement

The current chessboard does not negotiate USB Power Delivery. Its two 5.1 kohm Rd resistors make it
a passive sink, so a Type-C or laptop PD charger supplies 5 V. The hub measures the CC voltages on
the two unused ADC channels documented by [[esp32-c6-mini-1u-datasheet]], then applies the source
classes from [[usb-type-c-r2-current-advertisement]].

Both CC pins are measured because cable orientation decides which one carries Rp. A 10 kohm series
resistor and 100 nF capacitor on each ADC input make a 1 ms low-pass while leaving Rd directly on
the connector. The highest valid CC level is 2.04 V, below the MCU's 3.3 V supply.

The safe policy is asymmetric. A voltage below attachment or above the connected range is invalid.
A voltage in a threshold gap keeps the lower current class. The BQ25895 starts at 500 mA, a 1.5 A
advertisement permits no more than 1.5 A total input, and a 3.0 A advertisement permits the board's
1.970 A hardware ceiling. No branch requests or accepts a voltage above 5 V.

This is distinct from the superseded [[usb-c-pd-fast-charging]] architecture, which proposed an
explicit 9 V contract and a separate PD controller.
