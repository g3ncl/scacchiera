---
type: concept
date_updated: 2026-07-24
source_count: 1
confidence: high
tags:
  - wiki/concept
---

# BitwiseXY

[origin::[[ben-bulsink]], [[bitwiseid-whitepaper|Bitwise ID + Set Management v2.1]], Appendix 2] [extends::[[bitwiseid-method]]]

A further acceleration of [[bitwiseid-method|BitwiseID]] for large tag populations, where
transport time of a large identity bit-field starts to dominate (roughly above ~350 identity
bits). Instead of coding a fixed identity into each tag, code each tag's **current coordinates**
into two bit fields, one per row and one per column (e.g. 19 bits each for a 19x19 board): a tag
at (row 7, col 12) sets bit 7 of its row field and bit 12 of its column field, all else zero, under
the same one-tag-per-position condition BitwiseID relies on.

Reading a column antenna then directly ORs the row fields of every tag on that column, which lists
which rows are occupied on that column without any further lookup. A tag whose stored coordinate
does not match the antenna it is actually read on has moved; the paper resolves this with a
classic anticollision read by UID, a table lookup, and a coordinate rewrite, measured at under 35
ms total (read ~25 ms, lookup, write ~10 ms).

## Speed tradeoff versus BitwiseID

BitwiseID re-reads its full identity bit-field every scan; BitwiseXY only reads/writes ID bits on
a move. For a 19x19 Go board the paper gives BitwiseID at ~608 ms per full scan (38 antennas x 16
ms) versus BitwiseXY at ~304 ms (38 x 8 ms) plus ~56 ms per detected movement, i.e. BitwiseXY
suits larger tag sets where per-scan transport time would otherwise dominate.

## Sources

- [[bitwiseid-whitepaper]]

## Related

- [[bitwiseid-method]]
- [[row-column-antenna-matrix-technique]]
