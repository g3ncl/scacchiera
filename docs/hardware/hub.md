# Hub board

The board that thinks and distributes power: WiFi MCU, ISO 15693 reader, regulated 5 V input,
and every harness connector. It lives in the service volume under one 50 mm player rail
([functional/physical.md](../functional/physical.md)) and serves the whole of
[functional/gameplay.md](../functional/gameplay.md) and
[functional/interface.md](../functional/interface.md). Schematic in `hardware/pcb/hub.py`,
layout in `hardware/pcb/hub_layout.py`.

## Power

The hub receives regulated 5 V from the purchased PiSugar 3 Plus described in
[power-subsystem.md](power-subsystem.md). PiSugar owns the cell, charger, battery protection,
5 V conversion, charging connector, UPS handover, and battery telemetry. The custom hub contains no
raw-cell connection and no USB charging circuit.

One buck converter makes 3.3 V for the MCU, reader, displays, and matrix. The exact converter remains
an open V1 selection. The light bars use the managed 5 V rail directly through the TPS2553
latch-off current limiter, with their data driven through an AHCT buffer at 5 V logic. This removes
the former TPS61023 boost and its duplicate energy conversion.

PiSugar shares I2C with the hub and reports source presence, battery voltage, estimated percentage,
and control state. A separate cell-contact sensor and hardware interlock must disable charging
outside 0 to 40 degrees Celsius because PiSugar reports charger-chip temperature rather than cell
temperature. Until that interlock and its fail-safe behavior pass V1 through V8, the power system
is not release-ready.

## MCU and slow control

ESP32-C6-MINI-1U-N4: WiFi 6 for the browser client, native USB on a service-only interface, one SPI bus
shared by the reader, both displays, and the matrix selection registers. A TCA9535 I2C expander
carries every slow signal: the matrix latch (SEL_RCLK), reader reset, display DC and reset, LED
rail enable, LED fault, and the single button (polled, 10 k pullup, 2-pin connector). PiSugar
telemetry and control remain directly on I2C rather than consuming expander pins.

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

All low-voltage harnesses use locking connectors: the 7-pin matrix link (RF bus between grounds,
3V3, serial selection), two 7-pin display connectors (3V3 SPI plus DC and reset), two 4-pin light
bar connectors chained through LED_RETURN, the PiSugar 5 V and I2C link, a 4-pin UART service
connector, and the 2-pin button. There is no battery connector on the hub.

## Board

The target remains at most 110 x 46 mm, 2 layers, in the service volume under one player rail.
The existing placement and reviewed route belong to the superseded charger design. They are
historical evidence only until regenerated around the 5 V boundary and checked again at V2.

## Mounting

Four M2.5 plated holes (H1 to H4), 4.0 mm in from each corner, bonded to ground so the enclosure
screws tie the shell to the pours rather than leaving it floating.

## Validation

`hardware/tests/test_sim_hub.py` drives the full 16-cell matrix bus subckt through the TX path
exactly as wired here and checks [criteria.yaml](criteria.yaml): the selected loop's field peaks
at 13.86 MHz (in band, trim pulls it to the carrier) at 60 mA of coil current per volt of drive.
The 68 pF match value came from this bench; 220 pF would drag the system to 9 MHz.

## Cost

The historical generated BOM belongs to the superseded MCP73871 hub. Recalculate the custom hub
cost after the simplified schematic and route pass V1 and V2. The PiSugar 3 Plus is a separately
purchased subsystem and must be included in complete-product cost, not the JLCPCB BOM.
