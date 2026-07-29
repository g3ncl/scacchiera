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

TPS61023 boosts the charger's system terminal, not the cell directly, so the rail keeps regulating
whether an adapter is present or not. A 330 k, 39 k and 5.1 k divider against its 0.6 V reference
gives 5.09 V: inside the hub's 4.5 to 5.5 V acceptance and under the converter's own 5.5 V minimum
over-voltage threshold. The lower leg is two resistors because the exact ratio wants a value this
design does not already carry, and a series pair of bound parts beats a new part number whose order
code the catalogue reports two ways.

L1 is an NR6045S1R0NT: the same series and footprint as the hub's inductor, so the filed data sheet
already covers it. Its selection table lists 1.0 uH, 9.5 A saturation and 5.5 A rated against the
2.4 A this converter draws from a depleted cell, and the value sits on the boost's 1 uH nominal even
at its 30 percent tolerance extremes.

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

The board is new, so its gates are not. **V1 is open on it**: L1's order code is unverified, and the
four revived parts need their audit records regenerated. **V3 is open on it**: nothing here has a
corner sweep yet, and a charger with a cell on it is exactly the circuit the workflow wants
simulated, then measured at V8 and reviewed at V9. That burden is the price of building this rather
than buying it, and panelising the PCB does not reduce it.
