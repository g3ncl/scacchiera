# Display interface

The two ER-OLEDM3.12-1W player displays are purchased modules, not boards this project generates.
This file is the contract between the hub's 7-pin display connectors and each module's 16-pin
header: which conductor carries what, which module pins must be strapped, and what still has to be
decided before the harness can be ordered. See [hub.md](hub.md) for the hub side and
[boards.md](boards.md) for why the display is not a board.

## Hub side

J5 and J6, `SM07B-GHS-TB(LF)(SN)`, 7-pin JST GH at 1.25 mm, horizontal. Pin order is fixed in
`hardware/pcb/hub.py`:

| Pin | Net |
| --- | --- |
| 1 | 3V3 |
| 2 | GND |
| 3 | SCLK |
| 4 | MOSI |
| 5 | OLED*n*_CS_N |
| 6 | OLED_DC |
| 7 | OLED_RESET_N |

SCLK, MOSI, DC and RESET_N are shared by both displays; only chip select is per-module.

## Module side

**A 2 x 8 pin header on 2.54 mm pitch**, verified against section 4.1 and the outline drawing of
the manufacturer datasheet (`ER-OLEDM3.12-1W_BUYDISPLAY.pdf`, revision 1.0, 2025-08-07). Odd pins
1 to 15 on one row, even pins 2 to 16 on the other, pin 1 marked with a square pad. The pin field
is 17.78 x 2.54 mm and sits between the two mounting holes on the 33 mm edge. This is an ordinary
IDC-16 footprint, so the mating part is a stock socket rather than anything custom.

In four-wire SPI mode ten of the sixteen pins are grounded and only six carry anything:

| Module pin | Function | Connects to |
| --- | --- | --- |
| 1 | VCC | hub pin 1, 3V3 |
| 2, 3 | GND | hub pin 2, GND |
| 4 | RES | hub pin 7, OLED_RESET_N |
| 5 | CS | hub pin 5, OLED*n*_CS_N |
| 6 | D/C | hub pin 6, OLED_DC |
| 7 | R/W, **must** be VSS in serial mode | GND, strapped locally |
| 8 | E/RD, **must** be VSS in serial mode | GND, strapped locally |
| 9 | D0 / SCLK | hub pin 3, SCLK |
| 10 | D1 / SID | hub pin 4, MOSI |
| 11 to 16 | D2 to D7, unused, *recommended* low | GND, strapped locally |

Section 4.1 is explicit that pins 7 and 8 must be tied to VSS when the serial interface is
selected, while pins 11 to 16 are only recommended to tie low. Both are grounded here; leaving
unused CMOS inputs floating in a battery product is not worth the saved copper.

Six signals plus ground is exactly seven conductors, which is why the hub connector is 7-pin. The
cable is not a straight-through: eight module pins (7, 8, 11 to 16) have no hub conductor and must
be tied to ground at the display end, and module pins 2 and 3 share the single ground conductor.

## How the straps are made: on the module, not on a new board

The ten grounds are commoned with a solder bridge on the display module's own header, on the
solder side where it does not interfere with mating. No adapter board.

The pin layout makes this easy, because the grounded pins are clustered rather than scattered:

| Column | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Odd row | 1 VCC | **3 GND** | 5 CS | **7 GND** | 9 SCLK | **11 GND** | **13 GND** | **15 GND** |
| Even row | **2 GND** | 4 RES | 6 D/C | **8 GND** | 10 SID | **12 GND** | **14 GND** | **16 GND** |

Columns 6 to 8 are ground on both rows, a solid two-by-three block at one end. Column 4 is ground
on both rows. That is one bridge across six adjacent pins, one across two, and a link wire to
pins 2 and 3. Per display, twice.

An adapter PCB was designed for this and then discarded as over-built: commoning ten adjacent pins
is a soldering job, not a routing job. It stays documented below only as a fallback.

### First, find out whether any of this is needed

The strap list above assumes the module does nothing for itself, and that assumption is not
verified. The interface-select jumpers on the module's back (R3/R9, R5/R8, R10/R11/R12) plausibly
already drive R/W and E/RD low when four-wire SPI is selected, since that is what selecting the
mode means. If they do, the required list collapses, and pins 11 to 16 are only *recommended* low
rather than mandatory.

| If the jumpers... | Work needed |
| --- | --- |
| handle 7 and 8, and D2 to D7 may float | none |
| handle 7 and 8, and D2 to D7 are tied low anyway | one bridge, columns 6 to 8 |
| do not handle 7 and 8 | two bridges plus a link wire |
| do something unexpected | the fallback adapter below |

All four are settled by the same EastRising interfacing document that settles mode selection.
Nothing should be fabricated before reading it.

### Fallback: the adapter board, if the module needs more than a bridge

28 x 22 mm, two layers, 1.0 mm, no active components, snapped off the panel that already carries
both light bars and the power board. J1 is a 2 x 8 socket receiving the display header, pin 1 at
the right-hand end; J2 is the `SM07B-GHS-TB(LF)(SN)` used everywhere else on this product, below
it with pin 1 at the left.

With those orientations five of the six signals fan out in monotonically increasing order and
cannot cross, so they share the front layer:

| Net | J2 pin | J1 pin | Row |
| --- | --- | --- | --- |
| SCLK | 3 | 9 | far |
| MOSI | 4 | 10 | near |
| CS_N | 5 | 5 | far |
| OLED_DC | 6 | 6 | near |
| RESET_N | 7 | 4 | near |

The two far-row nets pass through the 1.27 mm gap beside a near-row pad: 1.7 mm pads on 2.54 mm
pitch leave 0.295 mm to a 0.25 mm track, clearing the 0.2 mm rule. 3V3 is the exception, sitting at
one end of the GH and the far end of the display header, so it takes the back layer alone and runs
out past the right-hand end of the pin field. Ground pours on both layers and reaches all ten
grounded pins through their own barrels, so the board needs no vias.

Two further alternatives were considered and rejected outright. Merging into the light bar board is
physically impossible: it is 120 x 8.5 mm with every component on the front face behind a diffuser
and only 2.15 mm of free length. Widening the hub connectors to 2 x 8 for a stock IDC ribbon is
attractive but adds about 19 mm of hub edge and forces a re-route of a two-layer board that already
had to buy length to converge.

## Before the harness can be ordered

- **The module's interface-select configuration is not documented anywhere in the datasheet.**
  Section 4.1 describes what each pin does "when serial interface mode is selected" but never says
  how to select it. The outline drawing's back view shows the mechanism: paired resistor positions
  R3/R9, R5/R8 and the R10/R11/R12 group are 0-ohm selection jumpers. Which combination selects
  four-wire SPI, and which combination the module ships in, must come from EastRising's separate
  interfacing document (the datasheet's own Attention note points at it) or from the supplier
  directly. The adapter cannot fix this: if the modules arrive strapped for parallel or I2C they
  need rework before they will talk to the hub at all.
- The datasheet is revision 1.0, **preliminary**, dated 2025-08-07. V1 treats a provisional
  document as a release blocker regardless of what it says.
- **The 2 x 8 socket is not bound.** The footprint is a stock
  `Connector_PinSocket_2.54mm:PinSocket_2x08_P2.54mm_Vertical` (1.7 mm pads, 1.0 mm drill), but no
  MPN, order code or datasheet is filed, so the adapter's schematic cannot be generated: the
  build fails any fitted part without a manufacturer number, which is the intended behaviour.
  Binding it is an ordinary Datasheets-workflow job and the only thing standing between this
  design and a routed board.
