# Power board

The custom board that holds the cell, charges it, and hands the hub a regulated 5 V. It exists as a
snap-off piece of the light-bar panel, so its fabrication rides on an order that was happening
anyway. Schematic in `hardware/pcb/power.py`, layout in `hardware/pcb/power_layout.py`.

## Boundary

This board implements [power-module-interface.md](power-module-interface.md) rather than defining a
boundary of its own. The hub is unchanged by its existence: qualified 5 V leaves the hub on J2 and
comes back regulated on J3, exactly as a purchased module would deliver it. That is deliberate. A
bought module can still replace this board without touching the hub, and this board can be replaced
without touching anything else, which is what "modular" has to mean to be worth anything.

Two consequences follow. The cell-temperature interlock stays on the hub, where it is already proven
across 384 corners, so nothing on this board is trusted for charge safety. And the hub keeps
measuring cell voltage on its own ADC through `BAT_RAW`, so nothing here is trusted for telemetry
either.

## Charging

The original MCP73871 stage is superseded by the 10 W requirement. Its battery-to-system ideal
diode is specified for at most 2 A, while a 10 W output draws roughly 4 A from a depleted 1S cell
after conversion loss. The replacement requires a switch-mode 1S charger with an NVDC power path,
a battery path rated above 5 A, autonomous cold start, and a hardware-safe USB input limit.

The current replacement candidate is BQ25619RTWR. Its 4 x 4 mm WQFN package remains practical on a
two-layer panel, its BATFET has a 5 A minimum discharge clamp and 30 mOhm maximum resistance, and it
starts autonomously from either source. PSEL will select the safe 500 mA default until the hub sets
the qualified source and charge limits over I2C. This candidate is not fitted until its exact part,
passives, package proof, firmware startup behavior, and simulation are complete.

### Superseded 1 A implementation

MCP73871, at 1 A. The part was rejected from the first design because 500 mA made a recharge take as
long as a session; the relaxed 240-minute limit in
[functional/power.md](../functional/power.md) lets it run at its full rate and clear that limit with
30 minutes in hand. Its power path is what buys uninterrupted output: the system runs from the input
while the cell charges independently, and falls back to the cell without a gap.

Every setting comes from the data sheet rather than habit:

| Pin | Setting | Why |
| --- | --- | --- |
| PROG1 | 1.0 k | IREG is 1000 mA over PROG1 in kohm, so 1 k is the full 1 A and the floor of its 1 k to 20 k range |
| PROG3 | 10 k | Terminates at 100 mA, a fiftieth of the cell, inside its 5 k to 100 k range |
| SEL | high | Adapter mode, where PROG1 sets the current, rather than a USB port's 100 or 500 mA |
| TE | low | Enables the safety timer |
| CE | high | Charging is gated upstream by the hub's temperature window, not here |
| THERM | 10 k to VSS | 50 uA across 10 k sits at 0.5 V, inside the 0.25 to 1.24 V window it would otherwise suspend on |
| VPCC | 100 k / 39 k | Backs charging off below a 4.38 V input, which is how the board keeps from loading a source past its rating |

THERM is neutralised on purpose. One bead cannot bias two monitors without them interacting, and the
hub's analog window is the one with corner evidence behind it.

## The 5 V rail

The 10 W replacement candidate is TPS61088RHLR. It is a synchronous boost converter with external
current limit and compensation. At a 3.0 V minimum working cell voltage, 5 V at 2 A and 85 percent
conservative efficiency require 3.92 A average input before ripple. The design target is therefore
a 5.5 A minimum switch limit and an inductor rated for at least that current. The enable divider
must stop discharge at 3.0 V or above so neither the charger BATFET's 5 A minimum clamp nor the
cell's deep-discharge boundary becomes normal regulation behavior.

The output and battery connectors must change with the silicon. Two 1 A JST GH contacts provide no
margin at 2 A, and the JST PH cell connector cannot carry the roughly 4 A depleted-cell current.
Both connector revisions are release blockers, including the mating harness and wire gauge.

### Superseded converter implementation

TPS61023 boosts the charger's system terminal, not the cell directly, so the rail keeps regulating
whether an adapter is present or not. A 330 k, 39 k and 5.1 k divider against its 0.6 V reference
gives 5.09 V: inside the hub's 4.5 to 5.5 V acceptance and under the converter's own 5.5 V minimum
over-voltage threshold. The lower leg is two resistors because the exact ratio wants a value this
design does not already carry, and a series pair of bound parts beats a new part number whose order
code the catalogue reports two ways.

L1 is Murata DFE252012F-1R0M=P2, bound to LCSC C435392. It is 1.0 uH at 20 percent tolerance,
40 mOhm maximum DCR, 4.7 A saturation and 3.3 A temperature-rise current. Its exact manufacturer
land pattern is generated with the board.

The corrected display load invalidates this revision of the converter stage. The two displays may
draw 320 mA each, taking coincident module load to 1.48 A. TPS61023's 2.7 A guaranteed minimum
valley limit cannot support that at the depleted-cell and inductor corners. The converter must be
replaced before V3 can pass; its typical 5 V at 1.5 A application is not release evidence.

## Board and panel

46 x 32 mm, two layers, 1.0 mm. `make pcb-power-drc` reproduces 0 violations, 0 unconnected items and
0 schematic-parity issues from the reviewed route.

`make panel` builds a 130.1 x 63.0 mm panel holding both light bars and this board, joined by four
five-hole mouse-bite tabs. The panel is generated from the routed boards rather than drawn, so it
cannot disagree with them; re-run it after any board changes. Its own DRC reports only the two
classes structural to a netlist-less panel, footprint-library links and unconnected items, with no
clearance, edge or annular findings.

Panelising is what makes this board's fabrication nearly free, and it fixes something that was
already wrong: a 120 x 8.5 mm light bar is below the outline JLCPCB will assemble, which is why
`bom.py` routes the bars to hand assembly. The panel is not.

## Open evidence

The board is new, so its gates are not. Its fitted-part audit now has no sourcing blockers, but the
display-current contradiction has exposed a required converter redesign. **V3 is open on it**: nothing here has a
corner sweep yet, and a charger with a cell on it is exactly the circuit the workflow wants
simulated, then measured at V8 and reviewed at V9. That burden is the price of building this rather
than buying it, and panelising the PCB does not reduce it.
