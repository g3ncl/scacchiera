# Protected cell assembly

The fitted battery is a purchased protected 1S assembly, not something this project builds. This
file is the acceptance specification it must meet: the numbers a candidate pack has to satisfy and
the documents that have to exist before one can be bound. It exists because the open V1 item is not
"no candidate has been found" but "nobody wrote down what a candidate must satisfy", which left the
Keeppower pack in [battery-format-and-module-alternatives](../../Vault/Scacchiera/Wiki/synthesis/battery-format-and-module-alternatives.md)
stuck as a leading option rather than a decision.

Every bound below is derived from criteria already in [criteria.yaml](criteria.yaml) or from
[functional/power.md](../functional/power.md). None of it is new design freedom.

## Electrical acceptance

| Property | Bound | Where it comes from |
| --- | --- | --- |
| Over-discharge detection | at or below **2.8 V** | The TLV809K33 supervisor cuts the boost at 2.87 V (`POWER-BOOST-*` operating conditions). The pack's protection must be a backstop below that, not the thing that ends the discharge, or the runtime claim is governed by an undocumented threshold. |
| Over-discharge detection | at or above the cell's own datasheet minimum | Cutting below the cell's rated floor damages it. |
| Overcharge detection | at or above **4.25 V** | The BQ25895 terminates at 4.2 V; its regulation tolerance puts the real top near 4.221 V. A pack that trips at 4.2 V will nuisance-trip at every full charge. |
| Overcharge detection | at or below the cell's maximum charge voltage | Above that the protection is not protecting. |
| Overcurrent detection | at or above **6.6 A** | The worst-case discharge is 5.871 A at the 80 percent efficiency bound, and the TPS61088's guaranteed current limit is 6.502 A (`POWER-BOOST-PEAK-CURRENT` margin). The converter's own limit must act first; a pack tripping below 6.502 A turns a stress condition into a dead board. |
| Overcurrent detection | at or below the cell's continuous discharge rating | Otherwise the protection never acts before the cell does. |
| Short-circuit protection | present, with a stated trip current and delay | `POWER-SAFETY` requires it as one of the four independent protections. |
| Continuous discharge rating | at or above **4.442 A RMS** | `POWER-CELL-PASS-FET-LOSS` operating conditions. |
| Lead conductor | **18 AWG**, with insulation at most 1.85 mm | The cell link uses 430300038 terminals, rated 8.5 A against a 4.442 A RMS load. 18 AWG is also the lower-loss wire at 21 milliohm per metre. Many packs ship 22 AWG, which is the likeliest acceptance failure, and plenty of 18 AWG is jacketed above the terminal's 1.85 mm insulation limit. See [harnesses.md](harnesses.md). |

## Documentation acceptance

A pack is bindable only when all of these are filed under `Datasheets/` per the vault rules:

1. **The cell's own datasheet**, identified by exact manufacturer and revision, not "21700 6000 mAh".
   This is what supplies the charge-temperature window.
2. **The protection PCB's IC datasheet.** A listing saying "Seiko protection PCB" is not evidence:
   Seiko's 1S family spans several parts with different thresholds, and the four numbers above are
   properties of the specific IC and its sense resistor, not of the brand.
3. **The shipped construction**: how the leads attach to the cell, what insulation and sleeve are
   used, and whether the protection PCB sits at the positive end or along the body. This decides
   whether the assembly fits the 80 x 26 x 23 mm envelope reserved in
   `hardware/cad/power_rail_fit.py`, which the current STEP treats as a supplier acceptance box
   rather than a qualified fit.
4. **The shipped connector**, if any.

## What the design supplies regardless of pack

Two things no protected pack on the market provides, so they are this project's work in every case:

- **The thermistor.** `functional/power.md` requires charging to be gated on a thermistor attached
  to the cell, and protected packs do not include one. The off-board NTCLE317E4103SBA is already
  audited for this. What is still missing is a documented attachment method and thermal path;
  a sensor taped near a cell rather than bonded to it measures the air, not the cell.
- **The keyed connector.** `functional/power.md` requires the cell connector to be keyed, and the
  design binds a Molex 430250200 two-circuit housing with 430300038 terminals. Whatever the pack
  ships with is re-terminated, which means the acceptance question about lead gauge above is about
  the wire that stays, not the plug that goes.

## Open dependency this would close

`POWER-CHARGE-TEMPERATURE-MIN` and `POWER-CHARGE-TEMPERATURE-MAX` currently cite
`PISUGAR3_PLUS_safety.md`, the safety document of a module that is no longer bound, and both record
that "the fitted cell's own document must confirm or tighten this bound when one is chosen". The
0 and 40 degree window is therefore borrowed from an unrelated product. Binding a cell with its own
datasheet replaces that borrowed evidence, which is a V1 improvement and a V0 evidence-class
improvement at the same time.

## Candidate survey: 18650batterystore.com, 2026-08-02

The supplier was fixed by the owner, so this is a survey of what that catalogue can satisfy rather
than an open search. Its 21700 collection lists **eighteen cells, of which exactly one is
protected**:

| Cell | Capacity | Continuous | Price | Protected |
| --- | ---: | ---: | ---: | --- |
| **Nitecore NL2150HP** | 5000 mAh | 15 A | USD 24.95 | **yes**, button top |
| Samsung 50S | 5000 mAh | 25 A | USD 7.99 | no |
| EVE 50E | 5000 mAh | 15 A | USD 4.99 | no |
| Molicel P42A | 4200 mAh | 45 A | USD 5.99 | no |
| Samsung 50E | 5000 mAh | 9.8 A | USD 5.99 | no |
| *(thirteen more, all unprotected flat-top or tabless)* | | | | no |

**The catalogue is a bare-cell shop.** Everything except the Nitecore is an unprotected cell
intended for pack building, so the acceptance specification above selects the candidate by itself.

### Nitecore NL2150HP against the acceptance table

| Property | Bound | NL2150HP | |
| --- | --- | --- | --- |
| Continuous discharge | at or above 4.442 A RMS | 15 A | **pass**, 3.4x |
| Short-circuit protection | present | stated present | pass |
| Envelope | inside 80 x 26 x 23 mm | about 76.7 mm long (from the NL2150HPi sibling) | probable pass, needs the exact figure |
| Overcurrent detection | at or above 6.6 A | **not published** | unresolved |
| Over-discharge detection | at or below 2.8 V | **not published** | unresolved |
| Overcharge detection | at or above 4.25 V | **not published** | unresolved |
| Lead conductor | 18 AWG, insulation at most 1.85 mm | **button top, no leads at all** | **fail** |

Two of those matter and one is fatal as it stands.

**Verdict, decided 2026-08-02: the wired Keeppower pack stays selected, and this survey is why.**
Against it the NL2150HP is worse on every axis that separates them: 5000 mAh against 6000, USD
24.95 against about EUR 11, and no leads against a pack built with them. It is not better on the
axis that matters most either, because both have unpublished protection thresholds. Constraining
the supplier did not change the answer, and having the acceptance table meant that took one
comparison rather than a debate.

**The lead failure is structural, not a detail.** A button-top cell terminates in a raised positive
contact, and this design needs 18 AWG into a Molex 430250200. Two ways to bridge it, both with a
cost the acceptance table does not currently carry:

- **A 21700 holder.** Keeps the cell replaceable without tools, which is attractive for a product
  that is charged and discharged daily. It inserts spring contacts into the highest-current path in
  the product: at typical holder contact resistance of 10 to 30 milliohm and 4.442 A RMS that is
  44 to 133 mV of drop and 0.2 to 0.6 W of heating, against a boost that cuts out at 2.87 V. That
  is runtime spent, and it needs adding to the load budget rather than assumed negligible.
- **Spot-welded tabs.** Lower resistance and no added parts, but it needs a spot welder, and
  welding to the ends of an *already protected* cell risks the protection PCB it is there to keep.

**The unpublished thresholds are the same gap the Keeppower pack has**, so this candidate does not
improve documentation acceptance, and it costs USD 24.95 against the roughly EUR 11 assumed. It
buys one thing the Keeppower does not have: a named manufacturer and model whose datasheet can
actually be requested.

### If protection moved onto the power board

Recorded because the catalogue makes it tempting, **not recommended without a decision**. Accepting
an unprotected cell opens the other seventeen entries, and the best of them are better cells at a
quarter the price: Samsung 50S is 5000 mAh at 25 A for USD 7.99, Molicel P42A 4200 mAh at 45 A for
USD 5.99.

That is a design change, not a purchasing one. `functional/power.md` requires four independent
protections and this file requires them in the pack; moving over-discharge, overcharge, overcurrent
and short-circuit onto the power board means a 1S protection stage that does not exist, new V3
evidence for it, and a safety argument that currently rests on a purchased, certified assembly.
**The saving is about EUR 17 and the cost is a protection subsystem.** Do not take it for the money.

### The practical blocker nobody has checked

18650 Battery Store operates from Atlanta, Georgia. **Shipping lithium cells from the United States
to Italy is regulated under UN 38.3 and IATA rules and is refused by many carriers outright.**
Confirm the retailer actually ships cells to Italy, and at what freight cost, before treating any
row above as available. This is the item most likely to invalidate the whole survey, and it is
independent of which cell is chosen.

## Status

**Selected on assumption: the Keeppower wired 1S1P 21700 6000 mAh pack**, about EUR 11, whose
published 12 A continuous rating clears the current bounds comfortably. It still fails the
documentation acceptance above on all four counts, so the selection rests on assumption A5 in
[assumptions.md](assumptions.md): that a Seiko 1S protection PCB sits within the required windows
at typical thresholds.

**Reconfirmed 2026-08-02** against the constrained 18650batterystore.com survey above, which
offered one protected cell and it was worse on capacity, price and termination. The single thing
that survey did establish is that **"protected cell" and "wired pack" are different products**, and
this specification depends on the second: every requirement below the electrical table assumes
leads exist to gauge, terminate and route. A bare protected cell, however good, restarts that part
of the design.

This is the highest-consequence open assumption in the project, because getting protection
thresholds wrong is a safety and behaviour problem rather than a margin problem. It is carried
deliberately so the design can proceed, and a V8 test article characterises the pack before any
final-board order.
