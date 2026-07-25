---
type: concept
tags:
  - wiki/concept
date_updated: 2026-07-25
source_count: 2
confidence: high
---

# The TPS2553 current-limit error

A worked example of why the [Datasheets rule](../../../../CLAUDE.md) exists, kept because the failure
mode was invisible to every check the project had at the time.

## What happened

The hub's light-bar rail is protected by a TPS2553 latch-off current limiter whose trip point is set
by one resistor, R17. The design used **82 kohm**, and the value was reasoned about from a recalled
formula rather than read from the datasheet. Across a long design session the figure "about 0.67 A"
was quoted repeatedly, and every downstream decision was checked against it: whether 17 pixels fit,
whether a 12 mA LED needed a firmware brightness cap, whether 14 pixels had margin.

When the datasheet was finally filed (section 9.5.1) the real equations were:

    IOSmin = 25230 / R^1.016      IOSnom = 23950 / R^0.977      IOSmax = 22980 / R^0.94

with R in kohm. At 82 kohm that is **287 / 323 / 365 mA**, not 670 mA. The two light bars draw
**448 mA** (14 pixels x 16 mA x 2). The limiter would have tripped below the normal operating load,
so the bars would have latched dark on any bright cue, on every board built.

[wrong_value_ma::670] [actual_nom_ma::323] [load_ma::448]

## Why nothing caught it

- **ERC and DRC cannot see it.** Both check connectivity and geometry. A resistor of the wrong value
  is perfectly connected and perfectly spaced.
- **The SPICE suite did not cover it.** `test_sim_lightbar.py` validates copper droop and
  `test_sim_hub.py` validates the RF front end. Neither simulates the 5 V rail's protection path, so
  a passing 28-test suite said nothing about it.
- **It was self-consistent.** Because the same wrong number was used everywhere, every internal
  cross-check agreed. Consistency is not correctness.
- **It survived a design review of its own consequences.** The wrong limit drove a real decision (a
  firmware brightness cap) and that decision was debated on its merits, which made the underlying
  figure look settled.

## The fix

R17 became **39 kohm** (C23153, JLCPCB Basic, so free): 609 / 667 / 734 mA, giving 1.36x the load at
the *minimum* trip. The worst-case 734 mA fault reflects to about 1.24 A on 3V3, inside the
TPS63802's 2 A. See [[hub-power-tree-datasheets]].

Still open, and deliberately not closed by arithmetic: inrush into the two 100 uF bulk capacitors may
trip a limiter set only 1.36x above the steady load. That is a
[simulation-workflow](../../../../docs/simulation-workflow.md) V3 corner-sweep question, which is the
right tool for it.

## The general lesson

The dangerous parameter is not the one you know you are guessing. It is the one you are confident
about. This project's rule now reads: never take an electrical limit from a catalog listing, a search
result, or memory when a datasheet exists. The corollary this case adds is that a value used to make
a decision is not thereby validated, and that a formula recalled correctly in shape can still be
wrong by a factor of two in its constants.

Two sibling findings from the same ingest, both of which passed:

- TPS63802 511 k / 91 k gives 3.31 V against VFB 500 mV. Correct.
- TPS61023 732 k / 100 k gives 4.95 V against VREF 595 mV, and is TI's own worked example. Correct.

So the ingest was not a fishing expedition that found nothing: it found one fatal error among three
dividers, which is roughly the hit rate that justifies the discipline.

Related: [[jlcpcb-basic-part-sourcing]], [[sk6805mini-e]]
