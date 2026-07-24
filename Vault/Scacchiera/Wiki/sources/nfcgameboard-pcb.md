---
type: source-summary
date_updated: 2026-07-24
tags:
  - wiki/source
---

# Source: NFC Game Board — PCB page

Raw clipping: [Clippings/nfcgameboard.com/pcb.md](../../Clippings/nfcgameboard.com/pcb.md). [captured::2026-07-24] [author::[[ben-bulsink]]]

Describes four PCBs laid out in Sprint Layout 6.0 (Abacom): controller board, board antenna
array, cable-to-antenna adapter board, and rack antenna. Raw downloads captured locally: the
Sprint Layout 6.0 design files (`.lay6`) and a standalone PDF render of each board.

- **Controller board:** carries the Arduino Pro Micro, the reader IC, the rack switches, and
  connectors to both the racks and the board antenna array.
- **Board antenna array:** mounted under the playing surface, forms the row and column antennas
  plus the 30 antenna switches; populated on the underside so the top stays flat.
- **Cable-to-antenna adapter board:** added after the antenna board was already built, to swap a
  soldered connection for a Molex-style SMD connector cable; also carries an unpopulated
  placeholder for an electronic compass to sense board rotation.
- **Rack antenna:** single antenna per rack, wired to the controller board with shielded cable and
  a 2.5 mm jack plug.

## Sources used

- [[nfcgameboard-pcb]] (this page)

## Pages touched

- [[nfc-game-board-project]]
