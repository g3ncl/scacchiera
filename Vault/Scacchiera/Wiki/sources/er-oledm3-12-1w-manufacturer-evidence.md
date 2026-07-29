---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-29
source_file: "Datasheets/ER-OLEDM3.12-1W_BUYDISPLAY.md"
source_title: "ER-OLEDM3.12-1W manufacturer evidence"
publisher: "EastRising"
---

# ER-OLEDM3.12-1W manufacturer evidence

This source records the exact [[er-oledm3-12-1w]] display module fixed by the functional
specification. It is a 100 by 33 mm SSD1362 module with four-wire SPI support and a 3.0 to 3.5 V
logic supply. The 16-pin header exposes VCC, two grounds, reset, chip select, data/command, serial
clock and serial data; pins required low in serial mode also need a defined harness or module strap.

[mpn::ER-OLEDM3.12-1W] [supplier::BuyDisplay] [interface::four-wire SPI]

## Electrical conflict

Datasheet section 4.3 specifies 320 mA maximum at 3.3 V with the entire display active and 2 mA
maximum in sleep. The product page instead labels 2 mA as the module maximum. The load budget uses
320 mA per display. The contradiction, missing original PDF file and exact 16-to-7-pin interconnect
keep V1 open.
