---
type: concept
date_updated: 2026-07-24
source_count: 1
confidence: high
tags:
  - wiki/concept
---

# Set management and SetID

[origin::[[ben-bulsink]], [[bitwiseid-whitepaper|Bitwise ID + Set Management v2.1]], Appendix 5] [used_with::[[bitwiseid-method]]]

The problem [[bitwiseid-method|BitwiseID]] and [[bitwisexy-method|BitwiseXY]] both leave open: a
tag from a different board or set can coincidentally carry the same bit code as one of ours and
become indistinguishable. The paper's fix is a **system identifier** read simultaneously with the
tag's bit coding, encoded as a fixed-weight bit pattern (a prescribed count of "1"s, e.g. exactly
8 ones in a 16-bit field). Because the read result is a logical OR, any foreign tag with a
different identifier pushes the observed one-count above the expected weight, which is directly
detectable without decoding individual tags. A 16-bit fixed-weight pattern already encodes over
12,000 distinct system identifiers.

## Bootstrapping a SetID

Two proposals in the paper:

- **Proposal 1:** on an empty board, compare the first placed tag's SetID against the previous
  session's; reuse the stored table on a match, otherwise generate a fresh SetID and re-register
  every tag under it. A 31-bit SetID with 15 ones gives ~2.8x10^8 variations, so accidental
  collisions are ignored in practice.
- **Proposal 2 (more secure):** always start a new random SessionID on power-up or an empty board,
  compare each readout's combined SetID against it, and fall back to classic anticollision plus a
  stored Set table lookup for anything that doesn't match. Registration measured at ~85 ms per tag
  (Jan 2017 measurement cited in the paper).

## Write-failure protection

Rewriting a tag's row/column or SetID value takes ~10 ms and fails 5-10% of the time if the tag is
moving during the write; in ~10% of those failures the written block goes to all-zero, and a
zero block is indistinguishable from "no tag" (invisible). The paper's two mitigations: keep
**two instances** of the data block (write the first, then the second, so the original survives
in the second copy if the first zeroes), and/or an **"ID-writing-in-progress" bit** set before the
write and cleared only after verification.

## Sources

- [[bitwiseid-whitepaper]]

## Related

- [[bitwiseid-method]]
- [[bitwisexy-method]]
