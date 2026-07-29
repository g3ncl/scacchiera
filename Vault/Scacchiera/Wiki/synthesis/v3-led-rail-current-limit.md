---
type: synthesis
date_updated: 2026-07-29
tags:
  - wiki/synthesis
  - wiki/power
---

# V3 light-bar rail current limit

The hub feeds both light bars through a [[tps2553dbvr-1]] latch-off limiter whose trip point is set
by one resistor. That resistor's value came from the data sheet's IOS formula, and
[[../../../../docs/simulation-workflow.md|the workflow]] is explicit that a board is not done while
its only evidence is a formula. This is the simulation that replaces it.

## What had to be true

Two things, pulling in opposite directions:

- The limiter must **not** trip on a legitimate bright cue. Both bars at full white draw 448 mA
  (14 pixels per bar, 16 mA each, two bars).
- It must clamp a fault **below** what the harness can carry. The light-bar connectors are rated
  1.0 A per contact, and a shorted bar cable is exactly the fault this part exists for.

A 39 kohm programming resistor was chosen for that window. An earlier 82 kohm choice would have
tripped at 287 to 365 mA, below the load, so the rail would have latched off on any bright cue; that
error is recorded in [[tps2553-current-limit-error]].

## Method

TI publishes a transient PSpice model for the part, already in the repository as an archive. It was
extracted unmodified and wrapped in a six-pin subcircuit so the emitter can instantiate it from the
hub's own SKiDL objects, the same way every other bench here works: the rail's connectivity comes
from the schematic, not from a hand-drawn copy.

Corners are both extremes of the 1% programming resistor and the 4.5 to 5.5 V range the
[[../../../../docs/hardware/power-module-interface.md|module interface]] admits. Each corner runs the
real load, then a dead short.

[corners::6] [model::vendor transient, TI SLVM425A]

## Result

| Quantity | Simulated | Limit and source |
| --- | --- | --- |
| Both bars at full white | 444 mA at 4.459 V | must not trip; bars draw 448 mA |
| Clamp into a short | 657 to 670 mA | at most 1.0 A, connector contact rating |
| Formula agreement | 664 mA against 668 mA computed | within one percent |

The useful outcome is not that a number changed, because it did not. It is that the number now has
measurement-shaped evidence behind it instead of arithmetic, and that the agreement is close enough
to say the data sheet's formula was being read correctly.

One limit on what this proves: the spread the model shows is **resistor tolerance only**. It carries
no IC process variation, so the data sheet's own 609 to 734 mA spread remains the worst case. Both
criteria are written against the data sheet numbers, with the simulation as confirmation rather than
as the limit itself. That is the difference between using a vendor model and hiding behind one.

## The conflict this turned up

TI's model enables on EN low. TI's data sheet for this part says EN is active high, and that the -1
suffix selects latch-off rather than an inverted enable. Recorded in detail on [[tps2553dbvr-1]].

The data sheet governs, the schematic already followed it, and the wrapper inverts in one place so
the discrepancy cannot leak into a bench and quietly invert a conclusion. It also means this bench
proves nothing about the enable thresholds themselves, which is stated in the model file rather than
left for someone to assume.

## What remains

The rest of the hub's power path: the AP63203 buck over line, load and temperature, the AP22811 input
switch's own current limit and fault timing, and every transient case. Neither Diodes part has a
distributable vendor model, so both need the documented substitute treatment that
[[v3-charge-interlock]] established.
