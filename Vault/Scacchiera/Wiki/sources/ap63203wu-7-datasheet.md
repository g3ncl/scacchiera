---
type: source-summary
date_updated: 2026-07-26
tags: [wiki/source, wiki/power]
---

# AP63203WU-7 data sheet

Manufacturer data sheet for the [[ap63203wu-7]] fixed 3.3 V synchronous buck converter. The
immutable source is [[../../Datasheets/AP63203WU-7_C780769.pdf]].

The input range is 3.8 to 32 V, output current is 2 A, switching frequency is 1.1 MHz, and the
typical quiescent current is 22 uA. The fixed-output application table specifies a 3.9 uH inductor,
10 uF input capacitance, two 22 uF output capacitors, and a 100 nF bootstrap capacitor. The data
sheet permits 2.2 to 10 uH and requires adequate saturation and RMS current margin.

[mpn::AP63203WU-7] [order_code::C780769] [output_v::3.3] [output_a::2]
[package::TSOT-23-6]

The selected 4.7 uH [[nr6045s4r7mt]] remains inside the allowed range, with 4.97 A minimum
saturation and 3.3 A minimum thermal current ratings. The fixed-output part eliminates the former feedback divider and
the buck-boost converter's second switch node.
