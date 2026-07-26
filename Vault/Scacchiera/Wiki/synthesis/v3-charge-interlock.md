---
type: synthesis
date_updated: 2026-07-26
tags:
  - wiki/synthesis
  - wiki/safety
  - wiki/battery
---

# V3 charge interlock proof

How does the hub prove that a cold or hot cell cannot be charged, when the part that decides has no
vendor simulation model and the sensor's data sheet prints no resistance curve?

## What the gate is

An [[ntcle317e4103sba]] bead taped to the PiSugar pouch cell biases a 10 kohm divider from the USB
inlet. Two [[tlv7042dgkr]] comparators watch that divider against a 39k/100k cold reference and a
300k/200k hot reference. Their open-drain outputs are wired together, so the shared node is high
only inside the window, and that node is the enable pin of the [[ap22811aw5-7]] switch feeding
[[pisugar3-plus]]. Firmware reads a divided copy of the sensor voltage for reporting and has no path
that can override the decision. See [[../../../docs/hardware/hub.md|the hub spec]].

## The two gaps V3 had to close first

**No published curve.** The part data sheet gives R25, B25/85 and R85, which supports only a
single-beta fit. That fit is 0.80 K optimistic at 0 degrees Celsius, and the cold cutoff's whole
margin is about 4.5 K, so the shortcut would have consumed a fifth of it in the unsafe direction.
Vishay does publish the real curve for this bead's ceramic, now filed as
[[ntcle317e4103sba-rt-curve]] and cross-checked against both resistances the part data sheet prints.

**No vendor comparator model.** The [[tlv7042dgkr]] V1 record already stated that no distributable
ngspice model was identified, and that V3 may therefore use only parameters the filed data sheet
enumerates and must sweep their full published limits. `hardware/sim/models/tlv7042.lib` is that
substitute: pull-down resistance from VOL(max)/3 mA, leakage from ILKG, and every input error left
as a swept parameter rather than a fitted guess. What the model deliberately omits is written in the
model file with the reason and the size of the term, so nothing is silently dropped.

## Method

The deck instantiates one copy of the gate per corner, emitted from the same SKiDL objects the
KiCad netlist comes from, so a schematic change reaches the simulation without a second description
of the circuit to maintain. Each copy carries the filed curve as a behavioral resistance driven by a
shared temperature node; one DC sweep of that node is a temperature sweep of every copy at once.

The corner set is exhaustive over what the parts publish: both extremes of each 1% resistance group,
4.5 to 5.5 V input, and the comparator's full error (8 mV offset plus 25 mV hysteresis) in each
direction. Series members of one divider leg move together because the trip condition is monotone in
each resistance, so a leg's extreme sum bounds every interior combination. The sensor's own accuracy
is added to the result rather than swept, because Vishay's accuracy line already carries the R25 and
B tolerances.

Sensor error is signed against the question asked, which is easy to get backwards. Deciding whether
the gate can charge a forbidden cell means assuming the bead reads toward the middle of the window;
deciding whether it can refuse a permitted one means assuming the opposite. Using one direction for
both would have reported a usable window two kelvin wider on each side than the parts guarantee.

[corners::384] [permitted_window_worst::2.17 to 36.43 C] [qualified_range::0 to 40 C]

## Result

| Quantity | Simulated | Limit and source |
| --- | --- | --- |
| Widest permitted window | 2.17 to 36.43 C | inside 0 to 40 C, [[pisugar3-plus]] safety document |
| Narrowest permitted window | 6.87 to 32.48 C | must cover 20 to 25 C, functional charge spec |
| Enable level, permitting | 4.40 V | at least 1.5 V, AP22811 VIH |
| Enable level, inhibiting | 6.3 mV | at most 0.5 V, AP22811 VIL |
| Enable level, sensor open | 6.3 mV | at most 0.5 V |
| Enable level, sensor shorted | 6.3 mV | at most 0.5 V |

The gate is conservative by construction: it gives away roughly 2 K of cold range and 3.5 K of hot
range to tolerance, and still refuses to charge well inside the cell's qualified limits. Both sensor
failure directions inhibit charging, which is what makes a lost bead safe rather than invisible.

## What this does not prove

V3 is not closed by this. The rest of the hub's power path has no simulation yet: the AP63203 buck
over line, load and temperature, the AP22811's own current limit and fault timing, the TPS2553 LED
rail trip, and every transient case (cold start, brownout, USB insertion, rail handover). Two of
those parts also lack vendor models and will need the same substitute treatment.

Nor does simulation replace measurement. The thresholds rest on a curve, a comparator model, and
ideal resistors; V8 has to measure the built gate against a real cell before any of this counts as
final. What V3 establishes is that the design has margin to measure against, rather than a nominal
number that happened to look right.
