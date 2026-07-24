---
title: "Bitwise ID + Set Management, version 2.1"
source: https://nfcgameboard.com/wp-content/uploads/2026/05/Bitwise-ID-version-2.1.pdf
author: Ben Bulsink
captured: 2026-07-24
tags:
  - clipping
---

# BitwiseID and Set Management (white paper)

Transcription of the NFC Game Board project's "Bitwise ID + Set Management" white paper,
version 2.1 (March 2026), by Ben Bulsink, "A method to increase the detection speed of
electronic sensor boards based on RFID". Source PDF: [files/Bitwise-ID-version-2.1.pdf](files/Bitwise-ID-version-2.1.pdf),
originally fetched from <https://nfcgameboard.com/wp-content/uploads/2026/05/Bitwise-ID-version-2.1.pdf>.

Third-party GPLv3 free documentation (© 2016-2025 Ben Bulsink). Faithful transcription, lightly
reformatted for readability (tables and bit examples set as code). Wording and numbers are the
author's, not ours.

## Introduction

RFID object tracking is a common way to build electronic game boards (chess, Go, Scrabble, planning
boards). Tags are uniquely labelled, carry additional meaning in memory, and are mass produced. The
paper targets "electronic game boards": a bounded 2D surface on which objects carrying one or more
RFID tags are placed, moved, or removed, and an in-plane measurement system determines each tag's
location and identity.

Representative configurations:

- **Chessboard:** 8x8 squares, 34 pieces (extra queens), 12 identities. Up to 32 tags at the start,
  decreasing during play. Dead zones between squares are allowed.
- **Go board:** 19x19 (up to ~320 stones in practice), 2 identities, increasing during play.
- **Scrabble:** 15x15, 100 tiles plus racks, 27+ identities, increasing during play.
- **TagTile (TikTegel):** 12x12, 1-12 pieces, each its own identity, continuous field (no dead zones).

Detection under 1 s is acceptable, under 0.5 s desirable. The problem: with conventional anticollision
the scan time grows more than proportionally with tag count, and parallel readers add cost and
complexity.

## Architecture of the measurement system

One antenna under each row and one under each column, alternately connected to a single RFID reader
through an antenna multiplexer. The paper's footnotes state the multiplexer is built from **PIN diodes**
switching between low and high resistance with very low capacitance, and that the method was tested with
standard **ISO 15693 ICODE** tags (and, under conditions, ISO 14443 Type A).

Antennas may overlap or not. A tag reads on an antenna when roughly 60-85% of its surface falls within
that antenna. Non-overlapping antennas create dead zones between fields; overlapping antennas let a tag
read on more than one antenna, and the overlap can be treated as an extra field. Reading all antennas
in turn and combining the row and column results gives each tag's position. Tags carry a UID plus
writable memory holding the object's role (white pawn, black stone, letter W worth 8 points, etc.).

## The speed problem with the common method

The usual method runs a standard anticollision inventory on every antenna:

```
For every antenna, one by one:
  1. Inventory (1 slot) to detect 0, 1, or many tags. Skip where many are expected.
  2. On collision, run the full anticollision cycle.
  3. Read the role for the found tags.
  4. Combine data from all antennas, resolve position and role, report to the app.
```

Measured/average component times the paper cites:

- Inventory (1 slot): 18 ms with 0 tags, 28 ms with 1 tag, 12.3 ms with multiple.
- Anticollision (>=2 tags, no collision): 16.8 ms + (tags x 3.9 ms).
- Collision retries are probabilistic: 4 tags -> 33% chance of a repeat, 8 tags -> 88%.

Worked chessboard total (8 rows + 8 cols = 16 antennas, 32 pieces, 4 empty rows at start):

- 4 x 18 ms empty rows = 72 ms (an empty row still costs 18 ms).
- 12 x anticollision, ~4 responders average = 12 x 39 ms = 396 ms.
- Collision-retry overhead = 195-324 ms.
- **Total: 616-745 ms per cycle.** Go (19x19, ~281 tags) reaches ~7 s. This is the motivation.

Measured INV_AC times by tags-on-antenna (min/max over ~5 runs), for context:

```
tags   min(ms)  max(ms)   min/tag  max/tag
0      18       19        -        -
1      28       30        28       30
2      38       97        19       49
4      39       88        10       22
8      81       106       10       13
15     162      186       11       12
```

A random 100-tag Scrabble fill with per-row/column/rack anticollision gives 2.4-2.6 s. The author's
BitwiseID implementation does the same in **450 ms**, a factor ~5.5 faster.

## The new method: BitwiseID

Do not identify a tag by its UID; identify it by a **unique one-hot bit pattern** written into the tag's
R/W memory. Read that memory with a ReadBlock / ReadMultipleBlocks command issued **without addressing a
specific tag**, so every tag in the antenna field answers simultaneously. All bits arrive at once.

The key physics: when bits collide in the field, the reader receives the **logical OR** of all tags'
data (the paper cites CLRC632 reader IC section 10.5.2.4, the ColPos register, which detects the bit
position of an unequal value; the same signal drives standard anticollision). So if the coding
guarantees that **at most one tag carries a "1" in any given bit position**, that "1" survives the OR
and the tag is recognised. Each tile/position is assigned its own bit; reading N bits enumerates N
possible tags in one operation.

Worked example, three tags coded 1, 2, 4 (one-hot at bit positions 0, 1, 3):

```
Tag x sends 00000001   (code 1)
Tag y sends 00000010   (code 2)
Tag z sends 00001000   (code 8)
--------------------------------
OR result   00001011   -> x, y, z all present, all identified in one read
If y absent  00001001   -> only x and z
```

For a 400-tile Go board, 400 bits (50 bytes) at 25 kbit/s take ~16 ms per antenna; 19 rows + 19
columns = 38 antennas is ~608 ms for a full scan. "With one read operation, all tags were detected and
identified."

### Preconditions (area of use)

A limited, known set of tags is used and initialised for the setup. Three ways to bootstrap:

- **Option 1:** all tags present and static at session start; inventory and initialise them, then no
  new tags appear during the session.
- **Option 2:** tags made known before the session (placed once, or programmed in production) and
  stored in non-volatile memory; afterwards used freely, including from a power-up empty board.
- **Option 3:** arbitrary tags allowed; unknown tags are registered on first placement (~50-100 ms per
  tag) and thereafter tracked by movement speed.

All tags in a system must have identical timing behaviour (the basis of standard anticollision). Tested
successfully with Philips/NXP SL2 ICS20 label ICs.

### Avoidance/detection of system (set) mixing

A tag from another board/set can share a bit code and become indistinguishable. Solution: give each
system a **system identifier read simultaneously with the bit coding**, encoded as a fixed-weight bit
pattern (a prescribed count of "1"s). Example: in a 16-bit field, exactly 8 ones and 8 zeros. Because
the read result is the OR, any foreign tag with a different identifier pushes the result above 8 ones,
which is detectable. A 16-bit fixed-weight pattern encodes more than 12,000 system identifiers.

### Recoding a foreign tag, and interrupted writes

When a foreign SetID is detected, fall back to classic anticollision, verify the system and tag coding,
and rewrite it to fit the current system.

Rewriting a row/column value in a tag takes ~10 ms, during which the tag must stay in the field. Moving
tags fail the write 5-10% of the time. In >90% of failures the data is unchanged, but in ~10% the block
being written becomes zero, and a zero block makes the tag invisible (zero cannot be distinguished from
other tags' data). Two fixes:

- **Two instances** of the data block: write the first to success, then the second; the original
  survives in the second instance if the first goes zero.
- **An "ID-writing-in-progress" bit** set before the ID array write and cleared after verification.

### Resulting speed

- BitwiseID: Go board, 38 antennas, 400 tags -> ~38 x 16 ms = **608 ms**.
- BitwiseXY (below): same board -> ~38 x 8 ms = **304 ms**, plus ~56 ms per movement.

### Coding the role in the same array, and semi-unique tags

The piece role can be co-stored: chess has 12 roles = 4 bits (0000 = no tag); 34 pieces = 136 bits, plus
16 system bits = 152 bits, ~5.4 ms to send. Go needs 1 role bit per stone. Co-coding the role is often
unnecessary because the role is already read at BitwiseID/XY time and cached in a microcontroller table.

For applications that do not want full set management (e.g. a Scrabble rack), tags can carry a **short
semi-unique sequence number** (16-20 bits, 64k-1M values) assigned at production. Collisions are
negligibly rare. A rack antenna reads this page via an Inventory-Read anticollision and reports the
letters, no set management needed. Rack timing: single antenna ~30 ms for 7 tags; 8 overlapping
antennas ~240 ms.

### Required tables (for BitwiseID)

```
FifoReadBuf  : 64 bytes, read data from one antenna
FifoWriteBuf : 20 bytes, command to send to tags on one antenna
EE_ID_USE    : list of tag IDs used in the system
EE_ID_ROLE   : role of each of those tags
EE_ID_AUX    : other information per tag
```

## Restriction (Appendix 1)

Reading many simultaneous responders gets unreliable past ~10 tags on one antenna. When a ZERO and a ONE
collide, a modulation is present for the whole bit time and the decoder reads ONE; because the ZERO bits
(emitted by almost all tags) modulate much more strongly than a lone ONE bit, large tag counts need a
slightly stronger antenna signal, a problem for Scrabble/Go.

Fix: use a **16-slot Fast Inventory** (1 page = 32 bits) and use the slot number to supplement the
identification. Collision can still occur within a slot, but with a good distribution over 16 slots the
disruption does not occur. A 32-bit data field across all 16 slots reads within ~20 ms (6 command bytes
~3 ms + 16 x 4 bytes at ~1 ms/slot). A 38-antenna Go scan is then ~760 ms max, still usable.

## Appendix 2: BitwiseXY (further acceleration)

When identity needs many bits (>~350), transport time dominates. Instead, code each tag's **current
coordinates** into two bit fields: a row field and a column field (19 bits each for 19x19). A tag on
(row 7, col 12) has bit 7 of its row field and bit 12 of its column field set, the rest zero. Condition:
at most one tag per field (position).

Reading a column antenna then ORs the row fields of the tags on that column, so the result directly
lists which rows are occupied on that column, and vice versa.

Example, 4x4, three tags on column 3 (rows 1, 3, 4):

```
        column field   row field
Row 1   0010           1000
Row 2   ----           ----      (no tag)
Row 3   0010           0010
Row 4   0010           0001
------------------------------
OR      0010           1011      -> column 3, tags on rows 1, 3, 4
```

Moving a tag from (row 2, col 2) to (row 3, col 2):

```
        column field   row field
Row 1   0010           1000
Row 2   0100           0100      (stale coords: not on col 2 / row 2 anymore)
Row 3   0010           0010
Row 4   0010           0001
------------------------------
OR      0110           1111
```

A tag whose written coordinate does not match the antenna it is read on has moved; identify it (classic
anticollision by UID) and rewrite the correct coordinate. Detecting and adjusting a moved tag takes <35
ms (read Bitwise ID ~25 ms, look up UID in a static table, write new coordinate with UID addressing ~10
ms). Method implemented and tested.

## Appendix 5: Set management (initialisation of tags)

Ideally the measurement system, not the user, keeps sets of tags separated. Preconditions: max tag count
limited by bits-per-scan (BitwiseID) or ID bits at (re)placement (BitwiseXY). BitwiseID reads all its
bits every scan (128-bit ID -> ~0.35 s scan on a 30-antenna Scrabble board; 512-bit -> ~1.2 s).
BitwiseXY reads ID bits only on a move (128-bit -> +~50 ms per move; 512-bit -> +~80 ms), so it suits
large sets.

**Proposal 1 (start with old SetID):** on detecting an empty board, compare the first tag's SetID with
the previous session's. If they match, reuse the stored table; if not, generate a new SetID, clear the
table, and register every newly detected tag under it. Risk: a full table forces re-encoding all tags to
a fresh SetID, which is slow and risky (an unaddressed WriteBlock can catch conflicting tags added
meanwhile). A 31-bit SetID with 15 ones gives ~2.8x10^8 variations, so accidental collisions are ignored
in practice. Recode row/column by row/column, checking for duplicates first.

**Proposal 2 (more secure, always start with new SetID):** on power-up or empty board + empty racks,
generate a random SessionID (or only when the first placed tag does not match the last SessionID, so an
unchanged set is not re-registered). On each antenna readout, check that the combined SetID matches the
SessionID; if not, run an anticollision read of UID/Role/SetID/ID, compare against the stored Set table,
and assign new IDs where needed. An `AddedInSet` array marks which table entries have been seen this
session. A SetIDcopy block guards against write failures leaving a zero (as with BitwiseXY). New-ID
assignment: mark pending (write SetID + InProgress bit), verify, write the second copy, update the
BitwiseID field, then clear InProgress. Registration measured at ~85 ms per tag (Jan 2017).

## References (from the paper)

- ISO/IEC 15693 parts 2 and 3 (vicinity cards, air interface and anticollision); ICODE SL2 ICS20 spec.
- ISO/IEC 14443 parts 2-4 (proximity cards).
- Reader IC CLRC632 (ColPos register, section 10.5.2.4).
- Prior-art applications cited: RFID roulette/casino localization, RFID Scrabble (Engadget 2012), chess
  patent US7791483, ETH Zurich RFID tabletop wargame (Hinske), DGT/Saitek chess patents (expired),
  TikTegel US20110309970A1.
