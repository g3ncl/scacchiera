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

ESP32-C3-MINI-1U: WiFi for the browser client, native USB for charging-time debug, one SPI bus
shared by the reader, both displays, and the matrix selection registers. A TCA9535 I2C expander
carries every slow signal: the matrix latch (SEL_RCLK), reader reset, display DC and reset, LED
rail enable, USB current select, charger status, LED fault, and the single button (polled, 10 k
pullup, 2-pin connector). The boot-strapping pin carries a pulled-up display chip select, per the
previous generation's reviewed pin map.

## Reader

PN5180. ISO/IEC 15693 is the protocol the BitwiseID whole-line reads are proven on, and the NFC
Game Board author measured the PN5180 matching the CLRC632's inventory timings, so it de-risks
both the matrix scan rate and the firmware. It shares SPI with NSS, BUSY, and IRQ on MCU pins and
reset on the expander. 27.12 MHz crystal, internal 1.8 V LDO tied to AVDD/DVDD, everything else
on 3V3 (TVDD at 3V3 trades field strength the 3 mm read budget does not need for one less rail).

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
front end, edge connectors); track routing is autorouted by Freerouting (`make pcb-hub-route`)
with both-face ground pours added afterward. Freerouting leaves a few pads open in the dense
PN5180 QFN and USB-C areas that vary run to run, so a post-route step bridges any still-open pad
to its net's nearest routed copper. `make pcb-hub-drc` is clean: 0 violations, 0 unconnected.

## Validation

`hardware/tests/test_sim_hub.py` drives the full 16-cell matrix bus subckt through the TX path
exactly as wired here and checks [criteria.yaml](criteria.yaml): the selected loop's field peaks
at 13.86 MHz (in band, trim pulls it to the carrier) at 60 mA of coil current per volt of drive.
The 68 pF match value came from this bench; 220 pF would drag the system to 9 MHz.

## Cost

Generated BOM (`hardware/pcb/generated/hub/hub_bom.csv`) totals 14.94 EUR in parts against the
30 EUR board target in [boards.md](boards.md).
