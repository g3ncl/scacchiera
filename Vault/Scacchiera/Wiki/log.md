---
type: log
date_updated: 2026-07-26
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
