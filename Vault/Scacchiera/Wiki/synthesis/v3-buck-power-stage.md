---
type: synthesis
date_updated: 2026-07-29
tags:
  - wiki/synthesis
  - wiki/power
---

# V3 buck power stage

Everything on the hub except the light bars runs from one 3.3 V rail made by an [[ap63203wu-7]] and
a [[nr6045s4r7mt]] inductor. Those passives came from the data sheet's application table. This is
the simulation that checks what they actually do, and, as importantly, a record of what it refuses
to claim.

## What a substitute model may and may not say

Diodes publishes no distributable model, so `hardware/sim/models/ap63203.lib` is datasheet-bounded,
the same treatment [[v3-charge-interlock]] established for the comparator. The difference here is
that a switching regulator invites a modeller to fabricate the part that is missing.

The first attempt did exactly that: a feedback loop, added only to place the operating point, which
promptly rang to 17.9 A of inductor current. The fix was not to tune it. It was to delete it. The
bench now computes the duty each corner needs from the conduction drops and drives the stage open
loop, so the model contains **no control behaviour at all** and every dynamic in it traces to a data
sheet number.

That draws a hard line around the result. This bench measures ripple, peak and RMS current, and
conduction loss. It says nothing about regulation, transient response, phase margin or stability,
because those live in a compensation network the manufacturer does not publish. Those stay data
sheet claims until V8 measures them. The DC output it reports is likewise an artifact: the real part
senses after the inductor and corrects its resistance drop, and an open-loop stage cannot.

[corners::72] [model::datasheet_bounded, open loop, no compensation]

## Result

Seventy-two corners: loads from 0.2 A to the converter's rated 2 A, 4.5 to 5.5 V in, inductance
across its 20 percent tolerance, output capacitance at nominal and half nominal.

| Quantity | Worst corner | Limit and source |
| --- | --- | --- |
| Output ripple | 3.59 mV pk-pk | 50 mV, derived from the MCU's 3.0 to 3.6 V supply range |
| Inductor peak current | 2.141 A | 2.5 A, converter's lowest guaranteed peak limit |
| Inductor RMS current | 2.015 A | 3.30 A, inductor's rated current |
| Inductor conduction loss | 138 mW | reported, not limited |

Saturation is never the binding constraint. The converter's own current limit arrives at 2.5 A,
well before the inductor's 4.97 A, so the part protects the magnetics rather than the other way
round. The 14 percent peak-current margin is at the converter's full 2 A rating, not at anything
this board draws.

## Two numbers that were easy to get wrong

**Switching frequency.** The Oscillator Frequency table lists 500 kHz and 1100 kHz on adjacent rows,
for different members of the family. This part is the 1100 kHz one. Reading the row above would have
halved every predicted ripple figure and made the filter look twice as good as it is.

**Capacitor derating.** The output capacitor's data sheet prints example bias curves, not a numeric
derating for that part number, so there is no honest way to state its effective capacitance at
3.3 V. Rather than read a number off a graph, the bench sweeps a bound: nominal, and half of nominal.
Half is well beyond what a 25 V X5R loses at 3.3 V, and it is applied only in the pessimistic
direction, since less capacitance means more ripple. A design that passes at the bound passes at the
truth. That the parts are 25 V rather than the 10 V the schematic claimed was itself a finding, made
while looking for this curve.

## What remains

The [[ap22811aw5-7]] input switch's own current limit and fault timing, and every transient case:
cold start, brownout, USB insertion, rail handover. None of the boards has a transient case yet.
