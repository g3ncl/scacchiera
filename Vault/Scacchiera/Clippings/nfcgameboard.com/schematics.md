---
title: "NFC Game Board - Schematics"
source: https://nfcgameboard.com/schematics/
author: Ben Bulsink
captured: 2026-07-24
tags:
  - clipping
---

# Schematics

The schematics are drawn in four separate pages. Drawn using the sPlan tool of Abacom [sPlan 8.0, ELECTRONIC-SOFTWARE-SHOP](https://www.electronic-software-shop.com/lng/en/electronic-software/splan-80.html). A free demo version of this editor is also available.

- [Download the schematics in SPlan-8 format](https://nfcgameboard.com/wp-content/uploads/2026/05/NFC-Game-Board-schematics-SPlans.zip) — local copy: [files/schematics-splan/](files/schematics-splan/)
- [Download the schematics in .pdf format](https://nfcgameboard.com/wp-content/uploads/2026/05/NFC-Game-Board-.pdf.zip) — local copy: [files/schematics-pdf/](files/schematics-pdf/)
- [Download data sheets of components](https://nfcgameboard.com/wp-content/uploads/2026/05/Data-sheets.zip) — local copy: [files/datasheets/](files/datasheets/)

**The reader**

I have chosen the CLRC632 RFID reader. It is an older IC, bulky and more expensive, but well documented. Modern redesigns could also use other IC's that support the ISO/IEC 15693 protocol.
In this schematic, you see a standard configuration, however with non-symmetrical driving of the antennas. The tuning is done by experiments. The schematic also shows a 5V to 24V DC converter, needed for the antenna switches.

**The microprocessor board**

The Scrabble board is controlled by software on an Arduino Pro Micro 16 MHz module. This module is compact, and features an integrated USB connection. The schematic shows an optional Flash memory IC (not implemented currently) and a connection for a DGT3000 electronic chess clock (not implemented currently).

**The 15 x 15 antenna grid**

Each row and each column of the board has a RFID antenna structure underneath it. These 30 antennas are multiplexed by use of PIN diode switches. Why PIN diodes? All analog switch IC's that I found, even the quite expensive ones, show significant capacitances on the switched signal. When 30 switches are put in parallel, even a capacitance of 10 pF sums up to 300 pF, way too much for this HF system. PIN diodes show sub-pF capacitance when put in reverse, non-conducting mode. A 5V to 24V DC converter delivers the voltage for putting the PIN diodes in forward or backward configuration, the higher the voltage, the lower the capacitance, and in this schematic, the lower the forward resistance.
On the antennas: It is desired that the antennas only detect tags that are just above the surface of the board, and not the tags that are outside the outline of the antennas. Happily this condition allows a bad tuning and long feeding lines of the antennas.

**The Rack antenna and switches**

Each rack (in the current tournament version only 2) contains an antenna, which can identify which tiles are on the rack. The antennas are switched by the same mechanism as the board antennas. The arrangement of tiles on the rack is not identified. That would be a great feature, showing the thoughts of the player, but needs a multi-antenna system per rack, too complicated for the moment.

---

Scrabble® is a registered trade mark of Hasbro and Mattel
Copyright © 2022-2026 Ben Bulsink | benbulsink@outlook.com | Powered by WordPress
