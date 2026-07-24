---
type: entity
date_updated: 2026-07-24
source_count: 4
tags:
  - wiki/entity
---

# NFC Game Board (project)

[url::https://nfcgameboard.com/] [author::[[ben-bulsink]]] [status::active, redesign in progress as of 2026-07]

Open hobby project by [[ben-bulsink|Ben Bulsink]] demonstrating an RFID-sensed physical
Scrabble board: a 15x15 grid of tiles, each carrying a passive ISO/IEC 15693 ICode NFC tag,
read through one shared reader multiplexed across a row+column antenna matrix rather than one
antenna per tile. The site states the design goal plainly: match human manipulation speed, i.e.
respond to a tile move within about half a second, and hold that response time flat as tile
count grows to 225.

This is the primary prior art behind our own row-column antenna matrix direction (see
[[../../../docs/planning.md|docs/planning.md]] for the current rebuild plan): same core idea (one
reader, a matrix of row/column antennas, tag UID intersection gives position) applied to a 15x15
Scrabble board instead of an 8x8 chessboard.

## Architecture (from the captured pages)

- **Reader:** [[clrc632|CLRC632]] RFID reader IC, ISO/IEC 15693, on a redesign path toward the NXP
  PN5180.
- **Antenna matrix:** 15 rows + 15 columns = 30 antennas under the board, multiplexed with **PIN
  diode switches** (not analog-switch ICs) because parallel switch capacitance across 30
  switches would detune the HF tank; higher PIN bias voltage gives lower capacitance and lower
  forward resistance. A 5V-to-24V DC converter supplies the PIN diode bias. See
  [[pin-diode-antenna-switching]].
- **Rack antennas:** each of 2 tournament racks has its own antenna and switch, sharing the PIN
  diode switching mechanism, connected to the controller board by shielded cable and 2.5 mm jack.
  Tile arrangement within a rack is not resolved, only presence.
- **Controller board:** Arduino Pro Micro (16 MHz), carries the reader IC, rack switches, and
  connectors to the racks and board antenna array. Schematic shows an unimplemented flash IC and
  an unimplemented DGT3000 chess-clock connection.
- **PCBs:** four boards total, laid out in Sprint Layout 6.0 (Abacom): controller board, board
  antenna array (components on the underside for a flat playing surface), a later
  cable-to-antenna adapter board (adds a Molex-style connector and a placeholder for an
  electronic compass to sense board rotation), and the rack antenna.
- **Software / detection method:** [[bitwiseid-method|BitwiseID]], reading a whole row or column
  of tags in one operation instead of one tile at a time. Measured 0.35 s response time, flat up
  to 225 tiles.
- **Geometry tolerance:** antennas are only meant to see tags directly above the board surface,
  not tags beyond the antenna outline; this requirement tolerates imprecise tuning and long
  antenna feed lines.

## Sources

- [[nfcgameboard-home]]
- [[nfcgameboard-schematics]]
- [[nfcgameboard-pcb]]
- [[nfcgameboard-software]]

## Related

- [[ben-bulsink]]
- [[clrc632]]
- [[bitwiseid-method]]
- [[bitwisexy-method]]
- [[row-column-antenna-matrix-technique]]
- [[pin-diode-antenna-switching]]
