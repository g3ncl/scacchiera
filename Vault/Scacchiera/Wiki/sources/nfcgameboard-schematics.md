---
type: source-summary
date_updated: 2026-07-24
tags:
  - wiki/source
---

# Source: NFC Game Board schematics page

Raw clipping: [Clippings/nfcgameboard.com/schematics.md](../../Clippings/nfcgameboard.com/schematics.md). [captured::2026-07-24] [author::[[ben-bulsink]]]

Describes four sPlan-8 schematic sheets (Abacom sPlan tool) covering the reader, the
microprocessor board, the 15x15 antenna grid, and the rack antenna/switches. Raw downloads
captured locally: SPlan-8 source files, PDF renders of each sheet, and a zip of component
datasheets (CLRC632 x2, BAR64 dual PIN diode, 74HC164 shift register, XP ISE0524A 24 V DC-DC
converter, PDTC143 NPN transistor).

Key facts:

- Reader: [[clrc632|CLRC632]], non-symmetrical antenna drive, tuning done experimentally. A 5V to
  24V DC converter powers the PIN diode antenna switches.
- Microprocessor: Arduino Pro Micro, 16 MHz, integrated USB. Unimplemented options on the
  schematic: a flash memory IC and a DGT3000 chess-clock connector.
- Antenna grid: 15 rows + 15 columns = 30 antennas, multiplexed with
  [[pin-diode-antenna-switching|PIN diode switches]] because parallel analog-switch capacitance
  across 30 channels would detune the HF tank (author's own estimate: ~10 pF/switch x 30 = ~300
  pF, too much). Geometry only needs to reject tags outside each antenna's own footprint, which
  tolerates bad tuning and long feed lines.
- Rack antennas: 2 racks (current tournament version), same PIN diode switching mechanism,
  presence-only (arrangement of tiles within a rack is not resolved).

## Sources used

- [[nfcgameboard-schematics]] (this page)

## Pages touched

- [[ben-bulsink]]
- [[nfc-game-board-project]]
- [[clrc632]]
- [[pin-diode-antenna-switching]]
- [[row-column-antenna-matrix-technique]]
