# Hub board

The board that thinks and distributes power: WiFi MCU, ISO 15693 reader, regulated 5 V input,
and every harness connector. It lives in the service volume under one 50 mm player rail
([functional/physical.md](../functional/physical.md)) and serves the whole of
[functional/gameplay.md](../functional/gameplay.md) and
[functional/interface.md](../functional/interface.md). Schematic in `hardware/pcb/hub.py`,
layout in `hardware/pcb/hub_layout.py`.

## Power

The hub receives regulated 5 V from a purchased power module. Which module is a separate decision,
bounded by the contract in [power-module-interface.md](power-module-interface.md) and recorded in
[power-subsystem.md](power-subsystem.md); the hub is built against the contract, not against a
product, so the module can be swapped without touching this board. The custom hub never charges the
cell and never connects to it except through a 2 Mohm divider.

The product's power-only USB-C inlet presents passive Type-C sink resistors and accepts only a
qualified fixed 5 V/2 A adapter. AP22811AW5-7 gates that input to the module and adds current
limiting, short-circuit protection, output discharge, thermal protection, and reverse current
blocking. Its enable is the wired result of both TLV7042DGKR comparisons around a cell-bonded
NTCLE317E4103SBA sensor. A 10 kohm sensor bias, a 39k/100k cold reference, and a 300k/200k hot
reference made from existing 100k resistors produce conservative nominal trips near 4.5 and 34.5
degrees Celsius, simulated at 2.17 to 36.43 over every published tolerance corner (see Validation).
An open sensor trips cold and a shorted sensor trips hot. Firmware receives a divided sensor voltage
for reporting but has no path that can override the cutoff.

AP63203WU-7 and a 4.7 uH NR6045S4R7MT make 3.3 V from the module's managed 5 V. The fixed-output
buck uses the data sheet's 10 uF input, two 22 uF output, and 100 nF bootstrap network. The light
bars use managed 5 V directly through the TPS2553 latch-off current limiter, with their data driven
through an AHCT buffer at 5 V logic.

Both halves of the module link are seven-way, because every contact in these connector families is
rated 1.0 A and both halves carry the whole board. J2 spreads the qualified output over three
contacts, since it carries charge current and system load together while an adapter is connected;
J3 spreads the return over two.

Battery level is measured here rather than read from the module. R32 and R33 divide the cell
arriving on J3 pin 7 into IO4 (ADC1_CH4), filtered by C18. A 4.2 V cell reads 2.1 V, below the 2.5 V
the thermistor tap already presents to the same ADC, and the pair draws 2.1 uA, which is 1.5 mAh over
a month of storage. This is what lets a module with an undocumented or absent I2C map still satisfy
the product's battery reporting. Where a module does expose I2C, the hub can use it for source
presence and charge control, but nothing required by `docs/functional/` depends on it.

## MCU and slow control

ESP32-C6-MINI-1U-N4: WiFi 6 for the browser client, one SPI bus
shared by the reader, both displays, and the matrix selection registers. A TCA9535 I2C expander
carries every slow signal: the matrix latch (SEL_RCLK), reader reset, display DC and reset, LED
rail enable, LED fault, and the single button (polled, 10 k pullup, 2-pin connector). Power module
telemetry, where a module offers it, stays directly on I2C rather than consuming expander pins.

The pin map comes from datasheet v1.5 Table 3-1, not from the C3 module this replaced. The C6 is
pin compatible with the C3-MINI series only on power, ground, EN and UART0: most GPIO numbers
differ. Native USB pins 17 and 18 are unused because the external USB-C inlet is power-only.
IO2 provides ADC1_CH2 for independent cell-temperature telemetry. SPI uses nearby right-edge GPIOs
through the GPIO matrix to keep the reader route short. I2C stays on pins 22 and 23 because IO8 and
IO9 are the C6 boot strapping pins and the
4.7 k bus pullups hold them high for SPI boot, which also makes IO9 the download-mode recovery pin.
IO15 is left unused because it is the JTAG-source strapping pin.

C27 (10 uF) and C28 (100 nF) decouple the module locally at pin 3: WiFi TX peaks at 382 mA
(Table 6-4) and the regulator's own output capacitors are centimetres away. TP1, TP2 and TP3 expose
IO9, EN and ground, because the single button sits behind the polled expander and cannot hold IO9
low at reset; shorting TP1 to TP3 and pulsing TP2 forces joint download boot for recovery through
the UART service connector.

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
bar connectors chained through LED_RETURN, a 7-pin qualified 5 V output to the power module, a
7-pin module return carrying 5 V, optional I2C and the cell tap, the 2-pin cell thermistor, a 4-pin
UART service connector, and the 2-pin button. The cell itself never lands on this board.

## Board

The board is 162 x 46 mm, 1.0 mm thick, two copper layers. Every board in the product is now two
layers. The length buys the layer count: the service volume is a 310 mm player rail with only the
hub in it, so 162 mm costs nothing mechanically, while a four-layer panel costs a multiple of a
two-layer one at every fab. Width stays at 46 mm because that is what fits under a 50 mm rail.

Placement follows the signal path from USB input and temperature gate, through managed rails and
control, to the NFC front end and edge connectors. Functional zones slide along the board by fixed
amounts, so the crossings between clusters open while the geometry inside a cluster is untouched:
decoupling stays beside the pin it serves.

The back copper is reserved under the reader's match and the run to the matrix connector, where the
13.56 MHz return flows: no tracks, vias allowed, and the routed board has zero signal segments
inside it. The reserve starts clear of the reader itself, because a QFN-40 in a 6 mm body needs both
faces to escape its pins. Elsewhere B.Cu carries 256 signal segments against 819 on F.Cu.

The reviewed Specctra session is versioned, with the 2 A USB entry, the safety-window VBUS
distribution and its reference branch, and the USB shield owned deterministically by code.
`make pcb-hub-drc` reproduces 0 violations, 0 unconnected items, and 0 schematic-parity issues. The
fabrication export reads the stack from the board, so a later layer-count change cannot ship a
Gerber set missing copper.

## Mounting

Four M2.5 plated holes (H1 to H4), 4.0 mm in from each corner, bonded to ground so the enclosure
screws tie the shell to the pours rather than leaving it floating.

## Validation

`hardware/tests/test_sim_hub.py` drives the full 16-cell matrix bus subckt through the TX path
exactly as wired here and checks [criteria.yaml](criteria.yaml): the selected loop's field peaks
at 13.86 MHz (in band, trim pulls it to the carrier) at 60 mA of coil current per volt of drive.
The 68 pF match value came from this bench; 220 pF would drag the system to 9 MHz.

`hardware/tests/test_sim_interlock.py` sweeps the charge gate over 384 corners: both extremes of
every 1% resistor group, 4.5 to 5.5 V input, and the comparator's full published error (8 mV offset
plus 25 mV hysteresis) in each direction. The sensor is the filed Vishay R/T curve for this bead's
ceramic, which reproduces both resistances the part data sheet publishes; a single-beta fit would
have been optimistic by 0.8 K at 0 degrees, most of the cold margin. Results, with the sensor's own
published accuracy added on top:

| Quantity | Simulated | Limit |
| --- | --- | --- |
| Widest permitted window | 2.17 to 36.43 degrees Celsius | inside 0 to 40 |
| Narrowest permitted window | 6.87 to 32.48 degrees Celsius | covers 20 to 25 |
| Enable level, gate permitting | 4.40 V | at least 1.5 V |
| Enable level, gate inhibiting | 6.3 mV | at most 0.5 V |
| Enable level, sensor open or shorted | 6.3 mV | at most 0.5 V |

`hardware/tests/test_sim_led_rail.py` measures the light-bar rail's current limit on TI's own
transient model for the TPS2553, over both extremes of the 1% programming resistor and the module's
4.5 to 5.5 V output. The 39 k value had only the data sheet's IOS formula behind it, which is not
release evidence:

| Quantity | Simulated | Limit |
| --- | --- | --- |
| Both bars at full white | 444 mA at 4.459 V | must not trip; bars draw 448 mA |
| Clamp into a short | 657 to 670 mA | at most 1.0 A, the harness contact rating |

The model agrees with the formula it replaces to within one percent (668 mA computed, 664 mA
simulated at nominal), and the spread it shows is resistor tolerance only. The data sheet's own
609 to 734 mA process spread stays the worst case, and both criteria are written against that
rather than against the model.

Filing that model turned up a contradiction worth recording: TI's PSpice model enables on EN low,
while TI's data sheet for this part states EN is active high and that the -1 suffix selects latch-off,
not an inverted enable. The data sheet governs; the schematic follows it, with a 100 k pull-down that
leaves the rail dark until firmware asserts it. `hardware/sim/models/tps2553.lib` inverts in one
place and says why.

`hardware/tests/test_sim_buck.py` covers the 3.3 V power stage over 72 corners: loads from 0.2 A to
the converter's rated 2 A, 4.5 to 5.5 V in, the inductor across its 20 percent tolerance, and output
capacitance at nominal and at half of nominal.

| Quantity | Worst corner | Limit |
| --- | --- | --- |
| Output ripple | 3.59 mV pk-pk | 50 mV, from the MCU's 3.0 to 3.6 V supply range |
| Inductor peak current | 2.141 A | 2.5 A, the converter's lowest guaranteed peak limit |
| Inductor RMS current | 2.015 A | 3.30 A, the inductor's rated current |
| Inductor conduction loss | 138 mW | reported, not limited |

The peak-current margin is 14 percent, and it is smallest at the converter's own 2 A rating rather
than at anything this board draws. Saturation is never the binding limit: the converter's current
limit arrives first, at 2.5 A against the inductor's 4.97 A.

This is a power-stage result, not a control-loop one. Diodes publishes no model, so
`hardware/sim/models/ap63203.lib` is a datasheet-bounded substitute that runs open loop at a duty
computed per corner, and it deliberately contains no compensation, no soft start and no light-load
pulse-frequency mode. Regulation, transient response and stability stay data sheet claims that V8
measures. The DC output this bench reports (3.228 to 3.300 V) is an artifact of open loop, since the
real part senses after the inductor and corrects its resistance drop.

The gated input switch is checked by arithmetic rather than simulation, in
`hardware/tests/test_charge_path.py`. It is a resistor with a current limit, so its steady state is
Ohm's law on data sheet values and a SPICE bench would restate that with more ceremony and no more
confidence. At the 2 A a compliant source delivers it drops 130 mV, and its guaranteed-lowest 2.2 A
limit clears that load by 10 percent, which is deliberately tight because the switch limits at about
the point the adapter itself runs out.

One finding is recorded rather than resolved. At the top of its published spread the switch passes
3.2 A, while the three J2 contacts carrying that current are rated 1.0 A each. Contact ratings are
continuous and a fault in current limit is not, since the part dissipates about 16 W into a short and
its thermal protection intervenes in milliseconds, so this is a V8 measurement rather than a static
violation. A test pins the 0.2 A overshoot so it cannot quietly grow.

The rail's transient behaviour is in `hardware/tests/test_rail_budget.py`, derived for the same
reason as the switch: what is left after handover and loop response are excluded is bounded by
conduction and charge. Soft start draws 36 mA into the output capacitors over its 4 ms ramp, so cold
start needs no inrush limiting. The rail holds 3.3 V until the module's output falls to 3.51 V at the
1.3 A the interface obliges, which is where that contract's 4.0 V floor comes from. Hold-up is about
five microseconds, so the rail follows its input and riding out a source change is the module's job.

What remains for V3 on this board is not board-side. Uninterrupted handover and source insertion
belong to the power module and are V8 measurements; transient response and stability belong to a
compensation network the buck's manufacturer does not publish, so no honest model here can produce
them. Both are recorded as such rather than left looking unfinished.

## Cost

The engineering BOM is 13.768 EUR in estimated custom-board parts across 39 fitted lines, up
0.366 EUR from the four-layer revision: J2 and J3 became seven-way to spread their supply across
1.0 A contacts, and the cell divider added three passives with values already in the BOM. No new
part type entered the design, so the four fee-bearing Extended lines and their 10.80 EUR of feeder
charges are unchanged.

This is not a factory quote and excludes assembly fees, the power module, its cell, sensor and cable
assemblies. The purchased subsystem belongs in complete-product cost, not the JLCPCB BOM. Two copper
layers at 162 x 46 mm should quote well under a four-layer panel, but the 25 EUR board target in
[boards.md](boards.md) still needs a real quote at the final dimensions before ordering.
