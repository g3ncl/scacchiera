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
voltage. The hub measures both CC pins and leaves the BQ25895 at its 500 mA startup limit until a
stable 1.5 A or 3.0 A Type-C source advertisement permits more current.

## Charger and power path

U1 is BQ25895RTWR, a switch-mode 1S charger with an NVDC power path. It gives the system priority
while USB is present and uses its BATFET when the battery supplies the system. The filed data sheet
rates BATFET discharge at 6 A continuous and 9 A for one second, with a 9 A overcurrent threshold.
The conservative boost bound reaches 4.442 A RMS and 5.871 A peak at the depleted-cell,
full-output corner.

Q1, CSD25404Q3, sits between the keyed cell connector and `BAT_RAW`. Its body diode bootstraps
`BAT_RAW` only from a correctly oriented cell. U4, the open-drain TLV7021, then pulls the gate low
only after a divided connector voltage is positive. A 100 kohm gate-to-source resistor holds Q1 off
while the comparator is unpowered and during its high-impedance power-on reset. A BAT54H clamps
the sense input during reversed insertion. Once enabled, Q1 conducts in both directions for normal
charge and discharge.

With D+ and D- deliberately absent at this module boundary, the charger starts from its safe 500 mA
unknown-source default. The hub may configure a qualified source and a 1.472 A charge setting over
I2C. A 1.5 A advertisement caps total input at 1.5 A and may reduce charging behind system priority;
a 3.0 A advertisement permits the board's full 10 W input. Two 100 ohm resistors on ILIM
independently cap input at 1.970 A at the published KILIM and
resistor corners. That charge setting supplies 70 percent of 6.5 Ah in 185.5 ideal minutes, leaving
54.5 minutes inside the functional 10-to-80 limit. Source insertion, removal, charge taper,
thermals, and the exact protected assembly remain V8 physical measurements.

## Regulated output

U2 is TPS61088RHLR with a Sumida CDMC8D28NP-1R2MC 1.2 uH inductor. The inductor is rated 12.2 A at
the saturation criterion and 12.9 A thermally, with 7 milliohm maximum DCR. A 100 k plus 51 k ILIM
network gives a 6.502 A guaranteed minimum current-limit corner. The 100 k plus 91 k plus 91 k FSW
network selects approximately 500 kHz.

The 124.9 k over 39 k feedback divider produces 4.909 to 5.215 V across the TPS61088 reference and
resistor tolerances. The output uses 67 uF nominal ceramic capacitance. U3, TLV809K33DBVR, removes
boost enable as the system rail falls through its 2.87 to 2.99 V threshold, with a local 100 nF
bypass. This prevents ordinary operation from following the cell down to its absolute discharge
cutoff.

R11 and C13 form the series compensation branch. C13 is the exact 22 nF, 50 V, X7R
[Fenghua 0402B223K500NT](../../Vault/Scacchiera/Wiki/entities/0402b223k500nt.md), JLCPCB Basic
`C1532`. A 4,374-corner small-signal sensitivity analysis implements TPS61088 data-sheet equations
13 through 17. It combines line, load, inductor, output-capacitance, ESR, R11, and C13 corners with
a plus or minus 30 percent sensitivity on the error-amplifier transconductance. The minimum phase
margin is 54.64 degrees, every corner has infinite gain margin in the modeled frequency range, and
the highest crossover is 80.3 percent of TI's recommended ceiling. The former 4.7 nF value falls
below 45 degrees in the same analysis.

`hardware/tests/test_sim_power_boost.py` runs 162 ngspice switching-stage corners: 2.87, 3.6, and
4.2 V input; 0.1, 1, and 2 A output; inductor from minus 30 to plus 20 percent; and output
capacitance at nominal plus combined initial-tolerance, X5R temperature, and 50 percent DC-bias
bounds, with assembled-bank ESR from ideal to 15 milliohm. The third 22 uF output capacitor keeps
the minimum effective bank at 22.8 uF. The switching model reaches 138 mV peak-to-peak ripple,
5.325 A peak, and 3.877 A RMS. A separate 80
percent efficiency floor raises the accepted stress bound to 5.871 A peak and 4.442 A RMS, still
below the TPS61088 limit, the inductor ratings, and the BQ25895 battery path. The 4.442 A RMS figure
is the one a connector rating is compared against, since contact heating is I squared R; the peak
sizes the converter limit and the inductor. See [harnesses.md](harnesses.md).

TI's official TPS61088 transient model is preserved unchanged in
`hardware/sim/models/vendor/TPS61088_TRANS.LIB`. A two-expression compatibility copy parses and
runs with ngspice's PSpice mode but does not switch, settling at the body-diode voltage. The passing
bench therefore models only the power stage from published limits. It does not claim control-loop
closure, startup, or protection timing evidence. The compensation analysis selects a robust
nominal value, but TI publishes only a typical error-amplifier transconductance, so its sensitivity
band is not a guaranteed production corner. V3 therefore still needs a guaranteed model or
physical loop evidence, and V8 must measure phase and gain margin. The fitted Samsung capacitor sheet has no 500
kHz ESR maximum, so V8 must measure the complete bank below 15 milliohm rather than infer it from
the sheet's 120 Hz dissipation-factor test.

`hardware/tests/test_sim_power_path.py` covers the data-sheet-bounded averaged NVDC states: safe
default and qualified input limits, adapter priority, battery supplement, adapter removal, missing
and depleted cells, battery short, the external temperature gate against a stuck charge command,
and the full 10 W battery load. `hardware/tests/test_sim_reverse_battery.py` adds cold and
already-powered insertion at both polarities. The worst correct-cell comparator margin is 1.14 V
at 2.87 V. A reversed 4.2 V cell leaves `BAT_RAW` at minus 5.8 mV with USB absent and at positive
4.2 V with USB already present, inside the BQ25895 minus 0.3 V absolute limit. The 4.442 A RMS hot
pass-FET loss bound is 0.334 W and remains a V8 temperature and voltage-drop measurement.

`hardware/tests/test_junction_temperature.py` bounds that temperature rather than leaving it
entirely to V8. Stated as the ambient each part tolerates before its junction reaches the
data sheet limit, the reverse FET reaches its at 96.5 degrees on the 160 degrees per watt the data
sheet gives for minimum pad copper, and the charger reaches its at 103.5 degrees on the 85 percent
efficiency floor at the qualified 1.95 A input. The boost is the tightest of the whole product at
53.0 degrees, because charging it the complete 20 percent stage loss also hands it the inductor's
share. All three clear the 45 degree allowance, but the boost's 8 degrees is a bound, not margin,
until V8 measures it.

## Interconnect and cell

The output uses Molex 430450800 and the cell input uses 430450200. Their manufacturer records rate
each contact at 8.5 A. The mating receptacle housings are Molex 430250800 and 430250200, with
430300038 female terminals for 18 AWG wire. Exact wire, qualified crimp or pre-crimped lead, color
coding, strain relief, and the protected battery assembly still have to be bound before V1 can close.

The leading low-cost candidate is Keeppower's wired 1S1P 21700 protected pack. Its distributor
listing gives 21.6 Wh nominal, 12 A continuous discharge, and a maximum listed body of 75.45 by
22.25 mm. It clears the 4.442 A RMS and 5.871 A peak load bounds, while its protection PCB covers
overcharge, overdischarge, overcurrent, and short circuit. It is not yet bound because wire gauge,
connector, exact thresholds, shipped revision, thermistor attachment, and lead bend remain open.
The filed Molicel INR-21700-M65A remains the higher-capacity feasibility reference, but it is bare
and currently unavailable.

`hardware/cad/power_rail_fit.py` reserves 80 x 26 x 23 mm for the complete protected assembly.
The 75.45 x 22.25 mm Keeppower body fits inside that allocation, with lateral room reserved for the
cell-bonded thermistor rather than stacking it against the 24 mm rail height. The allocation sits
lengthwise beside a conservative 90 x 32 x 10 mm power-board envelope with a 5 mm gap.
Both fit the 310 x 46 x 24 mm service volume and leave 125 mm of rail length after the end
clearances. This is an allocation, not pack evidence. The supplier drawing, NTC retention, lead
exit, connector, and cable bend still have to pass the generated STEP fit before V7 can close.

## Board, panel, and release state

The board is 90 x 32 mm, two layers, and 1.0 mm thick. `make pcb-power-drc` reproduces zero
violations, zero unconnected items, and zero schematic-parity issues from the reviewed route.
`make panel` builds the routed board with both light bars on a 130.1 x 63.0 mm panel, joined by four
five-hole mouse-bite tabs. Individual routed boards are the DRC authority; the duplicated,
netlist-less manufacturing panel is not treated as an electrical schematic.

The schematic, layout, sourcing records, static connectivity, boost power-stage sweep, averaged
power-path model, and reverse-cell fault bench exist. V1 remains open on the complete battery and
cable assemblies. V3 remains open on temperature and ESR corners, switching-loop evidence, and
other transient protection timing. V8 still must physically test reversed insertion and pass-FET
temperature. V8 and V9 remain mandatory, so no fabrication or assembly order is released by these
results.
