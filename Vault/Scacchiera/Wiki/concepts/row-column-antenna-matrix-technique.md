---
type: concept
date_updated: 2026-08-02
source_count: 4
confidence: high
tags:
  - wiki/concept
---

# Row-column antenna matrix (technique)

[origin::[[nfc-game-board-project]]] [demonstrated_on::15x15 Scrabble board, 30 antennas]

Replace one dedicated antenna per board position with one antenna per **row** and one per
**column**, read through a single shared reader. A tag's position is the intersection of "which
row antenna saw this UID" and "which column antenna saw this UID." Antenna count drops from
`rows x columns` to `rows + columns` (for a 15x15 board, 225 -> 30; for an 8x8 board, 64 -> 16).

## What makes it unambiguous

A passive resistive keypad matrix suffers classic ghosting: two simultaneous presses can't be
told apart from two phantom presses at the swapped coordinates. This technique avoids that because
each tag reports a **unique UID** on every line it couples to, so row and column reports are
joined per UID, not per raw coordinate. The classic ghost only reappears if two tags share a UID,
or if a tag couples to two adjacent lines at once (an overlap/tuning failure, not an ambiguity of
the method itself).

## What the source project reports

Per [[nfcgameboard-schematics]]: 15 rows + 15 columns = 30 antennas, multiplexed with
[[pin-diode-antenna-switching|PIN diode switches]]. The antennas are only meant to detect tags
directly above the board surface, not tags outside the antenna's own outline; the paper notes this
requirement is forgiving enough to tolerate **bad tuning and long antenna feed lines**, which
lowers the bar for a first attempt at long row/column antennas. Per-line reads that used to be
single-tag become multi-tag inventories, which is the throughput problem
[[bitwiseid-method|BitwiseID]] and [[bitwisexy-method|BitwiseXY]] solve.

## Relation to our design

This is the reference architecture behind our own chessboard sensing design: same row+column,
one-reader idea, applied to an 8x8 chessboard (16 antennas) instead of a 15x15 Scrabble board
(30 antennas). Our own hardware is being rebuilt from scratch on the functional spec in
[[../../../../docs/functional/overview.md|docs/functional/]], tracked in
[[../../../../docs/planning.md|docs/planning.md]]. Three coupled risks carry over from the source
project's experience: long antenna geometry/tuning (low risk, per this page), multi-tag
anticollision per scan (solved by BitwiseID/BitwiseXY, our own firmware work still to do), and
overlap tuning between adjacent lines (physics understood via an ST community thread, not yet
prototyped by us).

## Sources

- [[nfcgameboard-home]]
- [[nfcgameboard-schematics]]
- [[nfcgameboard-pcb]]
- [[nfcgameboard-software]]

## Two board partitions, one technique

The technique says nothing about how many PCBs carry the antennas, and both answers have now been
built and validated in this project. One 300 by 300 mm board puts rows on front copper and columns
on back; sixteen strips stacked crosswise put each line on its own substrate. The extracted
coupling is the same to four figures either way, because it is set by the loop geometry and the
plane separation, neither of which the partition changes.

What the partition decides is cost of change, not electrical behaviour. See
[[split-sensing-plane]].

## Related

- [[split-sensing-plane]]
- [[nfc-game-board-project]]
- [[bitwiseid-method]]
- [[bitwisexy-method]]
- [[pin-diode-antenna-switching]]
