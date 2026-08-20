---
type: log
date_updated: 2026-07-30
tags:
  - wiki/log
---

# Operation Log

Append-only record of every wiki operation. Each entry header follows the shape
`## [YYYY-MM-DD] operation | Title` so it stays greppable:

```bash
grep "^## \[" Wiki/log.md | tail -5
```

Never rewrite existing entries. Add new ones at the bottom.

## [2026-07-24] setup | Scaffold the llm-wiki

Created the `Wiki/` structure (`sources/`, `entities/`, `concepts/`,
`synthesis/`) with starter [[index]], [[log]], and [[overview]]. Configured the
vault attachment folder (`assets/`) and the download-attachments hotkey. No
sources ingested yet.

## [2026-07-24] ingest | NFC Game Board (nfcgameboard.com) and the BitwiseID white paper

Captured four nfcgameboard.com pages (home, schematics, pcb, software) as raw HTML converted to
markdown clippings, plus every linked downloadable file (schematics in sPlan-8 and PDF form,
component datasheets, Sprint Layout 6.0 PCB design files, four standalone PCB PDFs, and the
BitwiseID white paper PDF), all under `Clippings/nfcgameboard.com/`. The existing BitwiseID
transcription (previously `docs/software/bitwiseid.md`) moved into
`Clippings/nfcgameboard.com/bitwiseid-whitepaper.md` as the raw source for that white paper, since
it is third-party reference material, not our own spec.

Ingested: 5 source summaries ([[nfcgameboard-home]], [[nfcgameboard-schematics]],
[[nfcgameboard-pcb]], [[nfcgameboard-software]], [[bitwiseid-whitepaper]]), 3 entities
([[ben-bulsink]], [[nfc-game-board-project]], [[clrc632]]), 5 concepts
([[bitwiseid-method]], [[bitwisexy-method]], [[set-management-and-setid]],
[[row-column-antenna-matrix-technique]], [[pin-diode-antenna-switching]]). Updated [[index]] and
[[overview]].

This is the prior art behind the chessboard project's pivot onto an 8x8 row-column antenna matrix
as the committed hardware direction; `docs/hardware/row-column-matrix.md`,
`docs/hardware/sensing.md`, and `docs/hardware/design-review.md` were updated in the same session
to reflect it and now link into this wiki instead of raw nfcgameboard.com URLs.

Not captured this round: `/why`, `/videos`, `/mechanics`, `/embedded`, `/presentation` (linked
from the captured pages, noted in [[index]] under Unprocessed sources).

## [2026-07-24] lint | Remove pivot framing now that row-column is the starting design

The chessboard project restarted the hardware design from scratch around the row-column matrix, so
it is no longer a pivot away from a prior 64-antenna target; that framing is now stale. Deleted
`[[row-column-pivot-decision]]` (its content was entirely about the pivot decision, now moot).
Reworded [[overview]], [[index]], and [[row-column-antenna-matrix-technique]] to drop "pivot",
"committed implementation", and "frozen reference" language while keeping the NFC Game Board prior
art itself, which is unaffected: it is still the reference architecture for the row+column technique
regardless of what came before it in this project. `Clippings/` sources were not touched (immutable).


## 2026-07-24: hardware rebuild decisions folded back into the wiki

The from-scratch hardware rebuild (docs/planning.md) reached its board designs, closing two
questions the wiki had marked open. Updated [[clrc632]]: our hub now carries the **PN5180**, the
successor the NFC Game Board author validated against the CLRC632, chosen because ISO/IEC 15693
is where [[bitwiseid-method|BitwiseID]] is proven. Updated [[pin-diode-antenna-switching]]: the
rebuilt matrix board re-adopted the technique as a single-ended half of the old hybrid cell,
re-validated in ngspice. Design detail lives in `docs/hardware/`, not here; these edits only
un-stale the wiki's "open decision" language. `Clippings/` untouched.

## [2026-07-24] ingest | JLCPCB economic-parts catalog snapshot

Captured the 2,004-row JLCPCB economic-parts CSV under `Clippings/jlcpcb/`, then ingested it as
[[jlcpcb-economic-parts-2026-07-24]]. Created [[jlcpcb]] and
[[jlcpcb-basic-part-sourcing]], updated [[index]] and [[overview]], and recorded the project-level
Basic selections plus intentionally unresolved parts in
`docs/hardware/jlcpcb-sourcing.md`. The catalog is a dated availability snapshot, so it informs
but does not replace a live JLCPCB quote.

## [2026-07-24] query | Validate the matrix JLCPCB assembly BOM

Filed [[jlcpcb-matrix-bom-review]] after resolving JLCPCB comment mismatches, unavailable matches,
and a PCB-copper pseudo-part. Updated [[jlcpcb-basic-part-sourcing]], [[index]], and [[overview]].
The final matrix upload has 11 exact JLC-bound rows and matching 165-reference BOM/CPL sets. The
stocked BAR64-02V PIN-diode substitution passed the matrix RF limits under a conservative model.

## [2026-07-25] ingest | Matrix live JLCPCB inventory

Captured the 11 selected matrix parts and their live public stock as
[[jlcpcb-matrix-live-stock-2026-07-25]]. Updated [[jlcpcb]],
[[jlcpcb-basic-part-sourcing]], [[index]], and [[overview]]. Every matrix selection exceeded its
five-board order quantity. Public Basic and Extended stock is the first choice; Pre-Order and
Global Sourcing remain explicit fallbacks when no safe stocked equivalent exists.

## [2026-07-25] lint | Correct Extended-component fee policy

Updated [[jlcpcb-basic-part-sourcing]] to treat the JLCPCB Extended fee per unique component, not
per PCB design. The production rule is now Basic-first, with an Extended line retained only when no
safe Basic part preserves the required function, package, and electrical limits.

## [2026-07-25] query | Separate factory and hand assembly candidates

Extended [[jlcpcb]] parts were classified by package access, quantity, and rework risk. The
engineering BOM now distinguishes factory placement from practical hand-solder candidates without
altering the upload BOM automatically. Connectors and low-count accessible packages are candidates
for external purchase; hidden-pad, fine-pitch, tiny, and repetitive parts remain factory work.

## [2026-07-25] correction | Route the complete lightbar to manual assembly

The lightbar's 120 by 8.5 mm outline is below [[jlcpcb]] assembly support. Its board-level rule now
overrides per-part classifications: the hand BOM contains every fitted component and both JLCPCB
BOM/CPL pairs are intentionally empty. Bare-board fabrication remains supported.

## [2026-07-25] query | Calibrate Extended fees from the hub quote

The live hub hybrid quote established a 2.70 EUR labor fee per charged Extended component, replacing
the earlier incorrect 25 EUR estimate. Seven charged feeder changes produced 18.88 EUR after quote
rounding. The quote confirmed 29 of 31 detected rows and reported inventory shortages only for U4
and Y1. Updated [[jlcpcb-basic-part-sourcing]] and the production sourcing register.

## [2026-07-25] query | Review the matrix hybrid quote

The matrix hybrid upload matched all ten rows with no shortages. Its 141.05 EUR PCB plus PCBA quote
is driven by 68.21 EUR in combined large-size charges, not its 7.56 EUR component cost or 13.48 EUR
Extended fee. Updated [[jlcpcb-basic-part-sourcing]] and the sourcing register: selective hand
fitting cannot remove the assembly large-size charge, so the useful decision is full PCBA versus
complete manual population.

## [2026-07-25] ingest | JLCPCB design-rule and pre-order reference

Captured Schemalyzer's 2025 JLCPCB design-rule guide under `Clippings/schemalyzer.com/` and
ingested it as [[schemalyzer-jlcpcb-design-rules-2025]]. Updated [[jlcpcb]],
[[jlcpcb-basic-part-sourcing]], [[overview]], and [[index]]. Its practical DFM and order-release
tasks remain in the source summary, not project documentation. The source itself says that
capabilities can change, so live JLCPCB settings and quote validation remain authoritative.

## 2026-07-25: datasheet layer added, three parts rebound

Operation: schema change plus a four-datasheet ingest, driven by a hub assembly order that JLCPCB
could not fill.

Schema: `CLAUDE.md` and `AGENTS.md` gained a Datasheets section. `Vault/Scacchiera/Datasheets/`
now holds raw component datasheets, immutable like `Clippings/`, named `<MPN>_<LCSC>.pdf`. The rule
is read-before-choosing (never take an electrical limit from a catalog listing when a datasheet
exists) and file-after-binding (source summary, entity page, index, log).

Ingested: [[esp32-c6-mini-1u-datasheet]], [[pn5180-crystal-and-clock-requirements]],
[[txc-7m27100009-datasheet]], [[sk68xx-mini-e-led-datasheets]].
New entities: [[esp32-c6-mini-1u]], [[pn5180]], [[txc-7m27100009]], [[sk6805mini-e]].

What the datasheets changed, that a catalog listing would not have:

- **U4** ESP32-C3-MINI-1U-N4X (no stock) to ESP32-C6-MINI-1U-N4. Vendors call the C6 "pin-to-pin
  compatible" with the C3-MINI series; Table 3-1 shows that holds only for power, ground, EN and
  UART0. Native USB moves to pins 17/18 and pin 21 becomes NC, so the old map would have put SCLK
  on USB_D+ and the reader's chip select on a no-connect.
- **Y1** EXS00A-CS01188 (no stock) to TXC 7M27100009 in 3225. PN5180 Table 142 wants CL 10 pF and
  ESR under 100 ohm; the new part is 10 pF and 60 ohm. The load capacitors went 10 pF to 15 pF,
  because two equal caps present C/2 plus stray and the old pair presented 8 pF, spending about
  41 ppm of a +/-100 ppm budget on load error alone.
- **D1-D14** WS2812C-2020 to SK6805MINI-E, because the light bar is hand-populated and the
  WS2812C's pads sit under its body. Its legs are wider, so 14 pixels fit a 120 mm bar where 17
  did not, changing `docs/functional/interface.md`.

Contradiction recorded, not resolved: the two OPSCO LED documents give different pinouts and
package outlines, and LCSC publishes nothing for C5200774. See [[sk6805mini-e]] for the open risk.

## 2026-07-25 (later): twelve datasheets filed, one fatal value found

Operation: ingest of the remaining bound-part datasheets, plus grounded mounting holes and a
defect pass, ahead of starting `docs/simulation-workflow.md`.

Filed 12 more datasheets, taking `Datasheets/` to 17: the hub power tree and logic
([[hub-power-tree-datasheets]]) and the matrix switch-cell discretes
([[matrix-discrete-datasheets]]).

**The ingest caught a fatal error.** R17 set the TPS2553 light-bar current limit to 287/323/365 mA
where the load is 448 mA, so the bars would have latched dark on every board built. The 82 kohm value
came from a recalled formula, not the datasheet. Changed to 39 kohm (609/667/734 mA), which is
JLCPCB Basic so it cost nothing. Written up as [[tps2553-current-limit-error]] because ERC, DRC and a
passing 28-test suite were all blind to it.

Two sibling dividers checked out against the same ingest: TPS63802 511k/91k gives 3.31 V against
VFB 500 mV, TPS61023 732k/100k gives 4.95 V against VREF 595 mV and is TI's own worked example. The
BAR64-02V model's "2.5 ohm at 10 mA, 100 MHz" is now datasheet-backed too.

New open questions the datasheets raised rather than settled:

- The 10 uH choke publishes one current number, 15 mA, and does not say whether it is a heating or a
  saturation limit. The design biases it at 10.29 mA, 69% of that. Needs a V3 sweep.
- MCP73871's THERM pin wants a 10 kohm NTC, which is on no BOM.
- `USBLC6-2SC6_C2687116.pdf` is a UMW document, not ST: LCSC lists UMW for that order code.
- LCSC's brand tags disagree with the documents it serves for BSS123 and BSS84. Recorded, not
  resolved; V1 treats a documentation conflict as a release blocker.

Also removed `models/bap64_02.lib` and its registry entry: the BAP64-02 it modelled was replaced by
the BAR64-02V and nothing referenced it. Corrected `matrix.py` and `matrix.md`, which still described
the cell as using a BAP64-02 at 3 ohm.

## 2026-07-25 (later still): mounting holes, and both matrix defects traced to one bug

Operation: hardware change plus a defect pass, ending with all three boards DRC clean from a
scratch rebuild.

**Grounded mounting holes.** A new `BoardBuilder.add_mounting_hole` places M2.5 plated holes bonded
to a net, so the enclosure screws tie the shell to the pours rather than floating. KiCad's
MountingHole footprints carry `exclude_from_bom` and `exclude_from_pos_files`, which is what keeps
them out of the JLCPCB upload files: a hole is not a part to place. Four at the hub's corners, two
on the matrix past each end of the switch-cell array. None on the light bar, and that is a finding
rather than an omission: J1, the pixels and the bulk capacitor occupy x 0.77 to 117.85 of a 120 mm
board, against the 5.40 mm an M2 pad plus clearance needs, and a 4.4 mm pad on an 8.5 mm board would
leave 2.05 mm of material either side of the screw.

**The matrix's two reported defects were one bug.** U1's placement was a bare 3.5 mm, which put its
pads 8 and 9 at x = -1.245: entirely off the board. Pad 9 is SEL_CHAIN, and a pad outside the outline
is a pad Freerouting cannot reach, which is why routing failed on exactly that net. The 0.025 mm
edge clearance reported on pads 7 and 10 was the same bug one pin further in. U1 is now seated by
measuring its own courtyard, not its pads (a SOIC's outline is drawn wider than its pad field), so
neither fault can recur if the footprint or rotation changes, and C65 follows it.

**The four shared serial nets were taken away from the router.** Freerouting reached U1's and U2's
0.65 mm serial pins unreliably, leaving a different one bare each run, and `_postroute_fixups` then
patched whatever it left relative to where it stopped. Three skip heuristics were measured (a
distance proxy, any-peer connectivity, all-peer connectivity) and all left the board sometimes clean
and sometimes not, which is the evidence that no skip rule fixes it: the patch was downstream of a
nondeterministic input. Their copper is now ripped up after import and all four paths drawn from
measured pad positions.

Three orderings make those paths provably non-crossing, and they are not the same ordering:

- lanes keep the U1 pad order, so the left-margin verticals are parallel;
- crossing y rises with lane x, so each horizontal clears the lanes to its right;
- turn-up x falls as U2 pad y rises, and the net reaching U2's highest pad rounds the far side of U2
  because its vertical would otherwise be tall enough to cut every other final leg;
- J1 taps get rows of their own, ordered by how far right each hop reaches, because SEL_SRCLK runs
  rightward from a lane left of its pin while SEL_RCLK runs leftward from a lane right of its pin.

Lanes also moved off the U1 pad x onto their own 1.3 mm pitch: U1's pins are on 1.27 mm and J1's on
1.25 mm, so lanes at the pads interleaved with J1's pads about 0.44 mm away, against the 0.525 mm a
0.4 mm via needs from a 0.25 mm lane.

Two approaches were tried and reverted, both recorded in the code so they are not repeated: running
the crossing band above U2 instead of below (19 violations against 1), and freeing U1's pad row to
let 3V3 through (fixes the rail, splits the ground pour into islands).

**Final state**, rebuilt from an empty `generated/`: light bar, matrix and hub all at 0 DRC
violations and 0 unconnected, 28 tests passing, mypy clean across 27 files.

Open, and stated plainly: the serial nets are deterministic but Freerouting's own completeness is
not. The hub needed three route attempts to reach 0 unconnected and the matrix one. `make
pcb-*-route` is therefore not yet clean by construction; re-run it, or raise `FREEROUTING_PASSES`.
## [2026-07-25] verification | V0 executable traceability

Operation: built the V0 requirement and numeric-criteria evidence structure.

Mapped all current functional documents into 71 atomic requirement IDs with named tests and pinned
the reviewed inputs by SHA-256. Replaced the flat nominal SPICE thresholds with 37 structured
criteria carrying units, evidence source, operating conditions, and margin, then added automated
checks for freshness, completeness, uniqueness, and bidirectional links. Filed the design rationale
as [[verification-evidence-model]]. The pass also removed the stale 17-pixel WS2812 wording from the
criteria after the light bar changed to fourteen SK6805MINI-E pixels.

## [2026-07-25] verification | V1 exact component and library proof

Audited the 59 purchased fitted MPNs generated by the three authoritative schematics. Filed every
immutable manufacturer datasheet and generated one exact source summary and entity page per MPN,
with the complete catalog in [[index]]. `docs/verification/v1-components.yaml` now binds supplier,
order code, dated availability, footprint, board uses, pin and package audit, ratings fields, model
treatment, source page and entity page. Six automated tests enforce exact parity with the
schematics and reject missing sources, open conflicts, provisional records and Samsung's mis-served
environmental declarations.

The audit resolved three release blockers rather than waiving them. The lightbar now uses the exact
Harvatek T37K3RGB-05C000112U1930 and DigiKey cut-tape code. The matrix now uses Diodes Incorporated
BSS123-7-F and BSS84-7-F, with their exact JLC codes and Diodes vendor SPICE models. The ESP32-C6
module and Würth boost inductor gained stocked DigiKey cut-tape sources. Historical conflicting raw
files and summaries remain immutable and are explicitly marked superseded.

## [2026-07-26] verification | V2 static connectivity and deterministic routing

Closed the V2 connectivity gate and filed the rationale as [[v2-static-connectivity]]. Replaced the
hub's generic USB connector model with the native alphanumeric USB-C symbol, grounded the TPS63802
and PN5180 exposed pads, moved plated mounting holes into the schematics, and enumerated every
reviewed no-connect against its filed datasheet. Connector tests now cover both cable ends, service
headers, boot and power-off defaults, recovery pads, and exact USB identities.

Versioned the reviewed matrix and hub route sessions. Normal builds import them, while new
Freerouting candidates require explicit reroute targets. Matrix serial and power escapes plus hub
USB shield and recovery geometry remain deterministic code-owned routes. A clean full gate reports
zero DRC violations, zero unconnected items, zero schematic-parity issues, mypy clean, and 43 tests
passing.

## [2026-07-26] design | Replace the slow linear charger

Captured and ingested the current Molicel INR-21700-M65A, TI TPS25730S, TI BQ25638, and TI PMP23456
primary sources. Filed [[chessboard-quick-charge-architecture]] and
[[usb-c-pd-fast-charging]]. The resulting product requirements bound representative runtime,
10-to-80 and full recharge time, PD fallback, power-path behavior, battery protection, and
temperature gating.

The selected target is a protected 6.5 Ah cell assembly charged at 4 A from a negotiated 9 V/3 A
source. Because this replaces the MCP73871 and passive Type-C sink, the hub portions of V1 and V2
are reopened. The exact protected pack source, schematic, footprint, route, simulation, and measured
charge cycle remain open and are not represented as passing evidence.

## [2026-07-26] query | Evaluate purchased quick-charge boards

Filed the immutable [[rbs18634-datasheet]] module sheet and [[sw6106-datasheet]] controller data
sheet, created [[rbs18634]] and [[sw6106]], and answered the buy-versus-build question in
[[quick-charge-module-evaluation]]. The named module was available for 6.76 EUR and advertises 1S,
18 W PD, and 4 A charging.

The cheap board is retained as a V8 battery, thermal, NTC, and cable-handover test article. It does
not replace the final NVDC charger: its module sheet recommends external battery protection and
does not publish its NTC wiring, schematic, complete BOM, dimensions, sustained thermal rating,
handover time, or revision control. Updated [[chessboard-quick-charge-architecture]],
[[usb-c-pd-fast-charging]], [[overview]], and [[index]] without treating unknown module behavior as
validated evidence.

## [2026-07-26] decision | Select a commercial battery subsystem

Filed the complete PiSugar 3 Plus product, I2C, safety, 3D, and 955465-cell UN 38.3 sources. Created
[[pisugar3-plus-manufacturer-docs]], [[955465-un38-3]], [[pisugar3-plus]],
[[commercial-battery-subsystem]], and [[commercial-power-subsystem-selection]].

The selected boundary is a purchased 5,000 mAh UPS producing regulated 5 V with I2C state data.
The custom TPS25730S/BQ25638 charger and RBS18634 test article are historical, not active designs.
The manufacturer documents uninterrupted cable changes and an included transport-tested cell, but
also expose two release obligations: the vendor assembly is 57 mm across a 50 mm rail, and its
temperature register measures the charger IC rather than the cell. Neither issue is waived.

## [2026-07-26] design | Bind the simplified hub power boundary

Filed and ingested [[ap63203wu-7]], [[swpa5045s4r7mt]], [[ap22811aw5-7]], [[tlv7042]], and
[[ntcle317e4103sba]]. The hub will accept a qualified fixed 5 V/2 A source, gate it to the PiSugar
input pad through an independent analog cell-temperature window, receive uninterrupted 5 V back,
and make 3.3 V with one fixed-output buck.

The analog window uses only existing E96 resistor values and nominally permits charging from about
8 to 34 degrees Celsius. This deliberate inner guard band absorbs component error inside the
PiSugar manufacturer's 0 to 40 degree operating range. Open and short sensor wiring both disable
charging. Created [[fail-safe-cell-temperature-window]] and updated [[overview]] and [[index]].

## [2026-07-26] design | Implement the commercial power boundary

Replaced the superseded charger and boost tree in the authoritative hub schematic with the
power-only USB-C inlet, [[tlv7042]] temperature gate, [[ap22811aw5-7]] protected PiSugar input,
PiSugar 5 V and I2C return, [[ap63203wu-7]] 3.3 V buck, and direct protected lightbar supply. IO2
now measures the divided thermistor voltage while UART remains the recovery interface.

The earlier [[swpa5045s4r7mt]] selection failed a manufacturer-table cross-check before binding:
the claimed MPN is absent from the filed series data. Filed and bound [[nr6045s4r7mt]] instead,
with a data-sheet-derived footprint and documented current, saturation, resistance, and thermal
margins. Corrected the nominal cold threshold from the earlier estimate to about 5 degrees
Celsius. Five focused static connectivity tests pass; generated-board ERC, BOM, V1 audit, routing,
and full V2 closure continue in their applicable phases.

## [2026-07-26] verification | Reclose V1 component proof

Regenerated the component evidence from the rebuilt schematics. The exact inventory is now 44
unique purchased fitted tuples, down from 59 after removing the custom charger, battery path and
duplicate boost stages. Added explicit external records for [[pisugar3-plus]] and
[[ntcle317e4103sba]] so their interface and safety-relevant ratings are checked without assigning
fictional PCB footprints.

The four new fitted power parts record their actual selected electrical and package limits, and
the [[nr6045s4r7mt]] footprint follows its filed land pattern. The regenerated wiki catalog and
structured audit have no open conflicts. Seven V1 component-proof tests pass, including exact
schematic parity, immutable sources, model classification, and external power-component evidence.

## [2026-07-26] verification | Bind exact comparator footprint

PCB DRC exposed 0.15 mm pad clearance in the generic KiCad VSSOP footprint, below the hub's 0.2 mm
rule. Replaced it with a code-generated [[tlv7042dgkr]] DGK0008A land pattern using the dimensions
in the filed Texas Instruments data sheet. The regenerated component audit and seven V1 tests pass.

## [2026-07-26] verification | Close rebuilt hub V2

Replaced the superseded hub placement and route around the commercial [[pisugar3-plus]] boundary.
The 110 x 46 mm hub now uses four copper layers because the dense two-layer trials repeatedly
stranded different MCU and NFC nets and left a fragmented return. USB VBUS, the temperature-gate
branch, USB shield, reader SCLK, and ground stitching are deterministic code-owned geometry.

The versioned route reproduces 0 DRC violations, 0 unconnected items, and 0 schematic-parity issues.
Five focused static tests pass, so [[v2-static-connectivity]] and the hardware plan advance through
V2. Power and fault simulation remains the next gate.

## [2026-07-26] verification | Carry the four-layer stack into fabrication

Auditing the four-layer decision found that the Gerber export named a fixed outer copper pair, so a
hub fabrication package would have silently omitted In1.Cu and In2.Cu, including the inner VBUS and
SCLK branches. The export now reads the stack from the board's own layer table, and a test asserts
the generated hub matches the stackup recorded in
[[v2-static-connectivity]]'s evidence file. Also corrected a stale hub comment claiming flashing runs
over USB-Serial-JTAG: the inlet is power-only, so recovery is UART0 on J9, as the hub document
already said. `make check` passes with 47 tests.

## [2026-07-26] ingest | File the cell sensor's resistance curve

The [[ntcle317e4103sba]] data sheet publishes R25, B25/85 and R85 but no R/T table, which left the
charge cutoff's thresholds resting on a single-beta fit. Filed Vishay's own curve for this bead's
ceramic as [[ntcle317e4103sba-rt-curve]], extracted from document 29130 with its sheet and row
recorded. It reproduces both resistances the part data sheet prints and the published B constant, so
the two sources confirm each other. The fit it replaces was 0.80 K optimistic at 0 degrees Celsius,
in the unsafe direction, against a cold margin of about 4.5 K.

## [2026-07-26] verification | Simulate the charge interlock over every corner

Built the first V3 power evidence for the hub: [[v3-charge-interlock]]. The gate is emitted from the
hub's own SKiDL objects, so the deck cannot drift from the netlist, and swept over 384 corners
covering both extremes of each 1% resistance group, 4.5 to 5.5 V input, and the [[tlv7042dgkr]]
comparator's full published offset and hysteresis in both directions. Worst case the gate permits
charging only from 2.17 to 36.43 degrees Celsius, inside the cell's qualified 0 to 40 range, while
its tightest corner still covers the functional 20 to 25 degree charge band. An open or a shorted
sensor both inhibit charging.

Two supporting pieces landed with it: `hardware/sim/models/tlv7042.lib`, a datasheet-bounded
substitute model that records what it omits and why, and a small extension to the SPICE emitter so a
test bench can take one named block of a board and drive it at a tolerance corner. Five new criteria
and their traceability links record the enable-level and usable-window limits. `make check` passes
with 53 tests.

One correction worth recording: the first version of the sweep applied the bead's accuracy in the
permissive direction for both the safety question and the usability one. That is right for the first
and backwards for the second, and it reported a usable window two kelvin wider on each side than the
parts guarantee. The safety result was unaffected.

V3 stays open: every switching converter on the hub and every transient case is still unsimulated.

## [2026-07-29] design | Two-layer hub and a swappable power boundary

Cost work, driven by the power subsystem being the most expensive line in the product. Two changes.

The hub is two layers again, so every board in the product is. Four layers had been chosen because a
110 x 46 mm two-layer route would not converge; the answer was to buy length instead of copper,
since the service volume is a 310 mm rail holding only this board. At 162 x 46 mm, with the
functional zones slid apart so the crossings open while clusters stay intact, the route closes at
0 violations, 0 unconnected and 0 schematic-parity issues. Three things had to go with the layers:
the SCLK bridge and comparator branch, which were workarounds for the four-layer failure and would
have slotted the ground return, and the free-standing stitching vias, which only worked because four
pours meant a via anywhere landed in copper.

The back copper under the reader's match and the run to the matrix connector is now a reserved
plane, no tracks, vias allowed. The routed board has zero signal segments inside it. The reserve
starts clear of the reader itself: covering the QFN-40 stranded nine of its own pins, since a 6 mm
package needs both faces to escape.

Two placement faults surfaced as routing failures and were fixed as placement: the crystal sat below
the reader while its clock pins are on the upper left edge, so the oscillator loop wrapped the
package, and the switch's input capacitors sat 9 mm off the rail they decouple. Both are better
placements independent of whether a router can close them.

Second change: the power module is no longer [[pisugar3-plus]], or any product. `J3` carries a
generic module's 5 V, optional I2C and the cell terminal, and the board divides that terminal into
its own ADC, so battery reporting does not rest on any module's register map. Both halves of the
link went seven-way after the connector data sheets showed 1.0 A per contact against a board that
draws about that much. Charge speed relaxed to 240 minutes for 10 to 80 percent at 1 A, which is
what admits the cheap module tier.

That withdrew V1's audit of the PiSugar boundary, so **V1 is open again**: a part nobody has chosen
cannot have a passing audit. Every board part still passes.

## [2026-07-26] query | Cell format and module alternatives against the rail

Asked whether a flat cell would fit the player rail, which lithium format is cheapest, and whether a
better shaped alternative to [[pisugar3-plus]] exists. Filed as
[[battery-format-and-module-alternatives]]. The finding that matters: the seven-millimetre overhang
is mostly the cell, not the board, since the LP955465 pouch is 54 mm wide on its own, so any fix has
to reshape the cell. Height is not scarce, width is.

Cylindrical 18650 and 21700 remain the cheapest per watt-hour, but on a single 18 Wh pack the saving
is a few euro against a holder, a separate protection board and a centimetre of height, so a 1S pouch
is the right choice here despite costing more per watt-hour. Two of the reasons
[[commercial-power-subsystem-selection]] rejected the smaller DFRobot module have weakened, which
reopens an unbundled module-plus-chosen-cell option at roughly 35 to 40 EUR.

## [2026-07-29] lint | Align docs and wiki after the two-layer and module changes

Health check across `docs/` and the vault, prompted by two structural changes landing at once.
Corrected: the recorded stackup evidence still described a four-layer hub and six static tests, the
catalog row and the battery survey still called the hub 110 x 46 mm, and [[v1-component-proof]] and
[[v3-charge-interlock]] still read as though [[pisugar3-plus]] were bound.

Two findings worth more than a text fix. Fifteen cross-references from wiki subfolders into `docs/`
used one `../` too few and resolved to a directory that does not exist; top-level pages used the same
depth correctly, which is how the error survived. And the qualified 0 to 40 degree charge window,
which [[v3-charge-interlock]] validates the gate against, is sourced from the safety document of a
cell that is no longer bound. The limits stand for now and are marked provisional in
[[../../../docs/hardware/criteria.yaml|criteria.yaml]] until a cell is chosen, since the gate's worst
case leaves about two kelvin of room at the cold edge for a tighter bound.

Nineteen entity pages are orphaned, almost all parts from the superseded charger design
([[mcp73871t-2cci-ml]], [[tps63802dlar]], [[tps61023drlr]], [[usblc6-2sc6]] and similar). They are
history rather than rot, so they stay unlinked rather than being wired into pages that no longer use
them.

## [2026-07-29] verification | Measure the light-bar current limit on the vendor model

Second piece of V3 for the hub. The 39 k resistor programming the [[tps2553dbvr-1]] limiter had only the
data sheet's IOS formula behind it, and the workflow is explicit that a formula is not release
evidence. TI publishes a transient PSpice model for this part, already filed in the repository as an
archive; extracted, wrapped and driven from the rail's own SKiDL connectivity, it carries both light
bars at full white (444 mA at 4.459 V) without tripping and clamps a short at 657 to 670 mA across
resistor and supply corners.

The model agrees with the formula to within one percent, which is the useful outcome: the number was
right, and now it has evidence rather than arithmetic behind it. The spread the model shows is
resistor tolerance only, so the data sheet's own 609 to 734 mA process spread stays the worst case
and both new criteria are written against that rather than against the simulation.

Two findings came out of using it. ngspice needs PSpice compatibility to parse TI's ABM primitives,
which is now scoped to this bench through a `.spiceinit` beside the deck rather than set globally.
And **TI's model contradicts TI's data sheet**: the model enables on EN low, while the data sheet for
this part states EN is active high and that the -1 suffix selects latch-off rather than an inverted
enable. The data sheet governs the fitted part, the schematic already follows it with a pull-down
that keeps the rail dark at power-up, and the wrapper inverts in one place with the contradiction
written next to it. Recorded on [[tps2553dbvr-1]] as an open conflict against the vendor model, not against
the design.

## [2026-07-29] correction | Eight capacitors carried the wrong voltage rating

Gathering power-stage parameters for the buck simulation meant opening the output capacitor's
manufacturer data sheet, which describes CL21A226MAQNNNE as a 25 V part. The schematic called it
10 V. Auditing every voltage-bearing capacitor label against its filed data sheet found four of five
part numbers wrong, eight component records in all:

| Part | Labelled | Filed data sheet |
| --- | --- | --- |
| CL05A105KA5NQNC | 1u 10V | 1 uF **25 V** |
| CL10A105KB8NNNC | 1u 10V | 1 uF **50 V** |
| CL21A106KAYNNNE | 10u 10V | 10 uF **25 V** |
| CL21A226MAQNNNE | 22u 10V | 22 uF **25 V** |
| CL10A225KO8NNNC | 2.2u 16V | 2.2 uF 16 V, correct |

Every error understates the fitted part, so nothing was operating over its rating and the boards were
always safe. The risk was downstream: these strings become the Comment column of the JLCPCB BOM, and
a 10 V description invites a substitution to a genuinely 10 V part, which at 5 V with derating would
be a real one. The corrected ratings are now in the schematic and regenerated into
`docs/verification/v1-components.yaml`.

It also improves the numbers the buck bench will use: a 25 V X5R 0805 loses far less capacitance to
DC bias at 3.3 V than a 10 V part would, so the output filter is better than the label claimed.

## [2026-07-29] correction | Scope PSpice mode to one directory

The light-bar bench needs ngspice's PSpice compatibility to parse TI's model, enabled through a
`.spiceinit`. Written into the shared `generated/hub/` directory it also reached the charge-interlock
deck sitting beside it, whose behavioral resistances stopped parsing: ngspice reads that file from
the deck's directory, not only from the working directory it is invoked in. Five interlock tests
errored in the full check that caught it.

The bench now generates into its own directory. Worth remembering as a general shape: a per-run
configuration file is still global state if two runs share a directory, and the thing that found it
was running the whole suite rather than the tests near the change.

## [2026-07-29] verification | Simulate the 3.3 V buck power stage

Third V3 piece for the hub. Everything except the light bars runs from this rail, and its inductor
and capacitors were chosen from an application table rather than a simulation. 72 corners of load,
input voltage, inductance tolerance and output capacitance give 3.59 mV of ripple against a 50 mV
budget, 2.141 A of inductor peak against the converter's 2.5 A lowest guaranteed limit, and 2.015 A
rms against the inductor's 3.30 A rating. Saturation never binds: the converter current-limits first.

Two dead ends worth recording, both from trying to make the model do more than it should. A feedback
loop added to place the operating point rang to 17.9 A, so it was deleted rather than tuned: the
bench now computes duty analytically per corner and the model contains no control behaviour at all,
which is what its header claimed anyway. And measuring ripple over a long window caught the LC
startup ring, because an open-loop stage is nearly undamped; the deck now starts at its operating
point and measures whole switching periods.

Two data sheet details that would have been easy to get wrong. The AP63203 switches at 1100 kHz, not
the 500 kHz on the adjacent row of the same table, which would have halved the predicted ripple. And
the output capacitor's data sheet prints only example bias curves, no numeric derating for that part,
so effective capacitance is treated as a bound (half of nominal) applied in the pessimistic direction
rather than as a number nobody can source.

## [2026-07-29] verification | Check the input switch by arithmetic, not simulation

Started a SPICE bench for the [[ap22811aw5-7]] input switch and abandoned it, which is the useful
part of this entry. A current-limited switch written with min() or max() has a flat region and a
kink in its characteristic; the operating point stopped converging, and ngspice printed "DC solution
failed" alongside numbers that the bench happily parsed as results. Smoothing it with tanh did not
help, because a hard saturating element has almost no derivative over most of its range.

The problem was the approach. The switch is a resistor with a current limit, so its steady state is
Ohm's law on data sheet values, which the workflow already recognises as Derived evidence. It is now
`hardware/verification/charge_path.py` and three tests, with no model and no deck. What genuinely
needs simulating on this path is the transient, and that is blocked on binding a module whose input
capacitance sets the inrush.

Doing the arithmetic carefully surfaced something the simulation would not have. At the top of its
published spread the switch passes 3.2 A, while the three J2 contacts carrying it are rated 1.0 A
each. Contact ratings are continuous and a fault in limit is not, since the part burns about 16 W
into a short and shuts down thermally in milliseconds, so it is recorded for V8 rather than treated
as a violation. A test pins the 0.2 A overshoot so it cannot change size unnoticed.

Worth keeping: a bench that parses whatever ngspice prints will report a failed solve as a
measurement. The numbers looked plausible enough to write down.

## [2026-07-29] verification | Close the hub's V3 transients, and say what cannot close

The transient cases V3 asks for split three ways on this board, and only one of the three is
board-side. Handover and source insertion are the power module's behaviour, measured at V8.
Transient response and stability rest on a compensation network Diodes does not publish, so no
honest model here can produce them. What is left is bounded by conduction and charge and reduces to
arithmetic on filed values, so `hardware/verification/rail_budget.py` derives it rather than dressing
it as a simulation: 36 mA of inrush over the 4 ms soft start, dropout at 3.51 V input, and about five
microseconds of hold-up.

The dropout figure earned its keep immediately. The power-module interface required a 5 V output at
1.3 A but never said how far that output could sag, and now it does: 4.0 V, which is the hub's
3.51 V dropout plus half a volt for cable and connector drops the figure excludes. Five microseconds
of hold-up is also worth stating plainly, because it means the rail follows its input and riding out
a source change is the module's job, which is exactly what the contract already demands of it.

The hub's V3 work is now complete to the limit of what a model can honestly say. The gate stays open
on two measured items rather than on missing effort.

## [2026-07-29] verification | Derive the coincident worst-case load

The power-module interface obliges a module to supply 1.3 A, and that number was an estimate written
while defining the contract. `hardware/verification/load_budget.py` now derives it from filed data
sheets with everything doing its worst at once: the radio at its 382 mA transmit peak, the reader at
its 250 mA TVDD maximum, both light bars white, the matrix biased, both displays active. The total is
1.14 A, so the obligation holds with 12 percent in hand.

The derivation exposed a gap it could not close. The two ER-OLEDM3.12-1W display modules are fixed by
the functional specification, but they have no filed data sheet and no V1 record, so their current is
an allowance rather than a value, and it carries about a fifth of the 3.3 V rail. The allowance is
deliberately generous, so filing the real sheet can only reduce the total, but V1 now lists the
displays alongside the unbound power module as its second open item. A test asserts the assumed share
stays under a third, so the budget cannot drift further onto a number nobody has filed.

## [2026-07-29] verification | Settle the matrix choke's rating

The plan had carried the 10 uH bias choke's 15 mA rating as an open V3 concern, because the design's
own bias band runs to 14 mA and the RF bench only ever ran one nominal point. Sweeping the bias over
the rail's 3.27 to 3.33 V regulation band and the setting resistor's 1 percent tolerance gives 10.08
to 10.58 mA, so 29 percent of the component maximum stays unused and the 14 mA end of the band is not
reachable in practice.

Worth separating the two numbers, since conflating them is what made this look risky. The 7 to 14 mA
band is a specification of what the design wants the bias to be. The 15 mA is what the part can take.
A criterion now exists for each, and the second one names the component's own data sheet rather than
the design's intent.

## [2026-07-29] verification | Waveform integrity on the cabled buses

Last of the V3 bullets that is board-side. Two buses leave the hub on a cable and both are bounded
rather than measured, since nothing in `docs/` dimensions the harnesses.

The light-bar data line is self-clocked, so the useful metric is not edge speed but pulse-width
distortion: a uniform delay shifts both edges alike and the pixel never notices. What it does notice
is the buffer sourcing through about 150 ohm and sinking through 55 ohm, which stretches the high
time by 15 ns at a 150 pF cable bound against the 50 ns the pixel's symbol table allows.

I2C rises in 796 ns at the specification's own 200 pF ceiling. That fits standard mode with a fifth
in hand and does not fit fast mode, which would need the bus under about 70 pF. So the bus is a
standard-mode bus, and that is now a criterion rather than an assumption firmware could quietly
break. A test asserts the fast-mode failure as well as the standard-mode pass, so the constraint
cannot be lost by someone strengthening a pull-up and forgetting why it was there.

## [2026-07-29] lint | Reconcile what V3 actually covers

After a run of V3 work it was worth checking the claim rather than the effort. An earlier entry in
the plan said the hub's V3 was "complete to the limit of what a model can honestly say", and that was
too strong. Walking the workflow's own six cases instead of the list of things built turns up items
that are neither module-side nor blocked by unpublished compensation, and simply are not done:
temperature corners, capacitor ESR, junction-temperature estimates, warm reset, power-off discharge,
repeated brownout, current-limit latch timing, open load, stuck control signal, and USB and display
SPI waveform integrity.

The plan now lists V3 case by case with what is covered and what is missing, so the gate reads as
partly done rather than nearly done. Two things did close in the same pass: the matrix serial link's
edge rate against the shift registers' own 139 ns/V transition-rate specification, and a note that
the same edge is a third of a half period at 4 MHz, which a rule of thumb would flag even though the
sourced limit is met eight times over. Keeping both means raising the clock later is a decision, not
an accident.

## [2026-07-29] design | A custom power board, panelised with the light bars

Reversing the buy decision, on the reasoning that panelising removes the fabrication cost that made
custom lose. That reasoning holds for the PCB and only for the PCB: the evidence burden of putting a
lithium charger in the design is unchanged, and V1 and V3 both open further because of this board.

The design leans entirely on the interface contract written a few days ago. The board implements it
rather than defining its own boundary, so the hub is untouched, V2 stays passing, and a bought module
is still a drop-in replacement. The cell-temperature interlock stays on the hub where it has corner
evidence, and the hub keeps measuring cell voltage itself, so nothing on the new board is trusted for
either safety or telemetry.

[[mcp73871t-2cci-ml]] comes back from the superseded charger design, and so do [[tps61023drlr]] and
the PH cell connector, which is why this took hours rather than days: their data sheets were still
filed and their entities merely orphaned. The part was rejected the first time for charging at
500 mA, which made a recharge as long as a session. The relaxed 240-minute limit lets it run at its
full 1 A and clear that with 30 minutes in hand.

Three places where the honest answer was to refuse a number. The 220k and 30k feedback divider was
abandoned when the catalogue returned two different order codes for the same part; it is now three
resistors this design already carries. L1 is bound from the manufacturer's own series table inside an
already-filed data sheet, with its order code recorded as an open V1 item rather than guessed, after
a search surfaced the rejected SWPA family again. And the boost's stock footprint holds 0.15 mm
between pads against a 0.2 mm rule, so it uses TI's own land pattern, whose row-to-row gap of 0.14 mm
then needs a clearance exception scoped to that part rather than to the board.

The panel is 130.1 by 63.0 mm, two bars and the power board on four five-hole mouse-bite tabs,
generated from the routed boards so it cannot disagree with them. It also fixes something already
wrong: a 120 by 8.5 mm light bar is below the outline JLCPCB will assemble, which is why the bars
were routed to hand assembly. The panel is not.

## [2026-07-29] audit | Bring the power board under V1 and V2 evidence

Regenerated the fitted-component catalog from all four authoritative schematics. The power board
adds four exact audited tuples: [[mcp73871t-2cci-ml]], [[tps61023drlr]], the PH cell connector and
the 330 kohm feedback resistor. Existing component pages now record their additional power-board
uses. The exact NR6045S1R0NT order code still could not be verified, so it is a structured V1
blocker rather than a fabricated catalog binding.

The audit extractor now reads one board per subprocess and combines only immutable part fields.
This keeps the matrix and hub from occupying one SKiDL process at the same time while still deriving
the result from their real builders. V2 evidence now also records the power board's zero DRC,
unconnected and parity results, its deliberate no-connects, and both ends of its hub interface.

## [2026-07-29] audit | Bind the power inductor and correct the display load

Replaced the unverified power L1 with [[dfe252012f-1r0m-p2]], LCSC C435392, using Murata's
0.8 by 2.0 mm recommended pads. A fresh reviewed route passes with zero DRC violations,
unconnected pads and parity issues, and the panel still measures 130.1 by 63.0 mm.

Ingested [[er-oledm3-12-1w-manufacturer-evidence]]. Its electrical table says 320 mA maximum active
current and 2 mA sleep current, while the product page calls 2 mA the active maximum. The design now
uses the conservative 320 mA, raising coincident module load to 1.48 A. That exposes TPS61023's
guaranteed current-limit corner as inadequate, so the converter needs replacement before V3 can pass.

## [2026-07-29] design | Establish the 10 W single-cell power basis

The product now requires regulated 5 V at 2 A from the battery subsystem. A cylindrical cell may
run lengthwise along the player rail, making the filed [[inr-21700-m65a]] candidate's 21.7 mm
diameter the relevant cross-section rather than its 70.2 mm length. The exact protected assembly
remains open.

Filed and ingested [[bq25619rtwr-datasheet]] and [[tps61088rhlr-datasheet]] before using them as
replacement candidates. The audit also rejected the existing JST PH battery connector and the
two-contact JST GH output at 10 W because neither has deliberate current margin.

## [2026-07-29] design | Implement and bound the 10 W custom power board

Replaced the superseded charger and boost with [[bq25619rtwr]], [[tps61088rhlr]],
[[tlv809k33dbvr]], and [[cdmc8d28np-1r2mc]]. Bound [[430450800]] and [[430450200]] Micro-Fit
headers for the output and cell paths. Regenerated the complete V1 component catalog and its source
and entity pages from all four authoritative schematics.

The routed 90 by 32 mm board and the matching eight-pin hub boundary reproduce zero DRC violations,
unconnected items, and parity issues. A 54-corner datasheet-bounded ngspice switching-stage sweep
passes the 10 W ripple and current-stress criteria. TI's official transient model is preserved, but
its ngspice compatibility copy does not switch, so control-loop and charger fault evidence remain
open rather than being waived. The filed [[inr-21700-m65a]] proves one-cell geometry and discharge
capability, while the complete protected assembly and mating harnesses remain V1 blockers.

## [2026-07-29] audit | Bind the Micro-Fit mating interface

Corrected the mating-side family from plug series 43020 to receptacle series 43025 using Molex's
own Micro-Fit product specification. Selected [[430250800]] and [[430250200]] housings with
[[430300038]] 18 AWG female terminals. The exact wire, qualified crimp or pre-crimped leads, color
coding, strain relief, and complete harness remain open rather than being implied by the connector.

## [2026-07-29] design | Raise the 10 W battery-path margin

Replaced the 5 A BQ25619 battery path with [[bq25895rtwr]], LCSC `C80200`, in the same RTW
WQFN-24 package. The filed manufacturer data sheet rates the new path at 6 A continuous, 9 A for
one second, and a 9 A overcurrent threshold. The 200 ohm ILIM network independently caps input at
1.970 A while unconnected D+ and D- preserve the 500 mA unknown-source startup default.

The reviewed 90 by 32 mm route and 130.1 by 63.0 mm panel remain clean. The 54-corner boost stage
now separates its switching result from an 80 percent efficiency current bound, which reaches
5.681 A peak and 4.422 A RMS. An eleven-case averaged NVDC model covers source priority,
supplement, removal, missing and depleted cells, short circuit, and the temperature gate against a
stuck command. Reversed-cell protection is explicitly failing until V1 binds a complete protected
keyed battery assembly.

## [2026-07-29] design | Recognize 5 V Type-C source current

Filed and ingested [[usb-type-c-r2-current-advertisement]], a five-page official specification
extract covering sink power states, debounce, and the exact CC voltage thresholds. The hub retains
its two passive Rd terminations and adds independent 10 kohm, 100 nF filtered ADC paths on IO0 and
IO1. [[usb-type-c-5v-current-advertisement]] records the conservative policy: default current until
a stable 1.5 A or 3.0 A advertisement is measured, with invalid and gap voltages resolving down.

Moved NFC IRQ and LED data to IO7 and IO14, then generated a fresh reviewed hub route. Reproduction
from that session passes with zero DRC violations, unconnected items, and schematic parity issues.
The path never negotiates PD and never requests or accepts more than 5 V.

## [2026-07-29] design | Isolate reversed cell insertion

Filed and ingested [[csd25404q3-datasheet]] and [[tlv7021dckr-datasheet]]. Power Q1 uses the TI
DQG land pattern as a bidirectional high-side pass FET, while U4's open-drain, high-impedance POR
output holds it off until the cell connector proves positive. A BAT54H clamps the reversed sense
input and a 100 kohm gate-source pullup makes the unpowered state safe.

The ngspice bench covers cold and already-powered insertion at both polarities. A correct 2.87 V
cell has 1.14 V of worst comparator margin. A reversed 4.2 V cell leaves the protected charger BAT
node at minus 5.8 mV with USB absent and positive 4.2 V with USB present. The 4.422 A RMS hot loss
bound is 0.331 W. A fresh reviewed route and the unchanged 130.1 by 63.0 mm panel reproduce cleanly.

## [2026-07-30] design | Bound the boost capacitance corners

The previous two-capacitor output bank did not preserve its 150 mV ripple margin once the Samsung
initial tolerance and X5R temperature limit were combined with the existing DC-bias sensitivity
bound. Added a third [[cl21a226maqnnne]] 22 uF capacitor and routed the 90 by 32 mm power board
again. The reviewed route, panel, and manufacturing export remain clean.

The expanded 162-corner ngspice bench also applies TI's recommended minus 30 percent inductor
corner and a derived 15 milliohm assembled-bank ESR acceptance limit. It reaches 138 mV ripple,
5.325 A switching-model peak, and 3.877 A switching-model RMS.
The conservative 80 percent efficiency bound reaches 5.871 A peak and 4.442 A RMS. The TPS61088
maximum switch resistances already cover its minus 40 to 125 degree Celsius electrical range.
The capacitor sheet supplies no part-specific DC-bias curve or 500 kHz ESR maximum, so those remain
open measurements instead of being inferred from its 120 Hz dissipation-factor test.
The complete gate passes with all four boards at zero violations, zero unconnected items, and zero
parity issues, mypy clean on 76 source files, and 124 tests passing.

## [2026-07-30] design | Stabilize the boost compensation

Filed and ingested [[0402b223k500nt-datasheet]], a Basic 22 nF, 50 V, X7R 0402 capacitor for
power C13. JLCPCB showed more than one million assembly units while LCSC retail showed no stock,
so the two catalog channels remain explicitly distinct.

Implemented TPS61088 data-sheet equations 13 through 17 as a 4,374-corner small-signal sensitivity
analysis. The former 4.7 nF compensation value falls below TI's 45 degree phase-margin guidance.
The fitted 22 nF value reaches 54.64 degrees minimum phase margin, infinite modeled gain margin,
and a maximum crossover at 80.3 percent of TI's ceiling. The amplifier transconductance is swept
plus or minus 30 percent, but TI publishes only a typical value, so V3 loop closure remains open.
A fresh reviewed power route, the 130.1 by 63.0 mm panel, and manufacturing export reproduce with
zero power-board DRC violations, unconnected items, or parity issues. The complete gate passes all
four boards at zero findings, mypy on 78 source files, and 129 tests.

## [2026-07-30] research | Keep the cell candidate provisional

Checked the exact [[inr-21700-m65a]] against current European supply. NKON listed the flat-top cell
out of stock, and Akkuparts24 offered only a September 2026 preorder. The filed one-page sheet gives
a 71.0 mm maximum height while Molicel's product page says 70.2 mm, so the larger envelope now owns
mechanical planning and the contradiction remains open.

A newer tentative Molicel approval sheet exposed through NKON requires pack protection and direct
FET cutoff of both charge and discharge on cell overtemperature. It could not be downloaded into
the immutable vault outside the browser, and several of its fields remain TBD or estimated, so it
is reconnaissance rather than V1 evidence. The protected assembly now explicitly requires this
bidirectional temperature cutoff. ABLIC S-82D1A is recorded only as an architecture candidate
until an exact suffix, protection circuit, and qualified pack assembler are bound.

Recorded Eltec in Italy and ANV Production in Poland as quote candidates. Neither has been
contacted or selected. The acceptance request must return exact protection thresholds,
construction, test, and transport evidence, not merely price and nominal capacity.

Added a build123d power-rail fit model. It reserves an 80 x 23 x 23 mm protected-pack envelope
around the 71.0 x 21.7 mm candidate cell, places the routed 90 x 32 mm power board beside it, and
leaves 125 mm after clearances. This closes only the provisional allocation question; a supplier
drawing, lead bend, retention, and complete rail fit remain V7 work.

The complete gate regenerated all four boards with zero DRC violations, unconnected items, or
parity issues, passed mypy on 81 source files, and passed all 133 tests. The build123d import emits
14 upstream Python 3.14 deprecation warnings; they do not change the generated geometry or test
result.

## [2026-07-30] research | Prefer completed-pack cost over bare-cell price

Compared current 21700 offers against the 4.442 A RMS and 5.871 A peak battery bounds. The Samsung
58E at 18650 Battery Store was the cheapest credible cell at USD 3.15, but the seller does not offer
online lithium-cell shipping to Italy and the offer excludes protection and assembly. NKON listed
the same bare cell at EUR 3.45.

Recorded Keeppower's wired 1S1P 6000 mAh protected pack as the leading total-cost candidate. Its
European listing gives 5900 mAh minimum, 12 A continuous discharge, the four mandatory electrical
protections, and a maximum listed body of 75.45 x 22.25 mm. The roughly EUR 11 price includes the
protection PCB and leads. Selection remains open until the cell revision, protection thresholds,
wire gauge, connector, thermistor retention, exact construction, and transport evidence are filed.

Expanded the mechanical pack allocation laterally from 80 x 23 x 23 mm to 80 x 26 x 23 mm. This
keeps the pack below the 24 mm rail height while reserving side space for the bonded thermistor.
The board position and 125 mm unused rail length do not change.

The regenerated STEP and all four allocation tests pass. Mypy is clean on 81 source files and all
133 tests pass. The 14 warnings are the existing upstream Python 3.14 lib3mf deprecations.

## [2026-07-30] ingest | File the SSD1362 controller timing

Filed and read Solomon Systech's complete 62-page SSD1362 Rev 1.0 data sheet. Added
[[ssd1362-datasheet]] and [[ssd1362]], then linked the controller to both purchased
[[er-oledm3-12-1w]] modules. Table 12-4 supplies the four-wire SPI limits missing from the module
capture: 100 ns minimum clock period, 15 ns maximum edges, and bounded clock, data, chip-select and
address setup and hold times.

The 15 ns edge limit derives a 57.86 pF absolute load ceiling from the weaker guaranteed ESP32-C6
drive side. The V3 implementation uses a 50 pF complete-load acceptance limit and fixes display SPI
to mode 0 at 4 MHz. The exact harness remains a V1 blocker until its cable, connector and module
input stay within that bound. The data sheet's advance-information status and 25-degree timing
condition remain explicit rather than being treated as guaranteed temperature-corner evidence.

## [2026-07-31] verify | Extend the display SPI segment to the control lines

Added `HUB-DISPLAY-SPI-CONTROL-TIMING` so the segment covers the whole of [[ssd1362]] Table 12-4
rather than only the write-data rows. Chip select needs 20 ns of setup and 10 ns of hold, and
command/data needs 15 ns and 40 ns, which makes the 40 ns D/C# hold the largest single obligation
on the bus, larger than the 30 ns write-data hold the earlier criterion treated as the worst case.

Framing both control lines a full clock period around each burst leaves 237.04 ns at the bounded
50 pF load, close to six times that obligation. Mypy is clean on 81 source files and the signal
integrity and traceability tests pass.

## [2026-07-31] verify | Close the warm reset, power-off and brownout cases

Walking the generated hub schematic showed the 3.3 V rail has no discharge path at all. The
[[ap63203wu-7]] is the fixed-output part, so there is no feedback divider and no output discharge,
and every pull on the board ends on a high-impedance node. The decay was therefore unspecified
leakage, which matters because [[tca9535pwr]] section 7.4.1 requires VCC below VPORF, 0.75 V
minimum, before another power-on reset happens.

Added hub R36, 10 k across 3V3, reusing an already-bound resistor. It reaches that floor in 1.46 s
against a 2.0 s limit, discharging 97.7 uF summed from the hub and matrix schematics plus a 20 uF
acceptance allowance for each unbound display module. It costs 333 uA while the board runs, 0.025
percent of the coincident rail load, and nothing while the board is off. That time is also the
off-time that turns repeated brownout into a bounded case.

The warm reset case needed no change but did need stating. MCU_EN reaches only its pull-up, delay
capacitor and recovery pad, so no peripheral resets with the MCU, and the TCA9535 has no reset pin,
so its ten driven nets survive at whatever firmware last wrote. That enumeration is now generated
from the schematic and handed to V6.

A fresh Freerouting session was needed for R36. The promoted route passes at zero DRC violations,
zero unconnected items and zero parity issues. Mypy is clean on 83 source files.

## [2026-07-31] verify | Bound junction temperature for every dissipating part

Read the thermal tables of [[ap63203wu-7]], [[tps2553dbvr-1]], [[tps61088rhlr]], [[bq25895rtwr]] and
[[csd25404q3]]: 89, 182.6, 38.8, 31.8 and 55 degrees per watt, with the CSD sheet also giving 160
for minimum pad copper, and a 150 degree junction limit throughout.

Stating one junction temperature would need an ambient nobody has measured, so each case is
inverted into the highest ambient the part tolerates. The light-bar limiter reaches 145.1 degrees,
the charger 103.5, the reverse FET 96.5 on the pessimistic 160 figure, the buck 81.0, and the boost
53.0. The allowance they are judged against is 45 degrees: the functional specification's 25 degree
room plus a 20 degree enclosure rise, which is an acceptance limit on the enclosure, not a
measurement.

The boost is the tightest in the product by a wide margin, and only because the bound charges the
controller the whole stage's 20 percent efficiency floor, inductor loss included. Recorded as a
bound rather than as margin, with V8 owing a measurement of both it and the enclosure rise.

## [2026-08-01] verify | Close the current-limit latch and open-load fault cases

Read [[tps2553dbvr-1]]'s fault timing: the latch-off suffix holds a 5 to 10 ms overcurrent deglitch,
and section 9.5.1's formulas give 610, 667 and 734 mA at the board's 39 k ILIM resistor. Both
numbers matter in opposite directions.

A cold start into both bars' 202.9 uF would draw 1.45 A on the soft-start ramp alone, above the
limit, so the rail charges at the 610 mA floor and takes 1.66 ms. That is a third of the 5 ms
minimum deglitch, and the rail could carry 610 uF before a normal power-on latched itself off. A
real short is bounded the other way at 10 ms and 36.7 mJ, with the transient junction rise left to
V8 because the data sheet does not tabulate it.

The open-cable sweep, which reads the schematic for nets that appear only on connectors, found one:
LED_RETURN carries the first bar's data output to the second bar's input, and both bars stay powered
from the same limiter, so unplugging the first left a pixel input floating at 5 V. Hub R37 defines
it. An open load stays invisible to the limiter itself, which reports only overcurrent and reverse
voltage.

Fixing that turned up a separate latent defect. The reader's VMID pin was given two net names,
`NFC_VMID` at its stabilizer and `NFC_VMID_TAP` at the receive bias, so SKiDL merged them and picked
between the names by build order. The board's net name flipped between builds, and the layout
carried a net alias to paper over it, which made a fresh route fail to apply. The second name is
gone and the alias with it. The rerouted board passes at zero DRC violations, zero unconnected items
and zero parity issues, and mypy is clean on 87 source files.

## [2026-08-01] verify | Full gate after the three V3 segments

`make check` regenerated all four boards at zero DRC violations, zero unconnected items and zero
parity issues, mypy passed on 88 source files, and all 155 tests passed. The hub gained R36 and R37
and a fresh reviewed route; nothing else moved.

Two stale figures were corrected while passing through: the hub BOM is 14.090 EUR across 40 fitted
lines rather than 13.768 across 39, and the traceability manifest holds 83 requirements and 80
numeric criteria. Neither drift came from this work, but both were quoted next to numbers it
touched.

## [2026-08-01] verify | Corner the inductors and sequence the rails

Both inductor data sheets, [[nr6045s4r7mt]] and [[cdmc8d28np-1r2mc]], state their temperature range
to 125 degrees as including the coil's own rise and define rated RMS current as the current giving a
40 degree rise from 20 degrees ambient. That pair fixes one point on the heating curve, and the rise
scales with the square of the current, so hub L1 at 2.1 A rises 16.2 degrees and tolerates 108.8
degrees of ambient, and power L1 at 4.5 A rises 4.9 and tolerates 120.1. The same heating takes hub
L1's winding from 34 to 39.5 mOhm and the buck's dropout from 3.513 to 3.520 V, 7 mV of the 487 mV
the interface floor holds.

The converter itself stays uncornered. [[ap63203wu-7]] publishes its switch resistance as a typical
with no limits and no temperature coefficient, so a hot dropout cannot be closed from any filed
document. Recorded as open rather than filled in.

Sequencing reads five cross-rail signals off the hub schematic. Three land on pins their data sheets
rate against ground, minus 0.5 to 7 V for the [[sn74ahct1g125dbvr]] input and minus 0.3 to 7 V for
the [[tps2553dbvr-1]] enable and flag, so being driven before their own rail exists is a non-event.
A fourth shares a supply with its driver.

The fifth is a finding. [[ap22811aw5-7]]'s absolute maximum table lists VIN, VOUT and VEN and gives
its fault flag no row at all, while the enable it does list is rated against VIN. Running on battery
with USB unplugged holds that flag at 3.3 V with VIN at zero, which no filed document permits. R15
bounds the pin at 33 uA, under the leakages the same sheet specifies elsewhere and about 0.1 mW into
whatever clamp is inside. That bounds the condition without making it specified, so it stays a
vendor or V8 question rather than a closed result.

## [2026-08-01] plan | Record the firmware split and the V4 tooling blocker

Wrote `docs/software/architecture.md`. V5 requires gameplay and product state logic to be
independent of ESP32 register access, which is the same separation the first product principle
already asks for: deciding what a position means has to be separable from deciding what the hardware
just reported. So a pure `core/` with no ESP-IDF header, a `port/` that has them, and a small set of
interface headers the fakes implement on the host. C, because the target build has to be the exact
image V6 runs and V9 releases, and a rules engine that is not the shipped one is not evidence.

V4 is blocked on tooling rather than on design. openEMS is in neither the Fedora repositories nor
PyPI, so it needs a from-source build of CSXCAD and its Python bindings against system development
packages. scikit-rf is now installed and covers the Touchstone side once an extraction exists. The
workflow permits an equivalent solver, but the substitution has to be recorded with its reason and
no candidate has been shown to produce the same evidence.

## [2026-08-01] verify | FastHenry extraction finds a broken RF return

Chose FastHenry over openEMS for V4 and recorded the substitution. At 13.56 MHz the wavelength is
22 m against a 162 mm board, about 0.007 of a wavelength, so nothing is electrically large and the
question is magnetoquasistatic rather than radiating. Built FastHenry 3.0.1 from the FastFieldSolvers
source, which needs `-std=gnu89 -fcommon` under a current GCC, and validated it against the Grover
model already used for the matrix loop: 572.6 nH against 584.9 and 0.436 against 0.473 ohm, agreeing
to 2 and 8 percent. A solver that reproduces evidence the project already trusts can be trusted for
the extraction the analytical model cannot do.

The first extraction refused to run, which was the result. The recorded reserve is x 122 to 156, but
the routed RF run spans x 121.32 to 158.63, so it leaves the reserve at both ends and FastHenry
found the source point outside the plane. Measuring from the routed copper then showed MOSI on the
back layer at x 121.3535, **0.034 mm** from the RF trace, straight through its return. The return
current sits within about three dielectric thicknesses, 2.8 mm on this 1.0 mm two-layer board, so
that copper is inside the corridor the reserve exists to protect.

Widening the reserve to x 118 to 161 was tried and the two-layer route stopped converging: three
reroutes left 2, 7 and 3 unconnected items where the current reserve reliably reaches zero. The
board is left on its committed clean route with the defect recorded rather than half fixed. The
regression test carries a strict xfail so it turns red the moment the layout is corrected.

## [2026-08-01] verify | The RF return defect is placement, not routing

Removed the xfail that had been masking the failed corridor check. The project's own workflow calls a
manually waived critical check a failure, and the marker was exactly that, so the test now fails
until the board is right.

Chasing the fix found the real cause. RF_BUS has to reach the match output near x 141 to 143, the
connector at 150.5, and the receive tap C37 at 121.8, 33.8. C37 sits by the reader on purpose, to
keep the high-impedance receive traces short, so the bus is obliged to cross a third of the board.
Protecting the return corridor of a bus that long is what fights the back copper everything else
needs. A wide keepout stopped the two-layer route converging; a targeted one fixed the entry, from
0.034 to 21 mm, and left the far end open past x 156. Scored reroutes then gave 0.56, 4.69 and
3.43 mm against a 2.79 mm requirement with 0, 4 and 8 DRC violations. A constraint met on some
random seeds and not others is not a constraint.

Cloud and third-party routers do not address that. DeepPCB's free tier caps at 150 airwires against
this board's 254. TopoR Lite is free under 650 pins and reads DSN and writes SES, but is Windows
only with no batch mode, which would put a manual GUI step in a path CLAUDE.md requires to be code,
and its session would not import anyway because `ses_import.py` hardcodes Freerouting's resolution
and via padstack naming.

Three ways out, none chosen: move C37, R29 and R30 to the connector end and accept longer receive
traces; go to four layers on the hub; or extract the slotted return and show the coupling is
tolerable, which needs the FastHenry slot model to converge and it does not yet.

## [2026-08-01] correction | The RF return defect was an artifact of my own check

Retracting the two entries above it. The check that found it filtered RF_BUS to the front layer and
then measured its distance to back-layer tracks, so it compared traces on opposite layers. Two
traces crossing in plan view on different layers read as nearly zero apart, which is ordinary and
harmless; real same-layer clearance is DRC's job and passes at 0.2 mm. The 0.034 mm MOSI figure, the
placement root cause built on it, the keepout experiments and the router comparison all descend from
that number, and none of them stand.

The extraction was also of the wrong net. RF_BUS is routed on both layers, eleven segments on F.Cu
and two on B.Cu including an 18.35 mm run at x 121.49 with two vias. The layer filter dropped those,
so the 46.9 nH reported earlier was the inductance of a path that does not exist.

What survives: FastHenry is built, installed and validated against the Grover model at 2 percent on
inductance and 8 on resistance. The tool is good. What it was pointed at was not.

`deck()` now raises rather than modelling a net that runs on its own return plane, and a test pins
that refusal. The lesson worth keeping is that the check produced a result surprising enough to
justify a board respin, and that should have been the cue to validate the check before acting on it,
not after.

## [2026-08-01] ingest | Piece tag candidate bound: ICODE SLIX2 in a 21 mm Circus inlay

V1's open tag item had no MPN anywhere in the repo, and it is the first definition-of-done bullet
of V4. Closed the technical half of it.

Protocol first, because it is the decision that constrains everything else. ISO/IEC 15693 over
14443-A: a vicinity card operates at roughly a tenth the field strength of a proximity card, and
the matrix couples an 18 mm tag coil to a 280 mm line antenna, which is weak coupling by
construction. [[bitwiseid-method]] also runs on unaddressed READ MULTIPLE BLOCKS and INVENTORY
READ, which are 15693 commands with no 14443-A equivalent, so picking 14443-A would throw away the
one technique that de-risks the scan loop. [[pn5180a0hn-c3e]] is already bound and is NXP's
strongest 15693 reader. This resolves the open question flagged in [[bitwiseid-method]]'s
"Relation to our design" section, on architecture grounds rather than bench evidence.

Part: [[ad-circus-slix2]], Avery Dennison's 21 mm round inlay carrying [[sl2s2602]] (ICODE SLIX2).
Product code 3006370 / IL-603074. It is the smallest round HF inlay Avery Dennison publishes,
which is why it fits the 22 mm recess at all; the common 25 mm tag does not. Two datasheets filed
and ingested: `SL2S2602_NXP.pdf` and `AD-CIRCUS-SLIX2_AVERYDENNISON.pdf`.

The number V4 actually needed: input capacitance 23.5 pF typical, 22.3 to 24.7 pF over the
published spread, plus 40 uW minimum input power. Antenna diameter is 18 mm, not the 21 mm
die-cut, and modelling the die-cut would overstate the coupling area by 36 percent.

Two gaps recorded rather than papered over. Avery Dennison publishes no coil inductance, turn
count or resonant frequency, so the tag resonator has to be back-solved against the 23.5 pF or
measured at V8; that is a derived value and is marked as one. And the SL2S2602 datasheet gives no
equivalent parallel resistance at minimum operating power, so loaded Q cannot come from the
datasheet either. V4 can proceed with a bounded model, but not a fully datasheet-sourced one.

Still open on V1: nothing is purchased, so there is no dated availability record, and no second
source is identified. Avery Dennison disclaims continued availability in its own terms.

## [2026-08-01] correction | The retraction contained its own stale-state error

The entry above withdrew the RF return defect for a sound reason, that comparing front-layer traces
to back-layer traces by plan-view distance is meaningless. It then added a new claim that was itself
wrong: that RF_BUS runs 18.35 mm on the back layer with two vias. That was measured from a board
left on disk by the keepout experiments, not from a regenerated one. On the committed route RF_BUS
is entirely on the front layer with no vias.

The same mistake in a new place: reading the generated board without checking which run produced it.
Board state has been a moving target all session because every reroute overwrites it, and nothing in
the checks noticed. The test that pinned this now builds its own synthetic segment instead of
asserting whatever the last reroute happened to leave behind, so it cannot be fooled that way again.

What stands: the layer filter was a real latent bug and is fixed, `deck()` refuses a net on its own
return plane, and FastHenry remains validated. The 46.9 nH figure is unverified rather than refuted.

## [2026-08-01] finding | The 22 mm tag recess is larger than a pawn base at this grid pitch

Follow-on from the tag ingest above, prompted by asking whether the inlay actually fits a piece.
It fits the recess. The recess does not fit a conventional pawn, and that conflict was already in
the functional spec before any tag was chosen.

Conventional proportions put the king base at 0.73 to 0.78 of the square and the pawn base at
about 0.586 of it. On the 35 mm grid that is a 25.6 to 27.3 mm king base and a 20.5 mm pawn base.
The [[ad-circus-slix2]] die-cut is 21 mm and the specified recess is 22 mm, so both exceed the
pawn base, and pawns are half the set.

Nothing is invalidated: `hardware/cad/` contains no piece geometry, so the pieces are undesigned
and this is a design input rather than a respin. Recorded in `docs/hardware/matrix.md` with four
options for V7. The interesting one is trimming the die-cut: only the inner 18 mm is coil, the
outer 1.5 mm is PET carrier, so a punch to about 19 mm clears a standard pawn without touching the
antenna. Untested and it voids the vendor article, so it is a candidate, not a plan.

Rejected outright: a smaller tag for pawns only. [[bitwiseid-method]] requires uniform tag timing
across the set, and mixed coil diameters also mean mixed coupling per square.

Method note, given the retraction logged above: this one is arithmetic on published proportions
plus a datasheet dimension, and the pawn figure was cross-checked two ways (0.586 x square, and
0.765 x king base) landing at 20.5 and 20.1 mm. It has not been checked against a physical set.

## [2026-08-01] decision | Pawn bases grow to 24 mm rather than the tag shrinking

Resolving the conflict logged above. The owner's instruction was to enlarge the pawn base unless a
smaller tag existed for the whole set at a comparable price. Surveyed the small end of the ISO
15693 catalog; none qualifies.

- AD Miniblock SLIX2, 18 x 18 mm die-cut on a 14.5 mm coil. Square, so its 25.5 mm diagonal is
  what a round recess has to clear. Worse than the 21 mm round [[ad-circus-slix2]], not better.
- AD Minitrack SLIX2, 14 x 31 mm. The 31 mm dimension fits no base on this board.
- HID laundry tag SLIX2, 16 mm. Physically fits, but EUR 1.64 against EUR 0.34 to 0.69, and it is
  a sealed puck rather than a 141 um inlay.
- SLIX2 on-metal micro, 6 mm, EUR 2.50. Anti-metal behavior is explicitly prohibited by
  `docs/functional/physical.md`.

The RF argument points the same way independently. Coupling scales with coil area, an 18 mm coil
against a 276 mm line antenna is already weak by construction, and every smaller candidate roughly
halves it or worse. Spending piece silhouette to buy coupling margin is the right trade in a
system whose margin has not been measured yet.

So `docs/functional/physical.md` now requires a 24 mm minimum base on every piece, pawns included:
1 mm of wall around the 22 mm recess, 1.5 mm around the bound tag. Added PHY-PIECE-004 and the
PHY-PIECE-BASE-DIAMETER criterion, and re-pinned the physical.md source hash, which is the review
gate that change is supposed to trip. Recorded honestly in the spec that this makes pawn bases
nearly as wide as the king's and the set less classically proportioned.

## [2026-08-01] synthesis | The display product page publishes the sleep current as the maximum

V1's oldest open display item was a contradiction between two manufacturer documents: section 4.3
of the [[er-oledm3-12-1w]] datasheet says 320 mA active and 2 mA sleep, the BuyDisplay product
page says 2 mA maximum. Resolved in favour of 320 mA, which is what the load budget already
assumed. Filed as [[er-oledm3-12-1w-display-current]].

Two independent arguments. First, 2 mA at 3.3 V is 6.6 mW for the whole module, which has to run
the SSD1362, an onboard boost to the panel's high-voltage rail, and 16384 lit pixels; a boost
converter's quiescent draw alone is in that range. Second, and this is the useful part, a
comparable 3.12 inch 256 by 64 PMOLED from a different manufacturer publishes the current table
the product page garbles. [[w256064-xalg-datasheet]] gives 32 mA typical at VCC 14.5 V on a 50
percent checkerboard, which is 464 mW, roughly 928 mW at full fill, which through a 3.3 V boost at
85 to 90 percent is 312 to 331 mA. The datasheet says 320 mA. Filed that panel's PDF in
`Datasheets/` as corroborating evidence, clearly marked not-fitted.

Recorded as Derived, not Datasheet. The bound part's own datasheet always said 320 mA; what is new
is the demonstration that the contradicting product page is the wrong one. No human at the
supplier has confirmed it.

Two things this does not fix, and one I should have caught earlier. The original PDF is still not
filed: `buydisplay.com/download/manual/` returns 403 to automated clients even with ordinary
browser headers and a referer. Search engines index the path so it is public, just bot-blocked,
and a human opening it in a browser fixes it in a minute. I did not try to work around the block.

The one I should have caught: the filed datasheet is revision **1.0, preliminary, 2025-08-07**.
V1's definition of done makes a provisional document a release blocker by itself, independent of
any number in it. That has been sitting in the evidence capture since 2026-07-29 without being
recorded as a blocker. It is recorded now.

## [2026-08-01] doc | The display interconnect turns out to be fully specified, except for one fork

Wrote `docs/hardware/display-interface.md`, the contract between the hub's J5/J6 and each
[[er-oledm3-12-1w]] module's 16-pin header. The map was already recoverable from the immutable
evidence capture and nobody had assembled it in one place.

In four-wire SPI mode only six of the sixteen module pins carry anything: VCC, RES, CS, D/C, SCLK
and SID. The other ten are ground. Six signals plus ground is seven conductors, which is exactly
why the hub connector is a 7-pin GH, so the pin counts were never in conflict. But the cable is
not straight-through: eight module pins have no hub conductor at all and must be grounded at the
display end.

That is the fork. Either a small adapter PCB at each display with the grounds poured, which is
reproducible and DRC-checkable and matches this project's rule that layout is code, or a
hand-assembled 16-way loom with the ground pins daisy-chained inside it, which is cheaper and adds
no board. It changes the board inventory, so it is recorded as an open decision rather than
settled here.

Still blocked on the same two things as everything else about this display: the original PDF is
403-blocked so the pin map rests on a text capture, and the datasheet is a preliminary revision.

## [2026-08-01] ingest | The display datasheet arrives and settles three things, opens a fourth

The owner downloaded the PDF the supplier's server refuses to serve to scripts. Filed as
`Datasheets/ER-OLEDM3.12-1W_BUYDISPLAY.pdf`, 21 pages, revision 1.0 preliminary, Aug-07-2025. It
sits alongside the text capture rather than replacing it; both are immutable.

Confirmed, section 4.3: IDD maximum **320 mA** with note 5 reading "VDD=3.3V, 100% Display Area
Turn on", and IDD sleep maximum 2 mA. The [[er-oledm3-12-1w-display-current]] analysis was right
and the product page is wrong. Also worth noting the module has one supply pin: VCC on pin 1 with
a 3.6 V absolute maximum, so the panel's high-voltage rail is generated on-module and 320 mA is
the whole module at 3.3 V, which is what the corroboration assumed.

Confirmed, section 4.1: the pin map matches the text capture exactly. Pins 7 (R/W) and 8 (E/RD)
**must** be tied to VSS in serial mode; pins 11 to 16 (D2 to D7) are unused and only *recommended*
low. That mandatory-versus-recommended distinction was not in the capture.

New, from the outline drawing: the header is a **2 x 8 on 2.54 mm pitch**, not a single row. Odd
pins one row, even the other, pin 1 square, 17.78 x 2.54 mm field. That is a stock IDC-16 pattern,
so the mating part is off the shelf. Reading it took rendering the vector page at 600 dpi and
cropping, because the pitch could not be told from the page image and guessing between 2.0 mm
single-row and 2.54 mm dual-row would have produced a footprint that does not mate.

The fourth thing, which is now the real blocker: **the datasheet never says how the interface is
selected.** Every pin description is conditioned on "when serial interface mode is selected" and
no section explains the selection. The back view shows why: R3/R9, R5/R8 and R10/R11/R12 are
paired 0-ohm jumper positions. Which combination gives four-wire SPI, and which the module ships
with, needs EastRising's separate interfacing document. An adapter board cannot fix a module
strapped for parallel.

Decision recorded in `docs/hardware/display-interface.md`: a small adapter board that plugs onto
the display header, snapped off the existing light-bar panel so it costs no new fabrication line
item. Merging it into the light bar was checked and is physically impossible; the bar is 8.5 mm
tall with 2.15 mm of free length and everything on the front face behind a diffuser. Widening the
hub to 2 x 8 and using a stock ribbon was the attractive alternative and lost on the cost of
re-routing a hub that already struggled to converge on two layers.

## [2026-08-01] design | Display adapter specified, blocked on a connector nobody has bound

Owner confirmed the adapter should ride the existing light-bar panel rather than becoming its own
fabrication order, which is what `hardware/pcb/panel.py` was built for. Specified in
`docs/hardware/display-interface.md` and added to `boards.md` as board 5, two off.

The interesting part was orientation. Six signals between a 7-pin GH and a 2 x 8 header do not
route without crossings unless the two connectors are aimed correctly. With J1's pin 1 at the
right-hand end and J2's pin 1 at the left, five of the six fall into monotonically increasing
order (SCLK, MOSI, CS, DC, RESET) and cannot cross; all five go on the front. 3V3 is the exception
by construction, sitting at one end of the GH and the far end of the display header, so it takes
the back layer alone and runs out past the right end of the pin field. Ground pours on both layers
and reaches all ten grounded pins through their own through-hole barrels, so the board needs no
vias at all.

The far-row nets pass through the 1.27 mm gap beside a near-row pad. 1.7 mm pads on 2.54 mm pitch
against a 0.25 mm track leaves 0.295 mm, over the 0.2 mm rule. Checked rather than assumed,
because it is the one dimension in this design that could have failed.

Not generated, and deliberately so: the 2 x 8 socket has no bound MPN. Searching turned up
candidates but nothing with a datasheet I would put in `Datasheets/`, and binding a connector off
an ambiguous catalog hit is the exact failure mode the Datasheets rule exists to prevent. The
schematic generator refuses any fitted part without a manufacturer number, which is correct, so
the board stays on paper until the socket is bound properly.

## [2026-08-01] retraction | The display adapter board was over-built and is withdrawn

Owner asked why the module's own PCB cannot do the job. It can. Retracting the adapter as the
design; it stays in `docs/hardware/display-interface.md` as a fallback only, and is removed from
`boards.md`.

The adapter's entire job was shorting eight pins to ground. Laid out on the 2 x 8, those pins are
not scattered: columns 6, 7 and 8 are ground on both rows (pins 11 to 16, a solid two-by-three
block at one end), column 4 is ground on both rows (pins 7 and 8), and then pins 2 and 3. That is
one solder bridge across six adjacent pins, one across two, and a link wire, on the solder side of
the module's own header where it does not obstruct mating. Twice, for two displays. I had been
treating commoning ten adjacent pins as a routing problem when it is a soldering-iron problem.

Also correcting myself: I earlier dismissed hand strapping as failing intermittently rather than
obviously. That criticism was about a crimped daisy chain inside a flexing loom. A solder bridge
across adjacent pins on a rigid PCB is not that failure mode.

The more important point, which the adapter was obscuring: it is not established that any strapping
is needed. The module's interface-select jumpers (R3/R9, R5/R8, R10/R11/R12) plausibly already
drive R/W and E/RD low when four-wire SPI is selected, and pins 11 to 16 are only recommended low,
not required. Four outcomes, from no work at all to the fallback board, and all four are decided by
the same EastRising interfacing document that decides mode selection. Fabricating anything before
reading it risks building a board to solve a problem the module already solved.

## [2026-08-01] synthesis | The cell was never blocked on searching, it was blocked on a spec

Wrote `docs/hardware/cell-assembly.md`. The V1 entry had been reading as "no protected pack found",
but [[battery-format-and-module-alternatives]] found a good one on 2026-07-30. What was missing was
the acceptance specification a candidate has to be judged against, so the Keeppower pack had
nowhere to pass or fail.

Every bound in it is derived from criteria already recorded, not newly chosen:

- Over-discharge detection at or below 2.8 V, because the TLV809K33 supervisor cuts the boost at
  2.87 V. A pack tripping above that governs the discharge with an undocumented threshold and the
  ten-hour runtime claim stops meaning anything.
- Overcharge detection at or above 4.25 V, because the BQ25895 terminates at 4.2 V and its
  regulation tolerance puts the real top near 4.221 V. A 4.2 V trip nuisance-trips every charge.
- Overcurrent detection at or above 6.6 A, because worst case discharge is 5.871 A and the
  TPS61088's guaranteed limit is 6.502 A. The converter must clamp before the pack disconnects,
  or a stress condition becomes a dead board.
- Leads 20 AWG or heavier for 5.871 A peak. Many packs ship 22 AWG, and this is the likeliest
  acceptance failure.

Two things fall out that are true of every candidate, not just this one. No protected pack includes
a thermistor, and `functional/power.md` requires charging gated on one attached to the cell, so
bonding the audited NTCLE317E4103SBA is this project's work regardless; a sensor taped near a cell
measures air. And the keyed connector is a re-termination in every case, so the lead-gauge question
is about the wire that stays, not the plug that goes.

One thing worth flagging that I had not noticed before: `POWER-CHARGE-TEMPERATURE-MIN` and `-MAX`
still cite `PISUGAR3_PLUS_safety.md`, the safety document of a module that is no longer bound. The
0 and 40 degree charge window is borrowed from an unrelated product. Both criteria say so honestly
in their margin fields, but it means binding a cell is a V0 evidence improvement as well as a V1
one.

Still not bound, and the remaining gap is a supplier request rather than more searching: the cell's
own datasheet and revision, the protection IC behind "Seiko protection PCB" (that family spans
several parts with different thresholds), the shipped construction against the 80 x 26 x 23 mm
reserved envelope, and the shipped connector.

## [2026-08-01] doc | Harness inventory, and the highest-current path rests on an assumption

Wrote `docs/hardware/harnesses.md`, the last of the three V1 items that were sitting as prose
fragments in `planning.md` rather than as anything checkable. Every cable, its connector, its
contact allocation and its worst-case per-contact current in one table.

The finding: **the cell link puts 5.871 A through a single Micro-Fit 3.0 contact pair, and no filed
source says what that contact is rated for.** [[micro-fit-3-0-mating-evidence]] binds mating
compatibility, the 18 AWG wire range and the 1.85 mm insulation limit, and states in its own last
line that it qualifies nothing else. No current rating, no derating curve. Two circuits both at
5.871 A is the worst arrangement a two-circuit housing has, and this is the highest-current path in
the product.

Also retired a problem I thought I had found. J2's three JST GH supply contacts looked like 3.0 A
across a 1 A-per-contact connector, which would be at the rating with zero margin. It is not:
`functional/power.md` caps the source at a compliant 5 V 2 A USB supply, so it is 0.67 A per contact
with the return over four grounds. The "3.0 A capability" in the module interface is the
connector's capability, not the load. Worth recording as a non-problem so nobody re-derives it.

Cell-lead drop also checked and negligible: 18 AWG, roughly 21 milliohm per metre, 0.25 m round
trip, about 30 mV at 5.871 A, which does not encroach on the 2.87 V boost floor.

Still open on every harness and now listed explicitly: wire type and insulation diameter (the
terminal caps insulation at 1.85 mm, which rules out plenty of ordinary 18 AWG), crimp process
(Molex names hand tool 63828-0200, otherwise pre-crimped leads must be bound as parts), colour
coding, length and strain relief, and the assembled article itself. Lengths depend on the rail
arrangement, which is still undrawn.

## [2026-08-01] ingest | Chasing the Micro-Fit rating made the cell harness look worse, not better

Went after the number flagged in the harness inventory: what a Micro-Fit 3.0 contact is actually
rated for, given the cell link runs 5.871 A peak through one pair. Filed
[[micro-fit-current-rating]]. It does not close the gap and it moved the design from "unqualified"
to "possibly over rating", which is worth stating plainly.

Molex PS-43045 revision M1, dated 2007, section 4.2: 20 AWG at 5 A, 22 at 5, 24 at 4, 26 at 3, 28
at 2, 30 at 1. **The table stops at 20 AWG.** The 43030-0006 terminal drawing bundled with it says
5.0 A maximum. Neither covers [[430300038]], the fitted 18 AWG variant, which distributors list at
8.5 A. That is a catalog figure and this project does not bind electrical limits from listings.

So the cell harness sits between 31 percent margin at 8.5 A and 17 percent over rating at 5.0 A,
and nothing available here decides which. Recorded on the entity page and in
`docs/hardware/harnesses.md` rather than resolved.

Two caveats on the filing itself, both recorded on the page. It is an Octopart mirror, not a file
from Molex: `molex.com` and `tools.molex.com` both failed to respond over several attempts with
different clients and protocols, so this is a stopgap that the manufacturer's own file must
replace. And revision M1 is old; later revisions are known to carry an 18 AWG row and a derating
table indexed by circuit count and wire-to-wire versus wire-to-board, which is exactly what a
two-circuit housing with both circuits energized needs.

Also updated [[micro-fit-3-0-mating-evidence]], which had honestly said it qualified nothing beyond
mating and wire range, to point at where the current question now lives.

## [2026-08-01] decision | Cell link binds the documented 20 AWG row, and I had the comparison wrong

Owner's call: take the 20 AWG at 5.0 A row that PS-43045 actually documents rather than wait on the
8.5 A that distributors attach to the 18 AWG terminal. Applied across the docs.

**Correction first, because it changes the conclusion.** The previous entry said the cell harness
was 17 percent over rating at 5 A. That compared 5.871 A against a thermal limit, which is wrong. A
connector rating is a 30 degree temperature-rise figure and contact heating is I squared R, so the
governing quantity is RMS. The battery path is 4.442 A RMS against 5.0 A, about 11 percent margin.
The 5.871 A is a 500 kHz boost inductor peak and does not heat a contact. The harness is inside its
rating, not over it.

The binding: wire becomes exactly 20 AWG, and the terminal moves from [[430300038]] (18 AWG, which
appears nowhere in the filed revision) to 43030-0007, the 20 to 24 AWG tin female part in bag
packaging, read off the 43030 table in the same document. Board-side 43045 headers are untouched,
so this is cable-side only with no layout consequence. Propagated to `harnesses.md`,
`cell-assembly.md`, `boards.md`, `power.md`, `power-subsystem.md` and `planning.md`.

Two reservations recorded rather than smoothed over. Eleven percent is before derating, and the
table for a two-circuit housing with both circuits energized is absent from this revision; at 90
percent the margin becomes roughly one percent, which is not a margin. And the cell link is the
only power interface in the product that puts its whole current through a single contact pair,
which is contrary to the principle `power-module-interface.md` already states, that power and
ground use multiple contacts so no single terminal carries the whole interface current. J2 gives
5 V three contacts, J3 gives its output two. Four circuits on the cell link would put 2.22 A on
each contact and end the question, at the cost of a power-board re-route, so it is written up as a
recommendation and not done.

## [2026-08-01] correction | Back to 18 AWG, and the multiple-contact rule does not apply to a cell

Reversing the previous entry on the owner's call, and conceding a second point I got wrong.

**18 AWG stays.** The cell link keeps [[430300038]] on a single contact pair, and the 8.5 A that
distributors publish for that terminal is accepted as catalog evidence pending a current Molex
revision. This is recorded as an evidence-class gap, not a blocker, because the harness passes
under either candidate figure: 4.442 A RMS is 48 percent inside 8.5 A and still 11 percent inside
5.0 A. The rating question was never pass-or-fail, only how much room, and I should have said so
before turning it into a decision. 18 AWG is also the better wire at 21 milliohm per metre against
20 AWG's 33.

**The multiple-contact rule does not apply here, and citing it was a mistake.** A single positive
and a single negative is the normal way to connect a cell, not a compromise; essentially every
battery interconnect in general use is a single pair carrying far more than 4.4 A. The wording in
`power-module-interface.md` is about the board-to-board links J2 and J3, where the connector
already has pins to spare and paralleling costs nothing. Applying it to a two-wire battery link
was reading a local convenience as a general law. Paralleling is also weaker than it sounds:
contacts do not share current evenly because their resistances differ, so two are worth appreciably
less than twice one, and the right answer for a battery link short of capacity is a bigger
connector rather than more pins of a small one. The four-circuit proposal is withdrawn and the
power board is untouched.

One thing worth keeping from the detour: the terminal caps insulation outside diameter at 1.85 mm,
and plenty of ordinary 18 AWG is jacketed thicker than that. That is now an explicit acceptance
item on the cell leads rather than an assumption.

## [2026-08-01] decision | Stop waiting on suppliers, register the assumptions instead

Owner's call: make suppositions and keep moving rather than block on correspondence. Wrote
`docs/hardware/assumptions.md`, a register of nine values the design uses that no filed datasheet
backs, each with its basis, its consequence if wrong, and the point where it gets measured.

The point of the register is that these stay visible. `simulation-workflow.md` treats an assumed
critical value as a V1 failure, so every row is a waiver against the V8 and V9 order gates. That
constrains releasing a fabrication order and nothing else; schematic, layout, simulation and
firmware work all proceed normally. V1's plan entry now says "closed for design purposes on the
registered assumptions" and stays unticked, because ticking it would corrupt the gate the whole
project is tracked against.

Six of the nine are low consequence or conservative in the safe direction: the Micro-Fit 8.5 A
rating (which passes at either candidate figure), the redundant-if-wrong display ground bridge, the
preliminary datasheet numbers, the pack re-termination, the borrowed charge window, and the tag
geometry follow-ons.

Three matter and are named as such. The Keeppower pack's protection thresholds are the highest
consequence, because wrong thresholds are a safety and behaviour problem rather than a margin
problem, and the pack is now selected on that assumption rather than left as a candidate. The
display interface mode decides whether the displays work at all, though it fails loudly at first
bring-up, which is the best kind of wrong. And the tag resonator assumptions are what keep V4 from
being a fully datasheet-sourced electromagnetic model.

## [2026-08-01] finding | SEL_SRCLR_N is a dead net, and the matrix cannot be blanked

Found while writing the expander driver, which is the right time to find it: the pin map header I
generate exposes every driven expander bit, and a driver author would reasonably reach for
`SEL_SRCLR_N` to clear the selection before a scan.

It reaches nothing. From the generated hub netlist, not the source:

    SEL_SRCLR_N: (('R31', '2'), ('U6', '16'))
    SEL_RCLK:    (('J4', '7'), ('R26', '1'), ('U6', '4'))

Expander P1.3 to pullup R31 and stop. J4 carries seven conductors and none of them is this one, and
`matrix.py` never mentions it: both 74HC595 `SRCLR_N` pins are tied hard to 3V3, both `OE_N` pins
to ground. Verified from the matrix netlist too, where U1 and U2 pins 10 and 16 sit on 3V3 and pins
8 and 13 on GND.

So the selection outputs are permanently enabled and cannot be blanked by any signal. Two
consequences. The sixteen lines are live with undefined content from power-up until firmware shifts
and latches, which is an unmanaged current and a meaningless RF state, though at roughly 160 mA
across sixteen cells it is not damaging. And shifting a known pattern becomes the matrix driver's
mandatory first action rather than good practice, because nothing else can put the board in a known
state.

Not worth fixing in copper: J4 is a full 7-pin part, so carrying the signal means an 8-pin
connector at both ends and a re-route of two boards, all to replace what a 16-bit shift already
does. The trap was worth fixing, and `hardware/pcb/firmware_pins.py` now excludes the net from the
generated header with the reason inline, so no driver can call for a clear that would appear to
succeed and do nothing. Documented in `docs/hardware/matrix.md`.

Checked twice against generated netlists before writing any of this down, because the last time a
check surprised me this much the check was wrong.

## [2026-08-01] correction | Single-slot inventory cannot read a chess position

Correcting my own framing from earlier today. The PN5180 driver's single-slot ISO 15693 inventory
was described as "enough for a first bring-up". It is enough to prove the RF path end to end, and
it is not enough to read the board, which is a bigger difference than that wording admitted.

Single slot means every tag in the field answers in the same window, so a line carrying more than
one tag produces a collision and no UID. The row-and-column architecture guarantees several tags
per line: sixteen antennas cover sixty-four squares, so each line is shared by eight of them. A
chess starting position puts eight pieces on rank 1, so row 0 collides on every scan. The board as
it stands can read a sparse position and cannot read a game.

This is not a surprise to the design, it is the exact problem [[bitwiseid-method]] was researched
to solve, and [[row-column-antenna-matrix-technique]] already records that every line scan returns
multiple tags. What was wrong was calling the gap a later refinement rather than the next
requirement.

The mechanism is confirmed rather than guessed, which is the useful part. Sixteen-slot inventory
uses flags 0x06 instead of 0x26, and advancing a slot needs an EOF with no data. PN5180 datasheet
Table 98 gives TX_CONFIG bit 10 as TX_DATA_ENABLE: "If set to 1; transmission of data is enabled
otherwise only symbols are transmitted." Clearing it and transmitting emits the frame symbols
alone, which is the EOF. So the next increment is bounded and does not need a supplier.

Recorded in `docs/software/architecture.md` under what is real and what is not.

## [2026-08-01] finding | `make pcb-fab` was building an incomplete order set

Went looking at fabrication readiness because the owner wants to order boards. The aggregate target
`pcb-fab` depended on `pcb-lightbar-fab pcb-matrix-fab pcb-hub-fab` and not `pcb-power-fab`, so the
one command whose whole job is "produce the order artifacts" quietly produced three boards out of
four. The power board's own target existed and worked; nothing tied it in. Fixed.

That is the kind of defect that does not fail anything: every individual target passes, DRC passes,
tests pass, and the omission only shows up as a missing folder at the moment somebody uploads an
order.

Also extracted the DFM-relevant geometry from the routed boards rather than trusting the design
rules. All four are two layers, 1.0 mm, with 0.200 mm minimum copper track, which is comfortable.
The matrix is the exception on holes: **0.2 mm via drills into 0.4 mm pads**, against 0.3/0.6 on
the other three. That is tight enough to risk falling outside a fabricator's standard tier, and it
is the 300 by 300 mm board, so it is the worst one to discover a price tier on. Recorded in
`docs/planning.md` under V7 rather than assumed benign.

Earlier numbers I nearly reported were wrong and worth noting as a method warning: a first pass
matched every `(width ...)` in the board file and returned 0.05 mm and 0.00 mm minimum tracks,
which are silkscreen and graphic widths, not copper. Filtering to `(segment ...)` gave the real
0.200 mm. Extracting from a board file is not the same as extracting the right thing from it.

## [2026-08-01] release | Scoped test article: the bare matrix board

The owner wants boards in production. The honest position is that final boards need V0 through V9
and V4 has never been run on an RF board, so that cannot happen. What can happen, and what the
workflow explicitly prefers, is a scoped article: V8 names "copper antenna samples" ahead of a
complete assembled set. Written up as `docs/hardware/test-article-matrix.md` and buildable with
`make test-article-matrix`.

The argument for ordering it now rather than after more simulation is [[ad-circus-slix2]] and
[[sl2s2602]]. Assumptions A8 and A9 exist because Avery Dennison publishes no coil inductance for
any converted inlay and NXP publishes no equivalent parallel resistance at minimum operating power.
The tag resonator is back-solved. More simulation cannot fix that; a VNA can. Waiting for a
datasheet-sourced V4 before ordering the article that would source it is waiting for something that
cannot arrive.

Bare copper is also releasable in a way a populated board is not: it carries none of the electrical
risk V3 covers and none of the assembly risk V7's BOM and CPL bullets cover. And the matrix is
hand-populated regardless, because its outline is outside the assembly service, so ordering it bare
costs nothing in process.

Three things the project cannot answer from its own files and which must be settled at upload: the
0.2 mm via drills against the fabricator's standard tier, copper weight and surface finish which
the board file leaves to KiCad defaults and therefore does not specify at all, and quantity against
900 cm2 of area on the most expensive board in the product.

## [2026-08-01] extraction | The sixteen antennas, and what the mesh study caught

First real V4 work on the matrix. `hardware/sim/antenna_coupling.py` solves all sixteen line
antennas together in FastHenry at 13.56 MHz and returns the full port-to-port matrix. Geometry
comes from `matrix_geometry.py`, the same constants the footprint generator and layout use, so the
model cannot drift from the board.

Self inductance is 566.5 nH against 590 nH from Grover's formula in `loop.py`. Two independent
methods on one shape agreeing to 4 percent, which is the first time this copper has been solved
rather than estimated. All sixteen lines agree to 0.05 percent on inductance, so they are
interchangeable, which matters because a scan treats them identically.

Two findings the project did not have before. **Rows and columns are decoupled but not uniformly.**
[[row-column-antenna-matrix-technique]] and `matrix.md` assert decoupling; the figure is k = 0.0066
at the board centre and k = 0.0665 at the four corners, a tenfold variation, because the orthogonal
cancellation is weakest where two loops cross near their open ends. And **adjacent parallel lines
are the dominant coupling at k = 0.1398**, falling to 0.017 two lanes away and 0.001 across the
board. That is the physical path by which a tag could answer on the wrong line, which is the
RF_CROSSTALK mechanism the firmware's `scan_join` reports.

The mesh study is what makes those evidence rather than a first solve, and it earned its keep by
catching two things.

**Resistance never converged.** It climbed 525 to 563 milliohm across nhinc 1 to 7 and nwinc 9 to
13 and was still rising. The cause is physical: skin depth in copper at 13.56 MHz is 17.8 um
against a 1 mm wide, 35 um thick conductor, so resolving the current crowding needs far more
filaments than the coupling does. Resistance from this extraction is a lower bound and loaded Q,
being omega L over R, cannot be stated at all. Recorded as a gap with its own test rather than
quietly reported as a number.

**My reciprocity check measured nothing.** It normalised each mutual term against itself, so
near-zero couplings between distant lines produced a 47 percent error that did not move with
refinement. Against the self-inductance scale the residual is 0.15 percent and constant, which is
the solver's floor. A metric that does not improve with mesh refinement is usually the metric's
fault, not the solver's.

Still not V4: this is inductive coupling between antennas, not tag coupling, which A8 and A9 record
as unobtainable from any datasheet, and not capacitance, Q, or radiated emission. The bare matrix
test article exists to measure what this cannot.

## 2026-08-02 Query: can the sensing plane be one PCB per line antenna?

Filed [[split-sensing-plane]]. Updated [[row-column-antenna-matrix-technique]] to record that the
technique now has two validated board partitions behind it rather than one.

The question came in as a cost and convenience question and turned out to be an impedance question.
A connector between a loop and its tuning capacitor joins sixteen resonators and cannot be
compensated, which is why the earlier antenna-board-plus-daughterboard split was rejected. A
connector on the bus side of the cell's 100 nF DC block feeds a parallel-resonant branch through
series inductance, and 142 to 385 nH of it moves the bus by 0.46 percent. Same copper, same parts,
different boundary, completely different answer.

Two findings worth carrying to other partitioning questions:

**Equal beats short.** Sixteen equal-length harnesses detune sixteen lines together, which one
capacitor value absorbs. Mixed lengths would spread them, which nothing absorbs, because all
sixteen strips are one design. The instinct to minimise cable length is the wrong objective here.

**Some costs are structural, not fixable.** The monolith carries two antenna planes on one
substrate's two faces. Any per-line strip uses one face and wastes the other, so 1.94 times the
area is inherent to the idea rather than a drawing that could be tightened. Recognising that up
front saves redrawing it.

The coupling extraction was re-run on the new stackup through the same solver rather than inherited:
identical self inductance and adjacent-line coupling, worst row-to-column coupling 0.0652 against
0.0664. Splitting the planes onto separate substrates makes their separation a free parameter for
the first time, and it was deliberately set to reproduce the monolith so that the board change and
a coupling change could not arrive together.

## 2026-08-02 Quote: the split sensing plane is cheaper, and width is why

Updated [[split-sensing-plane]] with the JLCPCB figures. The open question was whether 1.94 times
the substrate would be outweighed by dodging the large-size surcharge, and it is, by more than
expected.

**A 300 by 33 mm board pays zero large-size assembly charge where a 300 by 300 mm one pays
50.47 EUR.** Both are 300 mm long, so length alone is not the trigger. Whether it is width or area
is not separable from two points, and I first wrote it up as width before noticing that. The
distinction is not academic: if the rule is area, a four-up strip panel reincurs a charge that four
separate strips avoid.

One working sensing plane: 26.92 EUR bare against 58.34, or 101.12 EUR assembled against 141.05.

Two things worth carrying. The vendor's five-piece minimum is part of the cost model rather than an
aside, because it forces four unusable boards to get one usable monolith while twenty strips is a
set plus spares. And fixed PCBA cost decides assembly route more than unit price does: 42.60 EUR of
the strip's 55.36 EUR PCBA is setup, stencil and feeder loading, which is why the spine, needed
twice per product, stays hand populated while the strip, needed sixteen times, is a real choice.

Also filed: enabling assembly nearly doubled the bare board price, 19.97 to 38.81 EUR, because the
vendor re-specifies the PCB for line handling. That cost appears in no line item named for it.

## 2026-08-02 Repartition: sixteen boards to four, on connector count

Updated [[split-sensing-plane]]. The sixteen-strip design was electrically fine and was superseded
anyway, which is the interesting part.

Sixteen strips needed sixteen connectors plus two spine boards carrying twenty more. Thirty-six
connectors was the entire parts-cost increase over the monolith, so the partition's cost was almost
purely its **interface**, not its content. Four boards of four lanes need eight connectors, delete
the spine design outright, and quote at 20.92 EUR the set against the strips' 26.92 and the
monolith's 58.34.

**When a partition's unit cost is dominated by the interface rather than the content, block size is
set by connector count, not by how finely the content divides.** Nothing in the electrical argument
distinguishes sixteen from four; the RF result survived the repartition untouched because the
boundary relative to the tank never moved and the loops never moved.

Three constraints in three different units, and the answer sits where they cross: connectors want
few boards, the fabricator's size charge wants boards under some width (280 mm is out, 140 is in),
and the five-piece minimum wants a board count that divides the set. Four satisfies all three.

Two things filed as costs of the choice. The on-board bus is autorouted where the spine's was drawn,
so its inductance is now a **bound** taken from the whole net's routed length rather than a value
read off a drawn geometry; the criteria pass at the bound, which is the honest way to keep it. And
four chained eight-bit registers make the selection a 32-bit shift where two made it 16, so a block
size chosen on fabrication economics reached back into firmware.


## 2026-08-02 The split wins and the monolith is retired

Closed the branch that had been carrying two sensing architectures. The four-lane board ships, the
300 by 300 mm matrix board becomes a recorded baseline, and the strip-and-spine design that
preceded both is deleted from the tree.

Corrected a stale figure in [[split-sensing-plane]]: the interconnect cost quoted there was the
sixteen-strip design's, 142 to 385 nH and 0.46 percent. The shipping four-board design is 181 to
773 nH and at most 0.99 percent. **Quadrupling the interconnect inductance roughly doubled a
sub-percent error**, which is the argument itself rather than a detail: the term is small because
of where the boundary sits relative to the tank, not because the cable is short. A number that
survives a fourfold change in its input is measuring the topology, not the geometry.

A second thing filed from the cleanup, and it is the more transferable one. **Retiring a design is
not the same as deleting it.** The quad instantiates the monolith's `matrix_cell` and its loop
geometry unchanged, and every quad figure is a delta against a matrix figure, so deleting the
matrix would have destroyed both the shared source and the baseline that justifies the choice. It
stays generated and in `make check` for exactly that reason. What was retired is the outline, the
stackup and the order path, and the documentation now says which of those three things it means.

Also: the repartition removed a fabrication risk nobody was tracking as a benefit. The matrix used
0.2 mm via drills into 0.4 mm pads, the tightest geometry in the product, on the largest and most
expensive board, where a fabricator tier change would have cost the most to discover. The quad is
0.3 into 0.6, the same standard tier as every other board. **A change made for one reason cleared a
risk filed under another**, which is worth checking for deliberately rather than noticing later.

## 2026-08-02 What the product actually costs, and the hole in the middle of it

First whole-product electronics cost model, filed as `docs/hardware/cost.md`. Roughly 155 to 165
EUR plus shipping and tax, **plus two display modules that have no price anywhere in this
repository or this vault**.

That is the finding. The sensing plane was the assumed dominant cost, the branch cut it to 28.20
EUR all in, and the exercise of totalling everything else revealed that the largest remaining line
item is the one nobody had ever quoted. A cost model is worth building early not because the total
is useful but because **it finds the unpriced item**, and an unpriced item hides best when
attention is on the one being optimised.

Two levers came out of it that were not visible from any single board:

- **Fixed assembly cost is charged per order, so it is a function of how many orders you place.**
  The hub and the power board are the only two boards going to factory assembly, both are 1.0 mm
  and 2 layers, and they currently go as two orders paying setup and stencil twice. One panel is
  about 9 EUR of fees and one shipment. `panel.py` already builds a panel from routed boards, so
  this is a change of which boards it takes.
- **Feeder fees are charged per unique Extended part, so panelising two boards that share no
  Extended parts saves nothing on feeders and everything else halves.** The corollary is that
  panelising boards that *do* share Extended parts is worth more, which is a reason to prefer the
  same part across boards beyond the usual inventory argument.

Also recorded: the register's 18.88 EUR of hub feeder fees is stale by four placements. The current
hub has four Extended factory parts, not seven, because the plan moved everything iron-reachable to
hand fitting. The saving was designed in months ago and has never appeared in a quote.

## 2026-08-02 The partition reached into firmware, and the map is not linear

Implemented the 32-bit selection chain the four-board sensing plane needs, which had been specified
and left undone. `software/firmware/port/matrix_encoding.h` and its host test.

The interesting part is not the width. It is that **half of every shift register drives nothing**,
because a board carries four lanes and the part has eight outputs, so the line-to-bit map is a
stride of 8 with a lane count of 4 rather than the linear map two full registers gave. Line n sits
at bit `8 * (n / 4) + (n % 4)`.

**A stride of 4 would have been wrong and would have looked right on any single board.** It only
fails once two boards are in the chain, which is the sort of defect that survives bench bring-up
and appears as a transposed board. Pinned with a test that spells the bytes out literally rather
than deriving them from the same expression the header uses, since deriving them would test
nothing.

Filed as a general shape: **when a partition leaves part of a component unused, the address map
stops being arithmetic on the index and starts being arithmetic on the packaging.** Worth checking
whenever a block size and a part's granularity disagree.

The encoding also had to fix something no board records: which board is which. The four are
identical, so chain order against plane (boards 0 and 1 the rows, 2 and 3 the columns) is an
assembly convention, and the firmware is now the place it is written down. That is a dependency on
the frame, which nothing in the repository has drawn yet.

## 2026-08-02 Mirrored the fee-free catalog, and it closed the substitution question

Ingested `Clippings/jlcpcb/economic-parts-2026-08-02.csv` as
[[jlcpcb-economic-parts-2026-08-02]]. 2004 rows, 1586 live, from lrks/jlcpcb-economic-parts, which
republishes JLCPCB's Basic and Preferred Extended lists weekly.

**First correction: the fee-free set is wider than "Basic".** JLCPCB waives the feeder-loading fee
for Preferred Extended parts too, so the question was never Basic-versus-Extended, it was *economic
catalog or not*. The vault had been treating the capture as a Basic list; it is 351 Basic plus 1235
Preferred Extended, and both classes are free.

**Second, the catalog answered the open substitution question outright, by category count rather
than by argument.** Of 1586 live parts, 1482 are diodes, protection, resistors, capacitors and
transistors. **Connectors: zero. Modules: zero.** Seven crystals, none at 27.12 MHz, though two are
in the exact 3225 footprint. So the project's seven feeder-fee parts are not merely hard to
replace: for the USB-C connector and the ESP32 module no fee-free part of that *class* exists at
all. An earlier analysis had named the USB-C connector a viable candidate; that is withdrawn.

The transferable move: **when a per-item search keeps failing, count the categories instead.** A
histogram of the candidate set answered in one query what part-by-part comparison had been
answering slowly and wrongly, and it converted "we could not find one" into "there is none", which
is a different and much more durable claim.

The one part with a real pool, the reverse-polarity FET, has sixteen fee-free candidates and all
sixteen are SOT-23 at 33 to 45 milliohm. At 4.442 A RMS that is 0.65 to 0.89 W in a 1.2 to 1.5 W
package. The pool exists and is uniformly the wrong class of part, which is its own kind of answer.

**Membership did not drift.** All 2004 rows match the 2026-07-24 capture; only price, stock and
lastSeen moved. Worth recording because it sets the recheck interval: this is a question to revisit
per quarter, not per order.

Deliberately did not mirror the full 700k-part catalog. It is large and every question this project
asks is about the fee-free subset. Interactive whole-catalog search stays at yaqwsx.github.io/jlcparts.

## 2026-08-02 One order is impossible, and the reason is regulatory

Filed the ordering plan in `docs/hardware/cost.md`. Four parcels is the floor, not one.

**LCSC and JLCPCB will merge two orders into one shipment**, which is the win: it puts all five
board designs and all 270 hand-fit parts in a single parcel and a single customs event. Place both,
then ask support to combine, or bind the JLCPCB order during LCSC checkout. Same currency and
customer ID required, and **once combined the orders cannot be split**, so it has to happen before
either ships.

What cannot join them is more interesting than what can. The displays exist only at the
manufacturer, the NFC inlays only at a tag distributor, and the protected cell is blocked by
**UN 38.3 lithium transport rules** rather than by any commercial fact. A constraint that looks like
a sourcing inconvenience is actually a shipping-class one, and no amount of supplier consolidation
moves it.

Generalises as: **before optimising the number of orders, check which items are legally
un-consolidatable.** Those set the floor, and the remaining freedom is only over everything else.

## 2026-08-02 The upload pair was quoting the road not taken

Found while preparing order artifacts, and it would have cost real money quietly. The generated
`<board>_jlcpcb_upload_bom.csv` excluded hand-routed parts **only on boards that were entirely hand
populated**. On the hub and the power board, the two that actually go to assembly, the upload pair
was byte-identical to the max-assembly pair: 19 Extended rows offered to the factory where the build
plan plans four.

At 2.70 EUR a feeder change that is **67.50 EUR across the two boards**, against a hub assembly bill
of about 30. The plan to hand-fit every iron-reachable Extended part had been designed, documented
and costed months earlier, and the file you upload did not implement it.

**The failure mode is worth naming: a plan that lives only in a column.** The engineering BOM
carried an `Assembly Route` column saying `Hand`, and the sourcing register described the hybrid
plan in prose, and the exported artifact ignored both. Nothing was inconsistent enough to fail a
test, because the tests checked BOM-against-CPL agreement and both files were wrong together.

Fixed by excluding Hand routes from the upload pair on every board, which is what "the plan actually
chosen" already claimed to mean. The max-assembly pair still ignores routes on purpose, because its
job is to price the alternative.

Generalises as: **an intent expressed as metadata is not implemented until something consumes it.**
Worth checking, for any column that encodes a decision, which artifact actually reads it.

## 2026-08-02 Cell survey: the supplier decides the answer

Surveyed 18650batterystore.com per the owner's constraint. Eighteen 21700 cells, **one protected**:
Nitecore NL2150HP, 5000 mAh, 15 A, USD 24.95.

The acceptance table in `docs/hardware/cell-assembly.md` selected the candidate by itself, which is
the point of having written it. It also produced a clean fail nobody had anticipated: the cell is
**button top with no leads**, against a requirement for 18 AWG into a Molex housing. Bridging that
means a holder, which inserts 10 to 30 milliohm of spring contact into the highest-current path in
the product, or spot-welded tabs onto an already-protected cell.

Two things filed. **A protected cell and a wired pack are different products**, and an acceptance
spec written around wire gauge silently assumes the second. And **the constraint that decides
availability may not be electrical at all**: the retailer is in Atlanta, and shipping lithium cells
to Italy is governed by UN 38.3 and refused by many carriers, which can invalidate the entire survey
independently of any cell's specification.

## 2026-08-02 Thin stock is free, and the escape route stays on the shelf

0.6 mm on a 300 mm outline priced against 0.8 and 1.0 mm at the same outline and quantity: **all
three the same price**. That was the last open fabrication risk on the shipping sensing board and it
is closed.

Worth keeping the sequence rather than just the answer. An earlier revision asserted "quoted and
accepted" when the quote had been at the fabricator's default 1.6 mm; the claim was withdrawn as
unverified; the thickness was then actually priced and the withdrawn claim turned out correct. **A
guess that happens to be right is still not evidence**, and the cost of insisting on that was one
extra line on a quote request.

The contingency built beforehand is now unused and stays documented: separation is
`QUAD_THICKNESS + INTERPLANE_GAP`, so 0.8 mm board with a 0.2 mm rib would have given the identical
1.0 mm. That optionality is a dividend of the partition nobody designed for, since the monolith's
plane separation *was* its board thickness and it had no such move available.

## 2026-08-02 A panel needs its own CPL, and the reason is geometry

`make panel-fab` now emits `panel_jlcpcb_upload_bom.csv` and `panel_jlcpcb_upload_cpl.csv`.

The gap was structural rather than an oversight. **A CPL is board-relative**, so a constituent
board's pair cannot be uploaded against the panel: every placement would sit at the wrong
coordinate. The panel is what a fabricator makes, so the panel is what needs a pair, and the docs
had been describing the panel as the fabrication unit while the tooling could not export one.

Two details made it tractable. Only one board on the panel is assembled, since both light bars are
hand populated, so the panel's assembly job *is* the power board's with an offset. And `panel.py`
already suffixed every reference on copy, for an unrelated reason (two J1 pads on one panel confuse
assembly and DRC), which happened to supply exactly the unique designators an assembly upload
requires. **A constraint solved for one reason turned out to be the precondition for another.**

The suffix map travels as a JSON manifest rather than being inferred, because `panel.py` runs under
the system interpreter for pcbnew and `fab.py` under the venv, so they cannot import each other.
Verified as a rigid translation: identical placement count, identical rotations and layers, one
uniform offset.

## 2026-08-02 Constraining the supplier did not change the cell

The owner accepted reverting to the wired Keeppower pack after the 18650batterystore.com survey,
and the acceptance table in `docs/hardware/cell-assembly.md` made that a one-comparison decision
rather than a debate: worse capacity, twice the price, and no leads.

The durable finding is the distinction the survey exposed. **"Protected cell" and "wired pack" are
different products**, and an acceptance specification written around wire gauge, terminal insulation
limits and connector re-termination silently assumes the second. Every requirement below the
electrical table depends on leads existing. A bare protected cell, however good, restarts that part
of the design, and no row in the electrical table would have caught it.

## 2026-08-02 The display blocker was answered in a document we already had

Three artifacts arrived for the display: the module datasheet, an ESP32 tutorial, and the SSD1362
controller datasheet. Only one was new.

The **module datasheet** is byte-identical to the copy filed on 2026-08-01. The **SSD1362** is
revision 0.20 "Product Preview", Aug 2014, watermarked confidential to a third party, and is
**superseded** by the revision 1.0 "Advance Information" already in `Datasheets/`. Neither was
filed; the duplicate and the older revision were discarded rather than added. Only the **ESP32
tutorial** was new, and it is now in `Clippings/buydisplay/`.

**And the open V1 blocker turned out to be answered by the revision already filed.** The record said
the interface-select configuration "is documented nowhere", which was true of the *module*
datasheet and false of the *controller* datasheet sitting next to it since 2026-07-30. SSD1362
Table 6-2: four-wire SPI is BS[2:0] = 000, the module's default 8080 parallel is 110, and the
0-ohm jumper pairs on the module's back are what strap those pins.

**The transferable lesson is about where a question gets filed.** The blocker was recorded against
the module, so it was searched for in the module's document. A module is a controller plus a panel
plus a carrier board, and a question about the controller's configuration was never going to be
answered by the carrier's datasheet. **When a document does not answer a question, check whether it
is the document that should.**

Two smaller results. Table 7-1 requires D2 to be tied low in four-wire SPI, so this design's
ten-pin ground list is right and **the vendor's own tutorial, which grounds nine and omits D2, is
the one in error** — a reminder that manufacturer example code is not manufacturer specification.
And section 7.1.3 allows only write operations in serial mode, so no driver may read the controller
back, which is cheaper to know now than at bring-up.

What remains open is narrower and now checkable: which strap state a shipped module has. It cannot
be fixed after delivery, because module datasheet 7.3 forbids modifying the board and 7.7 excludes
it from warranty. So the plan to inspect and re-strap on arrival is withdrawn and replaced by a
purchase condition: **supply configured for four-wire SPI, BS[2:0] = 000.** A vague technical
unknown became a precise line on an order.


## 2026-08-18 The BUSY contract moved from a code comment into the wiki

Extended [[pn5180a0hn-c3e-datasheet]] with the section 11.4 host-interface facts and the IRQ_STATUS
bit table. The firmware's PN5180 driver was built on a BUSY sequence cited as "datasheet 11.4" that
no wiki page had transcribed, so the one contract V6's peripheral model must reproduce was sourced
from a comment. A quality audit flagged both the missing transcription and the handshake bug it
hid: the driver waited for BUSY low twice and never observed the rise, so the completion wait could
not distinguish "finished" from "not started". The driver now watches for the rise with a tolerated
short window before trusting the fall, and the facts it rests on are filed where a reviewer and the
V6 model can check them. The IRQ table also records RX_SC_DET (bit 15), the subcarrier-detection
path that would decide an empty inventory slot in a third of a millisecond instead of six; wiring
that in stays a bench-measured change, but the register bit is no longer unfiled.


## 2026-08-19 The four V3 vendor gaps, re-searched against current documents

Updated [[ap63203wu-7-datasheet]], [[ap22811aw5-7-datasheet]] and [[tps61088rhlr-datasheet]] with
a targeted search of the current manufacturer documents, and sharpened the four V3 open items in
planning to match what actually exists. Two statements were too strong and are corrected: the
AP63203's compensation network is not unpublished, its nominals are on the Rev. 3-2 block diagram
(7.6 nF, 18 kOhm, 20 kOhm, slope compensation and current-sense ratio), and a typical
RDS(on)-versus-temperature curve exists as Figure 9. What no document provides, for any of the
four, is tolerance or corner information: no maximum RDS(on), no FLG rating at all on the AP22811
(a 5 V test condition is not a rating), and a TPS61088 GEA that is typical-only with TI excluding
its own application equations from the specification. So the gaps stand for worst-case release
evidence, but a nominal AP63203 transient model moved from impossible to open work, and every gap
now states precisely which number is missing, which is what a vendor query or a V8 measurement
plan needs.


## 2026-08-20 Which pads are correct: the datasheet answers

Appended the DCK land pattern to [[tlv7021dckr-datasheet]]. The question came from the power
board's seven DRC violations on KiCad 9.0.9: replaying the reviewed route against that release's
grown SOT-353 pads. TI's drawing 4214834/G recommends 0.95 x 0.4 mm pads on a 2.2 mm span; the
9.0.9 generic is 1.325 x 0.4 on 3.1 mm, oversized by 0.45 mm per side. So the bound footprint is
the manufacturer-consistent pattern and the reviewed board is correct; the drifted library is
merely different, and hardware/pcb/vendor_libraries.py now exists so the bound set travels with
the repo instead of living on one machine.
