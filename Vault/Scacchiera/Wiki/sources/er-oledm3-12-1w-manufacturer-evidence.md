---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-01
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

## Electrical conflict, resolved 2026-08-01

Datasheet section 4.3 specifies 320 mA maximum at 3.3 V with the entire display active and 2 mA
maximum in sleep. The product page instead labels 2 mA as the module maximum. The load budget uses
320 mA per display.

The contradiction is now resolved in favour of the datasheet: see
[[er-oledm3-12-1w-display-current]]. 2 mA at 3.3 V is 6.6 mW, which cannot run the controller, the
onboard boost and 16384 lit pixels, and an independently published table for a comparable 3.12
inch 256 by 64 panel ([[w256064-xalg-datasheet]]) works out to 312 to 331 mA equivalent at 3.3 V.
The product page publishes the sleep figure as the maximum. This is Derived evidence; the supplier
has not confirmed the error.

## Original PDF filed 2026-08-01

`Datasheets/ER-OLEDM3.12-1W_BUYDISPLAY.pdf`, 21 pages, revision 1.0 preliminary, Aug-07-2025,
downloaded by hand because the supplier's path refuses automated clients. It confirms this
capture on every point and adds three:

- Section 4.3 note 5 reads "VDD=3.3V, 100% Display Area Turn on" against the 320 mA maximum, and
  pin 1 VCC has a 3.6 V absolute maximum, so the panel's high-voltage rail is generated on-module
  and 320 mA is the whole module at 3.3 V.
- Section 4.1 makes pins 7 (R/W) and 8 (E/RD) **mandatory** to VSS in serial mode, while pins 11
  to 16 are only *recommended* low.
- The outline drawing shows the header is a **2 x 8 on 2.54 mm pitch**, a stock IDC-16 pattern.

## Still open for V1

- The datasheet revision is **1.0, preliminary**. A provisional document is a V1 release blocker
  on its own terms.
- **Interface selection is undocumented.** Every pin description is conditioned on "when serial
  interface mode is selected" and no section says how to select it. The back view shows paired
  0-ohm jumper positions R3/R9, R5/R8 and R10/R11/R12. Which combination gives four-wire SPI, and
  which the module ships in, needs EastRising's separate interfacing document.
- The mating socket and harness are unbound, though the footprint is now a stock pattern.
