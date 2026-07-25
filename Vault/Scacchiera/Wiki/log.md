---
type: log
date_updated: 2026-07-24
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
