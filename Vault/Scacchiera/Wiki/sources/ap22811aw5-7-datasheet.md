---
type: source-summary
date_updated: 2026-07-26
tags: [wiki/source, wiki/power, wiki/safety]
---

# AP22811AW5-7 data sheet

Manufacturer data sheet for the [[ap22811aw5-7]] current-limited high-side switch. The immutable
source is [[../../Datasheets/AP22811AW5-7_C3001660.pdf]].

The active-high SOT-25 part accepts 2.7 to 5.5 V and carries 2 A continuously. At 5 V its on
resistance is 50 mOhm typical and 65 mOhm maximum at 25 degrees Celsius. Overload current limit is
2.2 to 3.2 A, short-circuit current is 0.3 A typical, and the device includes reverse-current
blocking, output discharge, undervoltage lockout, and thermal shutdown. Enable low is at most 0.5 V
and enable high is at least 1.5 V.

[mpn::AP22811AW5-7] [order_code::C3001660] [continuous_a::2]
[package::SOT-25]

The hub's independent temperature window drives enable directly. A qualified 5 V/2 A adapter is
the input boundary, while this part protects the downstream PiSugar input and prevents reverse
current when disabled.
