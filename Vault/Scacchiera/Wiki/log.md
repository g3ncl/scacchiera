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
