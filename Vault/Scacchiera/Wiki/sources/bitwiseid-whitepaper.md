---
type: source-summary
date_updated: 2026-07-24
tags:
  - wiki/source
---

# Source: Bitwise ID + Set Management, version 2.1 (white paper)

Raw clipping: [Clippings/nfcgameboard.com/bitwiseid-whitepaper.md](../../Clippings/nfcgameboard.com/bitwiseid-whitepaper.md), PDF: [files/Bitwise-ID-version-2.1.pdf](../../Clippings/nfcgameboard.com/files/Bitwise-ID-version-2.1.pdf). [captured::2026-07-24] [author::[[ben-bulsink]]]

Formal write-up ("A method to increase the detection speed of electronic sensor boards based on
RFID", v2.1, March 2026) of the detection method used by [[nfc-game-board-project|NFC Game
Board]]. Third-party GPLv3 free documentation, © 2016-2025 Ben Bulsink. Transcribed in full in the
clipping (tables and bit examples reformatted as code; wording and numbers are the author's).

Covers, in order: the general architecture of row/column antenna sensor boards (chess, Go,
Scrabble, TagTile examples); why conventional per-antenna anticollision is too slow, with measured
component timings; the [[bitwiseid-method|BitwiseID]] method itself (one-hot bit coding read via
unaddressed block read, logical-OR collision behavior); its preconditions and a ~10-tag reliability
ceiling with a 16-slot Fast Inventory workaround (Appendix 1); [[bitwisexy-method|BitwiseXY]], a
coordinate-coding acceleration for large tag counts (Appendix 2); and
[[set-management-and-setid|set management and SetID]], keeping one system's tags distinguishable
from a foreign set's (Appendix 5).

Cites the reader IC's ColPos register (CLRC632 section 10.5.2.4) as the physical mechanism, ISO/IEC
15693 and 14443 as the relevant standards, and several prior-art applications (RFID
roulette/casino localization, RFID Scrabble per Engadget 2012, a chess patent US7791483, an ETH
Zurich RFID tabletop wargame, expired DGT/Saitek chess patents, TikTegel US20110309970A1).

## Sources used

- [[bitwiseid-whitepaper]] (this page)

## Pages touched

- [[ben-bulsink]]
- [[bitwiseid-method]]
- [[bitwisexy-method]]
- [[set-management-and-setid]]
- [[clrc632]]
