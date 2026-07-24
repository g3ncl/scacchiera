---
type: overview
date_updated: 2026-07-24
tags:
  - wiki/overview
---

# Overview

High level synthesis of everything the wiki knows. This page is regenerated as
the big picture changes during ingestion. Start here for the shape of the
knowledge base, then follow [[wikilinks]] into [[index|the index]] and the
individual pages.

## NFC Game Board: the reference project

The wiki's first ingest covers [[nfc-game-board-project|NFC Game Board]], [[ben-bulsink|Ben
Bulsink]]'s open Scrabble-board project (nfcgameboard.com), captured because it built and measured
the same core idea the chessboard's sensing design is built on: **one RFID reader, a row+column
antenna matrix instead of one antenna per position** (see
[[row-column-antenna-matrix-technique]]), an 8+8 matrix (16 antennas) on our 8x8 board. The
chessboard's own hardware implementation is being rebuilt from scratch on top of the functional
spec in [[../../../docs/functional/overview.md|docs/functional/]], tracked milestone by milestone in
[[../../../docs/planning.md|docs/planning.md]]; this project supplies real, measured prior art for
two of the row-column technique's three coupled risks:

- **Antenna geometry and tuning** (low risk): the source project tolerates "bad tuning and long
  feeding lines" because antennas only need to reject tags outside their own footprint, not tune
  precisely.
- **Multi-tag anticollision per scan** (the real work): solved on the source project's side by
  [[bitwiseid-method|BitwiseID]], a one-hot bit-coding technique that reads an entire row or
  column of tags in one operation by relying on the reader's logical-OR collision behavior,
  holding 0.35 s response time flat up to 225 tiles. [[bitwisexy-method|BitwiseXY]] extends it for
  larger tag counts by coding coordinates instead of identity, and
  [[set-management-and-setid|set management]] keeps one system's tags from colliding with a
  foreign set's. None of this is yet proven on our own tag protocol (ISO/IEC 14443-A, versus the
  source project's ISO/IEC 15693); that gap is explicit in [[bitwiseid-method]].
- **Overlap tuning between adjacent lines**: not directly addressed by this source; still an open
  item for our own design.

The source project also independently converged on
[[pin-diode-antenna-switching|PIN diode antenna switching]] to keep parallel switch capacitance
off a shared HF bus, the same fix an earlier iteration of our own SPICE simulation reached for the
same reason (see [[pin-diode-antenna-switching]] for that result; the switch device is an open
decision again in the from-scratch rebuild).

See [[nfc-game-board-project]] for the full architecture and [[bitwiseid-whitepaper]] for the
detection method in detail.
