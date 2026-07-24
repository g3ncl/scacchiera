---
title: "NFC Game Board - PCB"
source: https://nfcgameboard.com/pcb/
author: Ben Bulsink
captured: 2026-07-24
tags:
  - clipping
---

# PCB

Four printed circuit boards are used. The layouts are generated using (the cheap but oh so friendly, my favorite) SPrint Layout 6.0 of Abacom. See [Sprint Layout 6.0, ELECTRONIC-SOFTWARE-SHOP](https://www.electronic-software-shop.com/lng/en/electronic-software/sprint-layout-60.html). A free viewer for the design files can be downloaded at Abacom too.

[Download the Sprint Layout 6.0 PCB design files](https://nfcgameboard.com/wp-content/uploads/2026/05/NFC-Game-Board-PCB.zip) — local copy: [files/pcb-layouts/](files/pcb-layouts/)

The four design files are shortly discussed here (click on each title for viewing a .pdf version of the PCB design):

[Controller board](https://nfcgameboard.com/wp-content/uploads/2022/10/Scrabble-controller-board-PCB.pdf) — local copy: [files/Scrabble-controller-board-PCB.pdf](files/Scrabble-controller-board-PCB.pdf)

The controller board carries the Arduino Pro Micro, the RFID reader IC, the rack switches and connectors to the racks and the board antenna array.

[Board antenna array](https://nfcgameboard.com/wp-content/uploads/2022/10/Scrabble-board-antenna-PCB.pdf) — local copy: [files/Scrabble-board-antenna-PCB.pdf](files/Scrabble-board-antenna-PCB.pdf)

Placed underneath the playing surface of the board, this PCB forms the row and column antennas, and contains the 30 antenna switches. The board is used with components at the down side, to allow a flat playing surface.

[Cable to antenna adapter board](https://nfcgameboard.com/wp-content/uploads/2026/05/Cable-to-antenna-adapter.pdf) — local copy: [files/Cable-to-antenna-adapter.pdf](files/Cable-to-antenna-adapter.pdf)

The cable to antenna adapter board is designed and added after that the antenna board was already manufactured. This adapter board allows a Molex type smd connector cable to be used, which is more comfortable than the initial soldered connection. The adapter board also has a placeholder for an electronic compass, which can be used to detect the rotation action of the board.

[Rack antenna](https://nfcgameboard.com/wp-content/uploads/2022/10/Scrabble-rack-antenna-PCB.pdf) — local copy: [files/Scrabble-rack-antenna-PCB.pdf](files/Scrabble-rack-antenna-PCB.pdf)

The racks contain a single antenna. The antenna is connected to the controller board using a shielded cable and a 2.5 mm jack plug.

---

Scrabble® is a registered trade mark of Hasbro and Mattel
Copyright © 2022-2026 Ben Bulsink | benbulsink@outlook.com | Powered by WordPress
