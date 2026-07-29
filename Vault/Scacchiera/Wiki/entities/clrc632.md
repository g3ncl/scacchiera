---
type: entity
date_updated: 2026-07-24
source_count: 2
tags:
  - wiki/entity
---

# CLRC632 (reader IC)

[kind::RFID reader IC] [protocol::ISO/IEC 15693] [used_by::[[nfc-game-board-project]]]

The RFID reader IC chosen for the [[nfc-game-board-project|NFC Game Board]] project. Per the
[[nfcgameboard-schematics|schematics page]], described by the author as "an older IC, bulky and
more expensive, but well documented," with modern redesigns able to use any IC supporting
ISO/IEC 15693. The [[bitwiseid-whitepaper|BitwiseID white paper]] cites its **ColPos register**
(section 10.5.2.4) as the mechanism that detects the bit position of an unequal value during a
collision, i.e. delivers tags' logical OR to the reader, which is the physical basis the whole
BitwiseID method rests on. See [[bitwiseid-method]].

As of the [[nfcgameboard-home|home page]] capture (2026-07-24), the author has an active study
underway to replace it with the NXP PN5180 multi-protocol reader, reporting matching timing (9 ms
Inventory, 12 ms ReadSingleBlock) against community Github libraries.

Not the reader our own design uses. An earlier generation used an ST25R200 (ISO/IEC 14443-A, a
different protocol family); the from-scratch rebuild tracked in
[[../../../../docs/planning.md|docs/planning.md]] settled on the **PN5180**, the same successor this
project's author validated against the CLRC632 (matching Inventory and ReadSingleBlock timings),
because ISO/IEC 15693 is where [[bitwiseid-method|BitwiseID]] is proven. See
`docs/hardware/hub.md` for the hub design that carries it.

## Sources

- [[nfcgameboard-schematics]]
- [[bitwiseid-whitepaper]]

## Related

- [[nfc-game-board-project]]
- [[bitwiseid-method]]
