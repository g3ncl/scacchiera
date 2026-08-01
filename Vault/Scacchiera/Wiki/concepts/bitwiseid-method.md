---
type: concept
date_updated: 2026-08-01
source_count: 1
confidence: high
tags:
  - wiki/concept
---

# BitwiseID

[origin::[[ben-bulsink]], [[bitwiseid-whitepaper|Bitwise ID + Set Management v2.1]]] [used_by::[[nfc-game-board-project]]]

A method to identify every RFID tag on one antenna in a single read, instead of running
anticollision inventory tag by tag. Core trick: don't identify a tag by its factory UID, identify
it by a **unique one-hot bit pattern** written into the tag's own read/write memory, then issue an
unaddressed `ReadBlock`/`ReadMultipleBlocks` command that every tag in the field answers at once.
Colliding bits arrive at the reader as their **logical OR** (the physical basis is the reader IC's
collision-position detection, e.g. the [[clrc632|CLRC632]]'s ColPos register). If the coding
guarantees at most one tag carries a "1" in any given bit position, that "1" survives the OR
undamaged, so reading N bits in one operation enumerates up to N tags at once.

Worked example (3 tags, one-hot at bits 0, 1, 3): tag x sends `00000001`, tag y sends `00000010`,
tag z sends `00001000`; the reader sees `00001011` and all three are identified in one read.

## Why it exists

Standard per-antenna anticollision inventory scales badly with tag count: the source paper
measures an 8x8-chessboard-equivalent scan (16 antennas, 32 tags, ~4 average tags/antenna after
empty rows) at 616-745 ms per cycle with classic anticollision, growing to ~7 s for a 19x19 Go
board (~281 tags). BitwiseID reads a 400-tag, 400-bit Go board field in ~608 ms total (38
antennas x ~16 ms), and a 100-tile Scrabble fill in ~450 ms versus 2.4-2.6 s classic, about 5.5x
faster in that case.

## Preconditions and set management

Needs a bounded, known tag population (bootstrapped one of three ways: initialise a fully
present static set at session start, pre-register tags in non-volatile memory before the
session, or register unknown tags on first placement at a ~50-100 ms cost each) and uniform tag
timing across the whole set. See [[set-management-and-setid]] for how the paper keeps one
system's tags from being confused with a foreign set's tags that happen to share a bit code.

## Limits

Reliability degrades past roughly 10 simultaneous responders on one antenna, because a
zero/one bit collision reads as one (zero bits modulate more strongly than a lone one bit) and
large tag counts need a stronger antenna field to compensate. The paper's fix is a 16-slot Fast
Inventory that supplements identification with slot number, extending usable range to a 38-antenna
Go scan in ~760 ms worst case.

## Relation to our design

This is the concept that most directly de-risks the scan-loop cost of our own 8x8 row+column
antenna matrix design (see [[../../../../docs/planning.md|docs/planning.md]] for the current rebuild
plan), since every line scan under that architecture returns multiple tags per read.

The protocol question this page previously left open is now closed on the paper's side: as of
2026-08-01 the piece tag candidate is [[ad-circus-slix2]] carrying [[sl2s2602]] (ICODE SLIX2), so
the design runs ISO/IEC 15693 like the source paper, not ISO/IEC 14443-A. The SL2S2602 implements
`READ MULTIPLE BLOCKS` and `(FAST) INVENTORY READ`, which is what this method needs. Whether the
OR-collision behavior actually holds on the [[pn5180a0hn-c3e|PN5180]] rather than the paper's
[[clrc632|CLRC632]] is still an open bench question: the two readers expose collision position
differently, and nothing here has been measured.

## Sources

- [[bitwiseid-whitepaper]]

## Related

- [[bitwisexy-method]]
- [[set-management-and-setid]]
- [[row-column-antenna-matrix-technique]]
- [[clrc632]]
