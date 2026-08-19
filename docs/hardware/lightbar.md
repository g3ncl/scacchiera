# Light bar board

The player feedback bar from [functional/interface.md](../functional/interface.md): 120 x 8.5 mm,
14 low-current LEDs behind a replaceable diffuser, one identical board per player rail. This doc
describes the implemented design; the schematic and layout are generated from
`hardware/pcb/lightbar.py` and `hardware/pcb/lightbar_layout.py`.

## Design

One Harvatek T37K3RGB-05C000112U1930 addressable pixel per position. The controller sits inside each LED, so the whole
board is 14 pixels, per-pixel 100 nF decoupling, one 100 uF bulk capacitor, and a JST GH
connector; the hub drives any color pattern over a single data line. Full color is required by the
feedback semantics (red illegal-position flash plus move, result, WiFi, and countdown cues), and
the selected LED sinks 5 mA per channel, matching the functional spec's low-current requirement
and the dark-when-idle power behavior.

Every component sits on the front face, as the diffuser requirement demands. The board is 1.0 mm
thick to stay thin behind the diffuser.

There are no mounting holes, unlike the matrix and hub boards. J1, the pixel array and the bulk
capacitor occupy x 0.77 to 117.85 of a 120 mm board, leaving 2.15 mm against the 5.40 mm an M2 pad
plus clearance needs. Even with room, a 4.4 mm pad on an 8.5 mm board would leave 2.05 mm of material
either side of the screw, which tears out of a 1.0 mm substrate. The bar is retained by the diffuser
channel or by adhesive, as LED strips of this shape normally are.

### Why this LED, and why 14 of them

JLCPCB cannot assemble a 120 x 8.5 mm outline, so this board is populated by hand with an iron and
no hot air or stencil. That rules out the WS2812C-2020 class of pixel, whose four pads sit
underneath its body. The Harvatek part's legs extend outside the body, so every joint is reachable.

The cost is width. Its 3.5 by 2.8 mm body and four external pads need more pitch than a 2.0 mm
WS2812C-2020 body, and the 4-pin JST GH is 9.46 mm wide and 6.40 mm deep, too deep to tuck under the
LED row in an 8.5 mm tall board. That leaves room for 14 pixels rather than 17, which is the count
[functional/interface.md](../functional/interface.md) fixes. The selected 5 mA part keeps the
hub's 5 V rail and TPS2553 limiter inside their existing budget without a firmware brightness cap.
The exact manufacturer datasheet, pinout, land pattern and DigiKey cut-tape ordering code are filed
in the V1 component audit, replacing the unresolved SK6805 catalog selection.

## Interface to the hub

4-wire JST GH (1.25 mm): `LED_5V`, `GND`, `DATA_IN`, `DATA_OUT`. Data is the standard WS2812
single-wire stream at 800 kHz from the hub. `DATA_OUT` returns the end of the chain to the
connector so the two bars could be daisy-chained from one hub pin if the harness prefers it; with
one cable per bar it is simply left unconnected.

The 5 V rail comes from the hub. Worst-case load is all 14 pixels white: 5 mA per channel plus a
conservative 1 mA control allowance gives 16 mA per pixel, so 224 mA per bar and 448 mA for both, inside
the roughly 0.67 A the hub's TPS2553 limiter allows.

## Validation

`hardware/tests/test_sim_lightbar.py` extracts every routed `LED_5V` track segment from the
generated `lightbar.kicad_pcb`, models the back-copper ground pour as a resistive ladder between
its real stitching-via positions, loads the network with all 14 pixels white at the datasheet's
16 mA, and solves it in ngspice. The criterion in [criteria.yaml](criteria.yaml) bounds the worst
supply-loop droop (feed drop plus ground rise) at any LED to 100 mV; the routed board measures
12.46 mV at the far end of the bar.

Ground moved from routed track to a pour because the LED pad span left no pad-free band
for a front-copper ground bus. The plane is still layout-derived in the simulation rather than
assumed ideal: its resistance comes from the via positions in the board file and the real pour
width, one square of copper at a time.

## Cost

Generated engineering BOM (`hardware/pcb/generated/lightbar/lightbar_bom_all_parts.csv`) totals
6.33 EUR in parts per bar. This exceeds the original 5 EUR target because an exact, stocked,
hand-solderable LED was chosen instead of retaining an unresolved catalog part.
