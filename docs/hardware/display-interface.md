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

### Confirmed by the manufacturer's own ESP32 example

EastRising's `ER-OLEDM3.12-1_ESP32_Tutorial`, captured 2026-08-02 in
`Vault/Scacchiera/Clippings/buydisplay/`, ships working four-wire SPI code for an ESP32 and states
its wiring in the sketch header:

```
*1. VDD -> 3.3   *2,3,7,8,12-16. GND -> GND   *4. RES -> 8
*5. CS  -> 10    *6. DC -> 9                  *9. SCL -> SCK   *10. SDI -> MOSI
```

**That is this contract's pin map exactly**, and it is the first evidence for it that comes from
the manufacturer rather than from reading the pin table. It also confirms the straps are real work:
the vendor grounds pins 7 and 8 externally too, so the interface-select jumpers do **not** do it for
you.

One difference, and this design keeps its own choice. The vendor grounds nine pins and omits
**pin 11 (D2)**; this contract grounds ten. Section 4.1 recommends tying every unused D0 to D7 pin
low, and D2 is unused in serial mode, so grounding it is datasheet-compliant and the more
conservative reading. The likely reason for the vendor's omission is that D2 carries an I2C role
(tied to D1 as SDAout/SDAin), which does not apply here. Leaving a CMOS input floating next to a
switching bus is the failure this avoids.

### How the interface is actually selected: BS[2:0]

**This was in the vault all along, in the wrong document.** The module datasheet documents no way to
select an interface, which is what the open V1 item recorded. The *controller* datasheet does, and
it has been filed since 2026-07-30. `Datasheets/SSD1362_SOLOMON.pdf` revision 1.0, Table 6-2:

| BS[2:0] | Interface |
| --- | --- |
| **000** | **4-wire SPI** |
| 001 | 3-wire SPI |
| 110 | 8-bit 8080 parallel |
| 100 | 8-bit 6800 parallel |
| 010 | I2C |

`0` means the pin is tied to VSS and `1` to VDDIO. **Four-wire SPI is BS2, BS1 and BS0 all tied
low**, and the module's default 8080 parallel is `110`, so converting one means moving BS2 and BS1
from VDDIO to VSS. That is precisely what the R3/R9, R5/R8 and R10/R11/R12 jumper pairs on the
module's back do; the module datasheet just never says so.

The same document's Table 7-1 settles the strap list independently of EastRising's example, and
it **confirms this contract against the vendor's own tutorial**: in the 4-wire SPI row, D7 through
**D2** are all "Tie LOW", with D1 as SDIN and D0 as SCLK, and E and R/W# tied low. So grounding
module pin 11 is required by the controller datasheet, not merely recommended, and the vendor
tutorial's nine-pin ground list is the one that is short.

One firmware consequence, recorded here because it is easy to discover late: section 7.1.3 states
that **under serial mode only write operations are allowed.** There is no register readback over
SPI, so nothing in the driver may depend on reading the controller.

### What is settled, and what is not

**Settled: the module must not be reworked into SPI, so the interface has to be an order-time
selection.** Module datasheet section 7.3 is explicit: *"Do not damage or modify the pattern writing
on the printed circuit board"* and *"Except for soldering the interface, do not make any alterations
or modifications with a soldering iron."* Moving the BS straps is exactly that kind of alteration,
so the earlier plan of inspecting and re-strapping them on arrival is **withdrawn**: it is outside
the manufacturer's handling instructions and inside the warranty exclusion in 7.7.

**Not settled: which strap state a shipped module actually has.** The product listing says the
module is *"8080 8-bit Parallel interface with no pin header connection by default"*. So the
question to put to EastRising is now a precise, checkable purchasing one rather than a vague
technical one:

> Supply ER-OLEDM3.12-1W configured for **four-wire SPI, BS[2:0] = 000**.

A module strapped `110` will not talk to the hub, and per 7.3 it cannot legitimately be converted
after delivery.

**Also worth knowing before assembly:** "no pin header connection by default" means the 2 x 8 header
is very likely not fitted. That suits this design, because the strap work below is easier on bare
plated holes than on a mated header, but it means the header is the builder's part. Section 7.5
fixes how to solder it: **280 +/- 10 degrees C, 3 to 4 seconds, eutectic solder**, and the panel and
board must not be detached more than three times.

### The strap list assumed the module does nothing for itself

That assumption is now confirmed correct by the vendor's own wiring above, which grounds 7 and 8
externally. The table below is kept as the reasoning that got there.

| If the jumpers... | Work needed |
| --- | --- |
| handle 7 and 8, and D2 to D7 may float | none |
| handle 7 and 8, and D2 to D7 are tied low anyway | one bridge, columns 6 to 8 |
| do not handle 7 and 8 | two bridges plus a link wire |
| do something unexpected | the fallback adapter below |

All four are settled by the same EastRising interfacing document that settles mode selection.
Rather than wait on it, the design proceeds on assumptions A2 and A3 in
[assumptions.md](assumptions.md): the modules ship strapped for four-wire SPI, as BuyDisplay sells
and documents them, and pins 7 and 8 are grounded externally anyway because section 4.1 says they
must be and the bridge is harmless if redundant. Both fail loudly at first bring-up rather than
silently in the field, which is what makes them acceptable to assume.

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

## Carried as assumptions, not blockers

Three things the module datasheet does not settle. All three are registered in
[assumptions.md](assumptions.md) and carried rather than chased, so that display work proceeds.

- **Which strap state a shipped module has.** The mechanism itself is documented, just not in the
  module's own datasheet: SSD1362 Table 6-2 fixes BS[2:0] = 000 for four-wire SPI, and the paired
  0-ohm jumpers R3/R9, R5/R8 and R10/R11/R12 on the module's back are what set those pins.
  Assumption A2 takes the modules as shipping strapped for four-wire SPI, which is how BuyDisplay
  sells and documents them, while the product listing says the default is 8080 parallel. If it is
  wrong the display is silent at bring-up, and the remedy is a replacement module rather than
  rework, because section 7.3 forbids modifying the board and 7.7 excludes it from warranty. Hence
  the order-time condition above. No board change either way.
- **The datasheet is revision 1.0, preliminary**, dated 2025-08-07. Assumption A4 takes its numbers
  as holding, which its independently corroborated 320 mA supports.
- **The 2 x 8 socket is unbound.** This only matters for the fallback adapter, which is not being
  built. The footprint is a stock
  `Connector_PinSocket_2.54mm:PinSocket_2x08_P2.54mm_Vertical` if it ever is.
