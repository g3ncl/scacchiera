# JLCPCB assembly sourcing

This register records the project's JLCPCB part selections for the three boards and the parts that
need a deliberate follow-up. The supporting catalog capture and live-stock evidence live in the
vault. The complete bound BOM was checked live again on 2026-07-25. Stock and prices remain
time-sensitive.

The hub selections and quotes in this register describe the last generated MCP73871 design. That
hub is superseded by the commercial 5 V subsystem boundary in [hub.md](hub.md), so none of its hub
counts, costs, or order files are current release evidence. Update this register from the
regenerated simplified hub only after its V1 and V2 gates pass. Lightbar and matrix selections
remain current.

`make pcb-fab` emits the upload pair `<board>_jlcpcb_upload_bom.csv` and
`<board>_jlcpcb_upload_cpl.csv`, and rejects the export if their designators differ. The internal costed file is named
`<board>_bom_all_parts.csv`; do not upload it. Blank `LCSC Part #` cells in the upload BOM are
intentional unresolved items, not permission to select a substitute during ordering.

The engineering BOM also records `JLC Library`, `Assembly Route`, `Hand Method`, and
`Assembly Reason`. These columns are planning guidance. They do not silently remove parts from the
JLCPCB upload. `Hand` identifies a practical candidate to buy elsewhere and omit deliberately when
reviewing the JLCPCB match; `JLCPCB` means the part is Basic, too small or hidden for reliable iron
soldering, or too repetitive to place economically by hand.

Each fabrication run emits two upload choices. `<board>_jlcpcb_upload_bom.csv` and
`<board>_jlcpcb_upload_cpl.csv` ask JLCPCB to place every fitted part. The matched
`<board>_jlcpcb_max_assembly_bom.csv` and `<board>_jlcpcb_max_assembly_cpl.csv` omit every `Hand` row. Upload
the hybrid pair together when using manual completion, then purchase exactly the rows in
`<board>_self_solder_bom.csv` elsewhere. Never mix the full BOM with the hybrid CPL or the reverse.
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

The build plan assumes **an iron only**: no hot air, no stencil, no hot plate. That is what decides
each route, so "hand" here always means a joint an iron tip can reach.

| Board | Prefer JLCPCB | Hand fitted |
| --- | --- | --- |
| Lightbar | none, the board is below JLCPCB's supported assembly size | everything; the LED was changed to a legs-outside-body package so an iron reaches all four joints |
| Matrix | none, see below | all 165 references |
| Hub, historical MCP73871 design | QFN, SON, SOT563, USB-C, the crystal, and the ESP32 module | JST connectors, switch, SOT-23 devices, inductors, 0402 C0G RF and timing capacitors, and the 0.65 mm TSSOP expander |

Packages classified reflow-only are those with pads under the body or a pitch no tip can reach:
QFN, SON, SOT563, USB-C, the 3225 crystal, and the ESP32 module. **0402, SOD-523, SOT-23, SOIC and
0.65 mm TSSOP are deliberately not on that list.** They are tedious but every joint is reachable,
and the plan hand-fits them, which is what removes their feeder fees.

The lightbar and the matrix are now both fully hand populated, so only the hub goes to assembly.
Order bare Gerbers for the other two. The hub leaves **seven** Extended lines for factory placement,
all genuinely reflow-only: J1 (USB-C), U1 (MCP73871 QFN-20), U2 (TPS63802 SON-10), U3 (PN5180
QFN-40), U4 (ESP32-C6-MINI-1U), U5 (TPS61023 SOT563) and Y1 (the 3225 crystal). Everything else
Extended on the hub is hand fitted from `hub_self_solder_bom.csv`.

Moving the 0402 C0G RF capacitors (C33/C36, C34) and the TSSOP expander (U6) to hand removes three
feeder changes, about 8.10 EUR. That is offset by U4 and Y1 becoming real charged lines now that
they are bound to stocked parts, where previously they were shortages the factory simply would not
place. Net feeder count is about the same, but the board comes back complete instead of missing its
MCU and its reader clock, which was the point.

The quote below predates the U4, Y1, C31/C32, U6 and C33/C34 changes, so re-quote before ordering.
It is kept as the cost structure, not as a current price.

The 2026-07-25 hub hybrid quote is the current cost baseline. It reports 31 detected BOM rows, 29
confirmed rows, and shortages on U4 and Y1. Economic PCBA is 53.13 EUR: 7.19 setup, 1.34 stencil,
24.28 components, 18.88 Extended-component fees, 0.69 SMT assembly, and 0.75 nitrogen reflow. The
18.88 EUR is seven nominal 2.70 EUR feeder changes after quote rounding. J1 was detected with zero
quantity and no component price, so budget another 2.70 EUR if it becomes a charged placement.

The ESP32-C6-MINI-1U is not an iron-solder part. Its 0.8 mm perimeter pitch is manageable, but the
ground pad is an array of 1.45 mm pads under the module that no tip and no syringe can reach.
JLCPCB places it.

The crystal is now 3.2 by 2.5 mm (3225) rather than 2.0 by 1.6 mm. Its four pads are still on the
underside, so it stays a factory placement, but the larger pads are reworkable with hot air if one
ever has to come off.

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

- **Assembly route:** bare PCB fabrication only, populated by hand with an iron. Both JLCPCB BOM
  and CPL pairs are intentionally empty and `lightbar_self_solder_bom.csv` holds every fitted part.
- **C15:** C49066, Samsung CL32A107MQVNNNE, is the exact 100 uF, 6.3 V, X5R, 1210 requirement.
- **J1:** C225127, CJT A1257WR-S-4P, preserves the 1.25 mm GH-compatible right-angle interface.
- **D1-D14, Harvatek T37K3RGB-05C000112U1930:** DigiKey cut-tape order
  `3147-T37K3RGB-05C000112U1930CT-ND`. The exact manufacturer datasheet gives pin 1 DOUT, pin 2
  GND, pin 3 DIN and pin 4 VDD, a 3.5 by 2.8 mm body, external iron-reachable leads, 5 mA per
  channel and an 800 kHz protocol. The observed stock was 53, enough for two bars plus attrition.
  This closes the unresolved C5200774 catalog and pinout conflict without changing the rail budget.

### Matrix

The matrix upload is fully bound. Its 11 BOM rows contain 165 placed references, every row has an
exact JLC code, and the CPL contains the same 165 references. PCB copper loops L2/L4 through L32,
DNP tuning capacitors, and power flags are absent from both upload files.

| Designators | Exact MPN | JLC part | Library | Live stock | Selection basis |
| --- | --- | --- | --- | ---: | --- |
| C2/C6 through C62 | CC0603FRNPO9BN221 | C519500 | Extended | 157,735 | 220 pF, 50 V, C0G, 0603, 1%; tighter than the required 2% |
| C65/C66 and C1/C5 through C61 | CL05B104KO5NNNC | C1525 | Basic | 47,288,853 | exact 100 nF, 16 V, X7R, 0402 part |
| (all rows above are now hand fitted, not factory placed) | | | | | |
| D1-D32 | BAR64-02V | C5295579 | Extended | 25,001 | JSCJ PIN diode, SOD-523, validated as described below |
| J1 | SM07B-GHS-TB(LF)(SN) | C495552 | Extended | 52,619 | exact JST 7-pin right-angle connector |
| L1/L3 through L31 | SDFL2012S100KTF | C1046 | Basic | 167,255 | 10 uH, 0805, 15 mA rating exceeds the 10.326 mA simulated bias |
| Q1/Q3 through Q31 | BSS123-7-F | C85107 | Extended | stocked | Diodes Incorporated SOT-23 part with exact datasheet and vendor SPICE model |
| Q2/Q4 through Q32 | BSS84-7-F | C85202 | Extended | 173,300 | Diodes Incorporated SOT-23 part with exact datasheet and vendor SPICE model |
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

Selective hand fitting does not remove the 50.47 EUR assembly large-size charge, so the choice was
binary: pay 82.02 EUR to place the 164 hybrid references, or order the bare PCB and populate all 165
by hand. **The decision is to hand populate.** Every package on this board is iron-reachable
(0402, 0603, 0805, SOT-23, SOD-523, SOIC-16, one JST), there is no fine pitch and nothing hidden, so
the only cost is time, against roughly 82 EUR of PCBA of which 50.47 EUR was pure size penalty.

Splitting the matrix into a dumb antenna board plus a small switch daughterboard would also avoid
the charge, but it puts connector inductance into all 16 resonant tanks, changes the ground return,
and forces the antenna board through Milestones 1 to 4 again. Hand populating gets the same saving
with no RF risk, so **that** split was rejected.

A different split was not. The objection above is specific to a boundary drawn between a loop and
its tuning capacitor; the per-line strip in [strip.md](strip.md) keeps the whole tank on the strip
and puts the connector on the far side of the 100 nF DC block, so the harness loads the shared bus
instead of joining sixteen resonators. `hardware/sim/strip_rf.py` measures that at 0.46 percent of
tuning against the same cells with the interconnect removed. The RF objection does not carry over;
the area and connector cost below is what does.

### Split sensing plane

Not quoted. This is the open item that decides between the two sensing architectures, and it needs
JLCPCB's live calculator rather than an estimate.

What is known without a quote:

| | matrix | split | note |
| --- | ---: | ---: | --- |
| Designs | 1 | 2 | one strip built 16 times, one spine built twice |
| Substrate | 90,000 mm2 | 174,640 mm2 | 1.94 times, structural |
| Fitted parts | 4.80 EUR | 15.16 EUR | 10.36 of the 10.36 increase is connectors |
| Unique JLC parts | baseline | **unchanged** | the split binds no new component type |
| Placed references | 165 | 200 | hand population gets worse, not better |
| Minimum useful order | 5 boards | 5 strips | a third of one set, so a respin wastes nothing |

The two effects that could reverse the area penalty are both size-driven and both already visible
in the matrix quote above: 17.74 EUR of fabrication and 50.47 EUR of assembly large-size charge. A
300 x 33 mm outline is long but narrow, and whether JLCPCB's size bands price it like a 300 x 300
board is exactly what nobody here can answer from a catalogue. Both boards are therefore marked
hand populated in `hardware/pcb/bom.py` pending that quote, which is the conservative direction and
the same decision the matrix board already took.

Eighteen JST GH cable assemblies (sixteen strip harnesses, two link harnesses) are purchased
accessories on no board BOM, like the hub's antenna pigtail. An order that forgets them is
incomplete. The connectors themselves are all SM07B-GHS-TB, C495552, already bound above, so the
split adds no feeder change.

The stocked JSCJ BAR64-02V replaces the unavailable NXP BAP64-02. Its conservative ngspice model
uses the JSCJ limits of 2.5 ohm maximum at 10 mA and 0.55 pF maximum at 1 V, 0.35 pF maximum at
5 V. With the exact Diodes MOSFET vendor models, the complete matrix validation passes with
13.540 MHz selected-cell resonance, 12.930 MHz loaded-bus resonance, 65.6 dB off/on suppression,
10.326 mA on-state bias, and 0.058 uA off-state bias. The replacement keeps the SOD-523 package
and pin polarity.

At the live first-unit prices, BAR64-02V is $0.0361 versus $0.4253 for the unavailable NXP match.
For JLCPCB's quoted 160-diode quantity that is a component-price reduction of about $62.27. The
1.5 ohm C22769 selection is $0.0047 versus $0.0232 for the initially matched RT0603 part, saving
about $1.67 across 90 pieces. These figures exclude setup, attrition, tax, and shipping.

The 10 uH choke remains Basic C1046. Its 15 mA rating exceeds the validated 10.326 mA bias, and using
an Extended alternative solely for extra margin would add another unique-component fee.

### Hub

The hub necessarily uses Extended ICs. Its safe public-stock substitutions now include the exact
PN5180 C3E package suffix, verified connector families, RF chokes, protection parts, exact feedback
values, and passives that meet the original dielectric, voltage, and footprint requirements. The
24.9 kohm R6 replacement differs by only 0.4%, inside the original 25 kohm 1% tolerance.

U4, Y1 and L2 are exact and externally available. U4 still needs JLCPCB Global Sourcing or another
controlled placement route because its exposed ground pads make it reflow-only.

- **L2, 74438357010:** DigiKey cut-tape order `732-11197-1-ND`, 16,892 observed in stock. It remains
  hand fitted and preserves the required 9.6 A saturation current and 13.5 milliohm maximum DCR.

Resolved:

- **U4, now ESP32-C6-MINI-1U-N4.** The C3-MINI-1U-N4X was two pieces short. The C6 is
  newer silicon (2023 against 2021) with 512 KB SRAM against 400 KB, in the identical 13.2 x 12.5 mm
  footprint, so it cost no layout work beyond the pin map. **Its pin map is not the C3's**: the C6
  is pin compatible only on power, ground, EN and UART0, and native USB moves to pins 17/18 while
  pin 21 becomes NC. DigiKey cut-tape order `1965-ESP32-C6-MINI-1U-N4CT-ND` had 732 units in
  observed European stock. C7558096 remains on the JLC upload BOM for matching, but its public
  quantity is not release evidence. Source the exact DigiKey part through JLCPCB Global Sourcing
  before assembly rather than accepting an automatic substitute.
- **Y1, now TXC 7M27100009 (C90919), 27.12 MHz in 3225.** 1,905 in stock at capture. It clears every
  line of PN5180 Table 142: 10 pF load against 10 pF typ, 60 ohm ESR against 100 ohm max, ± 10 ppm
  and ± 15 ppm over temperature against ± 100 ppm. Drive level sits at the 100 uW ceiling rather
  than below it, the one value without margin; R27/R28 are the knob if the assembled board needs it
  reduced.
- **C31/C32, now 15 pF (C1548, Basic).** Two equal caps present C/2 plus stray, so 15 pF presents
  about 10.5 pF against the required 10 pF. The previous 10 pF presented about 8 pF, about 41 ppm of
  pull, spending most of the ± 100 ppm budget on load error before the crystal's own tolerance.
  Basic, so the correction was free.

### Power board

The power board is factory reflowed as part of the light-bar panel. Its reverse-cell stage adds two
exact Extended parts: CSD25404Q3 is LCSC `C2865523`, and TLV7021DCKR is `C702120`. Both passed the
dated V1 availability check. Q1 uses TI's DQG land pattern because its continuous source clip does
not map cleanly to a generic footprint; U4 uses the stock DCK SC70-5 pattern. The Q1-only 0.15 mm
pad-gap rule matches TI's recommended land geometry without changing the board-wide 0.2 mm rule.

Boost compensation C13 is Fenghua 0402B223K500NT, `C1532`: 22 nF, 50 V, X7R, plus or minus 10
percent, 0402. JLCPCB listed it as Basic with more than one million assembly units on 2026-07-29.
The LCSC retail page simultaneously reported no stock, so the JLC assembly inventory is the source
for this build and the retail result is retained as a catalog-channel contradiction rather than
silently merged with it.

## Antenna, a purchased accessory

The ESP32-C6-MINI-1U has an external antenna connector rather than a PCB antenna, which makes the
antenna a plug-in part: a bad one costs a euro, not a hub board. It is on no BOM. Buy an adhesive
FPC 2.4 GHz antenna with a pigtail and record it with the display modules in
[boards.md](boards.md).

**The connector is MHF3 / W.FL / IPEX3, not U.FL.** A U.FL (MHF1) pigtail is physically larger and
will not mate. This is the easiest way to waste money on this build.

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

## Generated order files

`make pcb-fab` writes six files per board. The names say what to do with each, because uploading
the wrong one is a silent and expensive mistake.

| File | Use |
| --- | --- |
| `<board>_bom_all_parts.csv` | Reference. Every part with MPN, supplier, order code, footprint, cost and its assembly classification. The other files are views of this one. |
| `<board>_jlcpcb_upload_bom.csv` and `_cpl.csv` | **Upload these.** The build plan actually chosen for this board. |
| `<board>_jlcpcb_max_assembly_bom.csv` and `_cpl.csv` | The alternative: everything JLCPCB could place, excluding only what must be hand-fitted. Kept because the economics that made the other choice can change. |
| `<board>_self_solder_bom.csv` | What you buy and fit yourself. |

BOM and CPL always come as a pair: the BOM says which part goes on each designator, the CPL says
where it sits and at what rotation. `validate_assembly_designators` fails the export if the two
disagree, which is the classic assembly failure.

The two JLCPCB pairs differ only where a board is hand-populated. For the hub and the power board
they are nearly the same file. For the light bar, which is below JLCPCB's assembly size, and the
matrix, where the large-size assembly charge exceeded the rest of its PCBA, the upload pair is bare
copper and the max-assembly pair shows what the alternative would cost.
