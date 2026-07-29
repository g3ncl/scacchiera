# Power board

The custom 90 x 32 mm board charges one protected 1S cell and supplies a regulated 5 V at 2 A. Its
SKiDL schematic is `hardware/pcb/power.py`; its reproducible layout is
`hardware/pcb/power_layout.py`.

## Boundary

The board implements [power-module-interface.md](power-module-interface.md). Qualified 5 V enters
through the seven-pin JST GH input. An eight-pin Molex Micro-Fit returns regulated power, ground,
optional I2C, and the raw cell voltage to the hub. The hub retains the independent cell-temperature
interlock and cell-voltage measurement, so this board is not trusted as their only safety or
telemetry mechanism.

The USB-C inlet is on the hub. Its passive sink resistors make ordinary USB-C and laptop Power
Delivery chargers provide their mandatory 5 V output. Nothing requests or accepts a higher PD
voltage.

## Charger and power path

U1 is BQ25619RTWR, a switch-mode 1S charger with an NVDC power path. It gives the system priority
while USB is present and uses its BATFET when the battery supplies the system. The filed data sheet
rates BATFET discharge at 5 A RMS. The boost sweep reaches 3.76 A RMS at the depleted-cell,
full-output corner.

The charger starts from a safe 500 mA input default and is configured by the hub over I2C for a
qualified 2 A source and 1.5 A cell charge. That target supplies 70 percent of 6.5 Ah in 182 ideal
minutes, leaving 58 minutes inside the functional 10-to-80 limit. Source insertion, removal,
charge taper, thermals, missing-cell behavior, and the exact protected assembly remain V8 physical
measurements rather than claims inferred from the IC alone.

## Regulated output

U2 is TPS61088RHLR with a Sumida CDMC8D28NP-1R2MC 1.2 uH inductor. The inductor is rated 12.2 A at
the saturation criterion and 12.9 A thermally, with 7 milliohm maximum DCR. A 100 k plus 51 k ILIM
network gives a 6.502 A guaranteed minimum current-limit corner. The 100 k plus 91 k plus 91 k FSW
network selects approximately 500 kHz.

The 124.9 k over 39 k feedback divider produces 4.909 to 5.215 V across the TPS61088 reference and
resistor tolerances. The output uses 45 uF nominal ceramic capacitance. U3, TLV809K33DBVR, removes
boost enable as the system rail falls through its 2.87 to 2.99 V threshold, with a local 100 nF
bypass. This prevents ordinary operation from following the cell down to its absolute discharge
cutoff.

`hardware/tests/test_sim_power_boost.py` runs 54 ngspice switching-stage corners: 2.87, 3.6, and
4.2 V input; 0.1, 1, and 2 A output; inductor nominal and plus or minus 20 percent; output
capacitance nominal and 50 percent effective. It reaches 119 mV peak-to-peak ripple, 5.02 A peak,
and 3.76 A RMS, all within the recorded criteria.

TI's official TPS61088 transient model is preserved unchanged in
`hardware/sim/models/vendor/TPS61088_TRANS.LIB`. A two-expression compatibility copy parses and
runs with ngspice's PSpice mode but does not switch, settling at the body-diode voltage. The passing
bench therefore models only the power stage from published limits. It does not claim control-loop
stability, startup, protection timing, or handover evidence.

## Interconnect and cell

The output uses Molex 430450800 and the cell input uses 430450200. Their manufacturer records rate
each contact at 8.5 A. The mating receptacle housings are Molex 430250800 and 430250200, with
430300038 female terminals for 18 AWG wire. Exact wire, qualified crimp or pre-crimped lead, color
coding, strain relief, and the protected battery assembly still have to be bound before V1 can close.

The filed Molicel INR-21700-M65A demonstrates the electrical and geometric feasibility of one large
cell. It stores 23.4 Wh typically, is 21.7 mm by 70.2 mm, and permits 26 A continuous discharge.
Placed lengthwise in the player rail, its diameter is the limiting cross-section. It is a bare cell,
not permission to install an unprotected loose cell.

## Board, panel, and release state

The board is 90 x 32 mm, two layers, and 1.0 mm thick. `make pcb-power-drc` reproduces zero
violations, zero unconnected items, and zero schematic-parity issues from the reviewed route.
`make panel` builds the routed board with both light bars on a 130.1 x 63.0 mm panel, joined by four
five-hole mouse-bite tabs. Individual routed boards are the DRC authority; the duplicated,
netlist-less manufacturing panel is not treated as an electrical schematic.

The schematic, layout, sourcing records, static connectivity, and bounded boost power-stage sweep
exist. V1 remains open on the complete battery and cable assemblies. V3 remains open on the charger
and power-path faults and on vendor-model control-loop evidence. V8 and V9 remain mandatory, so no
fabrication or assembly order is released by these results.
