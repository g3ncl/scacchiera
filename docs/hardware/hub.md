# Hub board

The board that thinks and powers: WiFi MCU, ISO 15693 reader, battery power path, and every
harness connector. It lives in the service volume under one 50 mm player rail
([functional/physical.md](../functional/physical.md)) and serves the whole of
[functional/gameplay.md](../functional/gameplay.md) and
[functional/interface.md](../functional/interface.md). Schematic in `hardware/pcb/hub.py`,
layout in `hardware/pcb/hub_layout.py`.

## Power

USB-C (5.1 k CC pulls, resettable fuse, ESD array) into an MCP73871 power-path charger for one
protected Li-ion cell, with a thermistor connector and a slide switch enabling battery operation
(USB power overrides it through a diode). A TPS63802 buck-boost makes 3V3 across the whole cell
range. The light bars' 5 V comes from a TPS61023 boost that true-disconnects when disabled, feeds
a TPS2553 latch-off current limiter, and drives the WS2812 data line through an AHCT buffer at
5 V logic. The charger's STAT1/LBO output gives the low-battery signal behind the functional
spec's save-and-shutdown behavior. This power tree is carried over from the previous hub
generation, which cleared ERC and review.

## MCU and slow control

ESP32-C6-MINI-1U-N4: WiFi 6 for the browser client, native USB for charging-time debug, one SPI bus
shared by the reader, both displays, and the matrix selection registers. A TCA9535 I2C expander
carries every slow signal: the matrix latch (SEL_RCLK), reader reset, display DC and reset, LED
rail enable, USB current select, charger status, LED fault, and the single button (polled, 10 k
pullup, 2-pin connector).

The pin map comes from datasheet v1.5 Table 3-1, not from the C3 module this replaced. The C6 is
pin compatible with the C3-MINI series only on power, ground, EN and UART0: most GPIO numbers
differ, and native USB moves from the C3's pins 26/27 to **pins 17/18**, while pin 21 becomes NC.
SPI sits on the FSPI-native pins (SCLK on IO6, MOSI on IO7, MISO on IO2) so the bus avoids the GPIO
matrix. I2C stays on pins 22 and 23 because IO8 and IO9 are the C6 boot strapping pins and the
4.7 k bus pullups hold them high for SPI boot, which also makes IO9 the download-mode recovery pin.
IO15 is left unused because it is the JTAG-source strapping pin.

C27 (10 uF) and C28 (100 nF) decouple the module locally at pin 3: WiFi TX peaks at 382 mA
(Table 6-4) and the regulator's own output capacitors are centimetres away. TP1, TP2 and TP3 expose
IO9, EN and ground, because the single button sits behind the polled expander and cannot hold IO9
low at reset; shorting TP1 to TP3 and pulsing TP2 forces joint download boot if firmware ever
breaks the USB peripheral.

The module carries an external antenna connector rather than a PCB antenna, which keeps it at
12.5 mm and needs no copper keepout. The antenna itself is a purchased accessory, not a board part:
see [boards.md](boards.md). Its connector is **MHF3 / W.FL / IPEX3**, not U.FL.

## Reader

PN5180. ISO/IEC 15693 is the protocol the BitwiseID whole-line reads are proven on, and the NFC
Game Board author measured the PN5180 matching the CLRC632's inventory timings, so it de-risks
both the matrix scan rate and the firmware. It shares SPI with NSS, BUSY, and IRQ on MCU pins and
reset on the expander. Internal 1.8 V LDO tied to AVDD/DVDD, everything else on 3V3 (TVDD at 3V3
trades field strength the 3 mm read budget does not need for one less rail).

Y1 is a TXC 7M27100009, 27.12 MHz in a 3225 package. 27.12 divided by two is the 13.56 MHz carrier,
so the value is fixed by the protocol, and the ESP32 module's own 40 MHz crystal cannot serve it.
Every value clears the reader's Table 142: 10 pF load against 10 pF typ, 60 ohm ESR against 100 ohm
max, +/-10 ppm and +/-15 ppm over temperature against +/-100 ppm. C31 and C32 are 15 pF, not the
10 pF used before: two equal caps present C/2 plus stray, so 15 pF lands near the required 10 pF
while 10 pF presented only 8 pF and spent about 41 ppm of the budget on load error alone. The 3225
package replaced a 2016 part JLCPCB could not stock, and its larger pads are also reworkable.

TX1 drives the single-ended matrix bus through a 470 nH / 220 pF EMC low-pass and a 68 pF series
match with a DNP trim; TX2 carries the mirrored EMC filter into ground so the push-pull driver
stays balanced. RX taps the bus through 100 pF and 1 k into RXP, with RXN referenced to VMID.

## Interfaces

All JST GH except the JST PH battery pair: the 7-pin matrix link (RF bus between grounds, 3V3,
serial selection), two 7-pin display connectors (3V3 SPI plus DC and reset), two 4-pin light bar
connectors chained through LED_RETURN, a 4-pin UART service connector, and the 2-pin button.

## Board

110 x 46 mm, 2 layers, in the service volume under one player rail. Components are placed
deterministically by functional zone (USB and charging, rails, MCU and expander, reader and its
front end, edge connectors). Normal builds import the reviewed route in
`hardware/pcb/routes/hub.ses`; `make pcb-hub-reroute` is the explicit command for producing a new
Freerouting candidate. The USB shield tabs and recovery pads have deterministic routes, the
TPS63802 and PN5180 exposed pads are grounded, and both-face ground pours are filled afterward.
`make pcb-hub-drc` checks schematic parity and is clean: 0 violations, 0 unconnected, 0 parity
issues.

## Mounting

Four M2.5 plated holes (H1 to H4), 4.0 mm in from each corner, bonded to ground so the enclosure
screws tie the shell to the pours rather than leaving it floating.

## Validation

`hardware/tests/test_sim_hub.py` drives the full 16-cell matrix bus subckt through the TX path
exactly as wired here and checks [criteria.yaml](criteria.yaml): the selected loop's field peaks
at 13.86 MHz (in band, trim pulls it to the carrier) at 60 mA of coil current per volt of drive.
The 68 pF match value came from this bench; 220 pF would drag the system to 9 MHz.

## Cost

Generated engineering BOM (`hardware/pcb/generated/hub/hub_engineering_bom.csv`) totals 16.21 EUR in parts against the
30 EUR board target in [boards.md](boards.md).

Seven Extended lines go to JLCPCB, all of them genuinely reflow-only: J1 (USB-C), U1, U2, U3, U5,
U4 and Y1. Everything else Extended is hand-fitted from `hub_hand_bom.csv`, including the 0402 C0G
RF and timing capacitors and the 0.65 mm TSSOP expander, which removes three feeder changes.
