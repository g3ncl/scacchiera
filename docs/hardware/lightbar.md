# Light bar board

The player feedback bar from [functional/interface.md](../functional/interface.md): 120 x 8.5 mm,
17 low-current LEDs behind a replaceable diffuser, one identical board per player rail. This doc
describes the implemented design; the schematic and layout are generated from
`hardware/pcb/lightbar.py` and `hardware/pcb/lightbar_layout.py`.

## Design

One WS2812C-2020 addressable pixel per position. The controller sits inside each LED, so the whole
board is 17 pixels, per-pixel 100 nF decoupling, one 100 uF bulk capacitor, and a JST GH
connector; the hub drives any color pattern over a single data line. Full color is required by the
feedback semantics (red illegal-position flash plus move, result, WiFi, and countdown cues), and
the WS2812C is the low-current variant (about 5 mA per channel), matching the functional spec's
low-current requirement and the dark-when-idle power behavior.

Every component sits on the front face, as the diffuser requirement demands. The board is 1.0 mm
thick to stay thin behind the diffuser.

## Interface to the hub

4-wire JST GH (1.25 mm): `LED_5V`, `GND`, `DATA_IN`, `DATA_OUT`. Data is the standard WS2812
single-wire stream at 800 kHz from the hub. `DATA_OUT` returns the end of the chain to the
connector so the two bars could be daisy-chained from one hub pin if the harness prefers it; with
one cable per bar it is simply left unconnected.

The 5 V rail comes from the hub. Worst-case load is all 17 pixels white, about 260 mA per bar.

## Validation

`hardware/tests/test_sim_lightbar.py` extracts every routed `LED_5V` and `GND` track segment from
the generated `lightbar.kicad_pcb`, builds the resistor network of the real copper, loads it with
all 17 pixels white, and solves it in ngspice. The criterion in
[criteria.yaml](criteria.yaml) bounds the worst supply-loop droop (feed drop plus ground rise) at
any LED to 100 mV; the routed board measures 24.6 mV at the far end of the bar.

## Cost

Generated engineering BOM (`hardware/pcb/generated/lightbar/lightbar_engineering_bom.csv`) totals 1.46 EUR in parts per
bar, against the 5 EUR per-bar target in [boards.md](boards.md) including fabrication.
