# JLCPCB assembly sourcing

This register records the project's JLCPCB part selections for the three boards and the parts that
need a deliberate follow-up. The supporting catalog capture and live-stock evidence live in the
vault. The complete bound BOM was checked live again on 2026-07-25. Stock and prices remain
time-sensitive.

`make pcb-fab` emits the upload pair `<board>_jlcpcb_bom.csv` and
`<board>_jlcpcb_cpl.csv`, and rejects the export if their designators differ. The internal costed file is named
`<board>_engineering_bom.csv`; do not upload it. Blank `LCSC Part #` cells in the upload BOM are
intentional unresolved items, not permission to select a substitute during ordering.

The engineering BOM also records `JLC Library`, `Assembly Route`, `Hand Method`, and
`Assembly Reason`. These columns are planning guidance. They do not silently remove parts from the
JLCPCB upload. `Hand` identifies a practical candidate to buy elsewhere and omit deliberately when
reviewing the JLCPCB match; `JLCPCB` means the part is Basic, too small or hidden for reliable iron
soldering, or too repetitive to place economically by hand.

Each fabrication run emits two upload choices. `<board>_jlcpcb_bom.csv` and
`<board>_jlcpcb_cpl.csv` ask JLCPCB to place every fitted part. The matched
`<board>_jlcpcb_hybrid_bom.csv` and `<board>_jlcpcb_hybrid_cpl.csv` omit every `Hand` row. Upload
the hybrid pair together when using manual completion, then purchase exactly the rows in
`<board>_hand_bom.csv` elsewhere. Never mix the full BOM with the hybrid CPL or the reverse.
The lightbar is the exception: JLCPCB cannot assemble its 120 by 8.5 mm outline, so both of its
JLCPCB BOM/CPL pairs are intentionally empty and its hand BOM contains every fitted component.
Order only its bare PCB Gerbers from JLCPCB.

The upload BOM uses the selected manufacturer's exact MPN in `Comment`, not the schematic value.
This makes the MPN agree with `LCSC Part #` and prevents JLCPCB's misleading comment mismatch
warning. The value and tolerance remain visible in the engineering BOM.

For Standard PCB Assembly, search JLCPCB's public Basic library first and require live stock above
the order quantity including attrition. Each unique Extended component currently adds a 2.70 EUR
feeder-change labor fee, so minimize Extended BOM lines. Keep one only when no Basic part preserves
the required function, package, and electrical limits. If no safe public-stock part exists, use
Pre-Order or Global Sourcing and wait until the inventory appears in My Parts Lib before submitting
the assembly order. Re-match the BOM immediately before payment because inventory can change.

## Factory versus hand assembly

The default route assumes an iron plus ordinary hot air. Stencil and hot-plate reflow can move some
factory-only parts into the manual column, but it also needs controlled paste deposition and close
inspection. Do not count a part as hand-solderable merely because one prototype can be made to
work.

| Board | Prefer JLCPCB | Practical hand-solder candidates |
| --- | --- | --- |
| Lightbar | none, because the board is below JLCPCB's supported assembly size | all components; use stencil reflow for the LEDs and 0402 capacitors, then iron or hot air for J1 and C18 |
| Matrix | repeated groups of 16 to 32 small passives, SOD-523 diodes, MOSFETs, and the Basic shift registers | the single seven-pin connector J1 |
| Hub | QFN, DFN, SON, fine-pitch TSSOP, USB-C, 0402 RF parts, the crystal, and the ESP32 module | JST connectors, switch, low-count 0603/0805/1206 parts, SOT-23 devices, and the two-terminal boost inductor |

For the current bound BOM, following the `Hand` recommendations removes 22 board-specific
Extended lines: two from the lightbar, one from the matrix, and nineteen from the hub. At 2.70 EUR
per line, that avoids up to 59.40 EUR in feeder-change fees across the three separate designs. It
leaves fourteen bound Extended lines for factory placement: six on the matrix and eight on the hub.
This saving assumes the hand-fitted parts are explicitly removed from the assembly order after
reviewing the generated engineering BOM.

The 2026-07-25 hub hybrid quote is the current cost baseline. It reports 31 detected BOM rows, 29
confirmed rows, and shortages on U4 and Y1. Economic PCBA is 53.13 EUR: 7.19 setup, 1.34 stencil,
24.28 components, 18.88 Extended-component fees, 0.69 SMT assembly, and 0.75 nitrogen reflow. The
18.88 EUR is seven nominal 2.70 EUR feeder changes after quote rounding. J1 was detected with zero
quantity and no component price, so budget another 2.70 EUR if it becomes a charged placement.

The ESP32-C3-MINI-1U is not an iron-solder part. Its 0.8 mm perimeter pitch is manageable, but the
large ground pad is split into nine paste areas under the module. It is feasible with a stencil and
hot plate or reflow oven, then electrical inspection, but JLCPCB or another reflow assembler is the
lower-risk route for the first hub.

The current 27.12 MHz crystal is only 2.0 by 1.6 mm with four underside pads. It is a hot-air or
reflow job, not a good manual iron candidate. A 3.2 by 2.5 mm crystal could be easier to rework, but
changing it also changes the footprint and RF layout and needs a reviewed board revision.

## Selected Basic parts

Every selection below has the same value and package as the design. Capacitors also keep the
specified dielectric and meet or exceed the specified voltage; resistors are 1%, 100 mW, and 75 V.
The catalog prices are recorded only as current sourcing evidence, not as a conversion from the
engineering BOM's EUR estimates.

| Design need | JLC/LCSC part | Catalog evidence |
| --- | --- | --- |
| 100 nF 0402 X7R | C1525, Samsung CL05B104KO5NNNC | 16 V, 47,606,425 in stock, 0.0053 catalog price |
| 22 uF 0805 | C45783, Samsung CL21A226MAQNNNE | 25 V X5R, 2,601,042 in stock, 0.5564 catalog price |
| 10 uF 0805 | C15850, Samsung CL21A106KAYNNNE | 25 V X5R, 10,562,367 in stock, 0.1394 catalog price |
| 4.7 uF 0805 | C1779, Samsung CL21A475KAQNNNE | 25 V X5R, 2,656,762 in stock, 0.0501 catalog price |
| 1 uF 0402 | C52923, Samsung CL05A105KA5NQNC | 25 V X5R, 14,561,021 in stock, 0.0265 catalog price |
| 1 uF 0603 | C15849, Samsung CL10A105KB8NNNC | 50 V X5R, 15,425,764 in stock, 0.0964 catalog price |
| 10 pF 0402 C0G | C32949, Samsung CL05C100JB5NNNC | 50 V, 1,436,709 in stock, 0.0053 catalog price |
| 100 pF 0402 C0G | C1546, 0402CG101J500NT | 50 V, 6,594,882 in stock, 0.0096 catalog price |
| 5.1 k, 100 k, 82 k, 4.7 k, 100, 1 k, 1 M, 330 k, 2 k, 10 k 0603 resistors | C23186, C25803, C23254, C23162, C22775, C21190, C22935, C23137, C22975, C25804 | exact 1% 0603 Basic selections, all above 900,000 in stock |

C45783 is the only Basic 22 uF 0805 candidate in the captured catalog. Its unit price is high, but
an Extended alternative must save more than its unique-component fee before it is worthwhile.

The hub's C7 BOM inconsistency was corrected: it is specified as 10 uF and now uses the 10 uF
Murata MPN, rather than the 22 uF MPN shared by C1-C3 and C8-C9.

## Production status by board

Every bound code below was checked against live JLCPCB stock above the five-board quantity on
2026-07-25.

### Lightbar

- **Assembly route:** bare PCB fabrication only. Populate every component manually. A stencil and
  hot plate or reflow oven are strongly preferred for the seventeen LEDs and 0402 capacitors.
- **C18:** C49066, Samsung CL32A107MQVNNNE, is the exact 100 uF, 6.3 V, X5R, 1210 requirement.
- **J1:** C225127, CJT A1257WR-S-4P, preserves the 1.25 mm GH-compatible right-angle interface.
- **D1-D17, WS2812C-2020:** no Basic 2020-package, pin-compatible LED candidate. A different
  stocked addressable LED changes both optics and the power assumptions. Keep this line unbound
  and use Pre-Order or Global Sourcing for the exact low-current device.

### Matrix

The matrix upload is fully bound. Its 11 BOM rows contain 165 placed references, every row has an
exact JLC code, and the CPL contains the same 165 references. PCB copper loops L2/L4 through L32,
DNP tuning capacitors, and power flags are absent from both upload files.

| Designators | Exact MPN | JLC part | Library | Live stock | Selection basis |
| --- | --- | --- | --- | ---: | --- |
| C2/C6 through C62 | CC0603FRNPO9BN221 | C519500 | Extended | 157,735 | 220 pF, 50 V, C0G, 0603, 1%; tighter than the required 2% |
| C65/C66 and C1/C5 through C61 | CL05B104KO5NNNC | C1525 | Basic | 47,288,853 | exact 100 nF, 16 V, X7R, 0402 part |
| D1-D32 | BAR64-02V | C5295579 | Extended | 25,001 | JSCJ PIN diode, SOD-523, validated as described below |
| J1 | SM07B-GHS-TB(LF)(SN) | C495552 | Extended | 52,619 | exact JST 7-pin right-angle connector |
| L1/L3 through L31 | SDFL2012S100KTF | C1046 | Basic | 167,255 | 10 uH, 0805, 15 mA rating exceeds the 10.29 mA simulated bias |
| Q1/Q3 through Q31 | BSS123 | C7420338 | Extended | 33,935 | exact SOT-23 N-channel device and modeled RF capacitances |
| Q2/Q4 through Q32 | BSS84 | C114481 | Extended | 225,237 | exact SOT-23 P-channel device, 50 V and 130 mA |
| R1/R4 through R46 | 0603WAF150KT5E | C22769 | Extended | 44,567 | 1.5 ohm, 1%, 100 mW, 0603 |
| R2/R5 through R47 | RS-03K1800FT | C286574 | Extended | 232,046 | 180 ohm, 1%, 100 mW, 0603 |
| R3/R6 through R48 | 0603WAF1003T5E | C25803 | Basic | 7,405,766 | 100 kohm, 1%, 100 mW, 0603 |
| U1/U2 | 74HC595D,118 | C5947 | Basic | 182,847 | Nexperia SOIC-16 device, same logic and pinout |

The 2026-07-25 matrix hybrid quote confirms all ten uploaded rows with no shortages. PCB fabrication
is 59.03 EUR and Economic PCBA is 82.02 EUR, for 141.05 EUR before shipping and tax. The dominant
cost is board size: 17.74 EUR on fabrication plus 50.47 EUR on assembly, or 68.21 EUR total. The
assembly large-size charge alone is 61.5% of the PCBA price. Components cost only 7.56 EUR and the
Extended-component fee is 13.48 EUR.

The upload contains six rows labelled Extended, while 13.48 EUR corresponds to five nominal
2.70 EUR feeder changes after quote rounding. The quote does not identify which row has its feeder
fee waived, so use the displayed total rather than estimating this order from labels alone.

Selective hand fitting does not remove the 50.47 EUR assembly large-size charge. The meaningful
choice is therefore binary: pay JLCPCB 82.02 EUR to place the 164 hybrid references, or order the
bare matrix PCB and populate all 165 purchased references manually, including 32 SOD-523 diodes
and the repeated 0603/SOT-23 arrays. Splitting the matrix into smaller PCBs could reduce future
large-size charges, but that is an RF and interconnect redesign rather than a sourcing substitution.

The stocked JSCJ BAR64-02V replaces the unavailable NXP BAP64-02. Its conservative ngspice model
uses the JSCJ limits of 2.5 ohm maximum at 10 mA and 0.55 pF maximum at 1 V, 0.35 pF maximum at
5 V. The complete matrix validation passes with 14.179 MHz selected-cell resonance, 13.385 MHz
loaded-bus resonance, 84.6 dB off/on suppression, 10.29 mA on-state bias, and effectively zero
off-state bias. The replacement keeps the SOD-523 package and pin polarity.

At the live first-unit prices, BAR64-02V is $0.0361 versus $0.4253 for the unavailable NXP match.
For JLCPCB's quoted 160-diode quantity that is a component-price reduction of about $62.27. The
1.5 ohm C22769 selection is $0.0047 versus $0.0232 for the initially matched RT0603 part, saving
about $1.67 across 90 pieces. These figures exclude setup, attrition, tax, and shipping.

The 10 uH choke remains Basic C1046. Its 15 mA rating exceeds the validated 10.29 mA bias, and using
an Extended alternative solely for extra margin would add another unique-component fee.

### Hub

The hub necessarily uses Extended ICs. Its safe public-stock substitutions now include the exact
PN5180 C3E package suffix, verified connector families, RF chokes, protection parts, exact feedback
values, and passives that meet the original dielectric, voltage, and footprint requirements. The
24.9 kohm R6 replacement differs by only 0.4%, inside the original 25 kohm 1% tolerance.

Three lines remain deliberately unbound:

- **L2, 74438357010:** stocked 1 uH candidates reduce saturation-current and DCR margin. Use
  Pre-Order or Global Sourcing rather than weakening the TPS61023 power stage.
- **U4, ESP32-C3-MINI-1U-N4X:** the stocked N4 module uses the older chip revision. Do not trade
  away the N4X revision and its lifecycle advantage merely to obtain public stock. JLCPCB matched
  exact C49230958 in the hybrid quote, but reported a two-piece shortfall.
- **Y1, EXS00A-CS01188:** stocked 27.12 MHz candidates found so far use a different footprint.
  Changing it requires a reviewed layout change, not a purchasing substitution. JLCPCB matched
  exact C3032297 in the hybrid quote, but reported a six-piece shortfall.

## IC upgrade and cost review

The captured Basic catalog contains no exact PN5180, ESP32-C3-MINI-1U, charger, regulator,
expander, protection IC, or logic buffer. The live catalog does contain Basic C5947, so the matrix
uses its Nexperia 74HC595 in SOIC-16 instead of the Extended TI TSSOP device. Any future proposal
must state:

1. exact JLC/LCSC part number, stock, price, and assembly classification;
2. per-board saving after the unique Extended-component fee;
3. pinout, electrical-limit, firmware, and layout impact; and
4. whether the existing ngspice validation must be rerun.

For the NFC reader and ESP32 in particular, a different package, protocol, RF architecture, or
firmware target is a redesign, not a purchasing substitution. Bring a concrete candidate to this
register before it is introduced.
