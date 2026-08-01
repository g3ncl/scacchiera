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

## Status

**Selected on assumption: the Keeppower wired 1S1P 21700 6000 mAh pack**, about EUR 11, whose
published 12 A continuous rating clears the current bounds comfortably. It still fails the
documentation acceptance above on all four counts, so the selection rests on assumption A5 in
[assumptions.md](assumptions.md): that a Seiko 1S protection PCB sits within the required windows
at typical thresholds.

This is the highest-consequence open assumption in the project, because getting protection
thresholds wrong is a safety and behaviour problem rather than a margin problem. It is carried
deliberately so the design can proceed, and a V8 test article characterises the pack before any
final-board order.
