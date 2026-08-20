# Ordering checklist

What to upload, in what order, with what options, to get a price for one complete board. Generated
artifacts live under `hardware/pcb/generated/<board>/` and are rebuilt with `make pcb-fab panel-fab`.
The step-by-step purchasing session across every shop is [order-runbook.md](order-runbook.md); this
file carries the rationale and the per-board detail.

**This is the upload checklist; the release authorisation lives in
[planning.md](../planning.md).** The scoped prototype-set release of 2026-08-19 authorises the
quad, light bars, power board and hub under its recorded conditions; the panel and the matrix stay
unorderable. Getting a price is not ordering.

## Read this first: which file to upload

Uploading the wrong file is the expensive mistake, so the names say what to do with each.

| File | What it is |
| --- | --- |
| `<board>_gerbers.zip` | **Upload for fabrication.** Twelve files: both copper, both mask, both paste, both silkscreen, edge cuts, PTH and NPTH drills, job file. |
| `<board>_jlcpcb_upload_bom.csv` + `_cpl.csv` | **Upload for assembly.** The plan actually chosen: factory places only what an iron cannot reach. Absent on a hand-populated board. |
| `<board>_jlcpcb_max_assembly_bom.csv` + `_cpl.csv` | The alternative, priced. Everything JLCPCB *could* place. Upload only to compare. |
| `<board>_self_solder_bom.csv` | What you buy from LCSC and fit yourself. Never uploaded. |
| `<board>_bom_all_parts.csv` | Reference only. **Never upload this one.** |

Never mix a BOM from one pair with a CPL from the other. `validate_assembly_designators` fails the
export if the two ever disagree, but it cannot stop you pairing them wrongly at the website.

## The three quotes

### 1. Sensing plane, bare

| | |
| --- | --- |
| Upload | `generated/quad/quad_gerbers.zip` |
| Quantity | **5** (four is a plane, the fifth is the spare) |
| Dimensions | 300 x 140 mm, 2 layers |
| Thickness | **0.6 mm** |
| Assembly | **none** |
| Surface finish | **OSP**, not HASL and not ENIG. See [Surface finish](#surface-finish-which-is-not-the-same-on-every-board) below |

0.6 mm is settled: priced 2026-08-02 against 0.8 and 1.0 mm at this outline and quantity and all
three cost the same, so take the thickness the design wants. HASL is not offered at 0.6 mm at all,
and ENIG's nickel underplate costs antenna Q, which is the quantity this board exists to measure.

### 2. Light bars and power board, ordered separately

**The panel is broken and must not be ordered.** See the defect below. Until it is fixed, order its
two constituent boards as separate fabrication items:

| | Light bars | Power board |
| --- | --- | --- |
| Upload, fabrication | `generated/lightbar/lightbar_gerbers.zip` | `generated/power/power_gerbers.zip` |
| Upload, assembly | none, hand populated | `power_jlcpcb_upload_bom.csv` + `_cpl.csv` |
| Outline | 120.0 x 8.5 mm | 90.0 x 32.0 mm |
| Thickness | 1.0 mm | 1.0 mm |
| Quantity | 5 (you need 2) | 5 |

Both are DRC-clean and both are in `make check`, unlike the panel. The power pair is 18 rows and 41
placements, 3 Extended.

Do not budget an X-ray line for the power board. This checklist previously predicted one because the
board carries two QFNs and the hub was charged 2.85 EUR for it; the power quote came back with no
X-ray line at all. Treat X-ray as a hub-class charge tied to pin count or hidden pad arrays, and as
something to quote rather than to model ([cost.md](cost.md)).

Ordering the two boards separately costs one extra fabrication order rather than the engineering fee
this checklist once assumed: both small boards came back on promotional pricing with no engineering
fee. What panelising genuinely saves is on the assembly side, about 8.40 EUR of duplicated setup and
stencil, and it needs a panel that works.

#### The panel defect

`hardware/pcb/generated/panel/panel_gerbers.zip` is **not orderable**. Two independent geometry
faults, both found 2026-08-02 after the file had already been listed here as uploadable:

1. **Edge_Cuts contains the panel border *and* all three sub-board outlines, as closed rectangles.**
   Sixteen segments where there should be four plus tab-broken separations. A fabricator and a
   gerber viewer both read nested closed contours as **cutouts**, so the three boards are milled
   completely free and the panel is a frame with three board-shaped holes. That is the "negative"
   appearance. Cause: `panel.py::_translate_and_append` copies each source board's `GetDrawings()`,
   which includes its Edge_Cuts.
2. **No tab connects the boards to the frame.** All four mouse bites sit in the two gutters
   *between* boards, at y = 14.50 and y = 25.00. Even with correct outlines the whole three-board
   cluster would be attached only to itself and would drop out of the panel.

**How it survived:** the panel is not in `make check`. Every other board has a `pcb-<board>-drc`
target in the gate; the panel has only `make panel`, and its own DRC report sat on disk unread. DRC
would not have caught these anyway, since it does not validate panelisation, but nothing was ever
looking. The report's 101 findings are all the benign `lib_footprint_issues` class the standalone
CLI produces without a footprint table, and the 18 unconnected items are expected on a board with no
netlist, so even a reader would have had to look past the noise.

**Fixing it properly** means drawing the sub-board separations with gaps at the tab positions rather
than copying closed outlines, adding tabs from the cluster to the frame, and putting the panel in
the verification gate so this cannot recur. That is real work and it is not worth blocking an order
for: panelising saves roughly one engineering fee.

### 3. Hub

| | |
| --- | --- |
| Upload, fabrication | `generated/hub/hub_gerbers.zip` |
| Upload, assembly | `generated/hub/hub_jlcpcb_upload_bom.csv` + `hub_jlcpcb_upload_cpl.csv` |
| Quantity | 5 |
| Dimensions | 162 x 46 mm, 2 layers |
| Thickness | 1.0 mm |
| Assembly | Economic PCBA |

25 rows, 67 placements, collapsing to **20 unique LCSC parts** because JLCPCB merges by part number.
Four are Extended and reflow-only: J1 (USB-C), U3 (PN5180), U4 (the module), Y1 (the 27.12 MHz
crystal).

Two of those need attention at order time, and both were seen in the 2026-08-02 quote:

- **U4 is not stocked at LCSC at all.** The bound ESP32-C6-MINI-1U-N4 (C7558096) shows a shortfall,
  not a dip. Substitute **ESP32-C6-MINI-1U-H4, C20627095**: the Espressif datasheet already filed
  covers both in one document, Table 1-2, and gives them the same 4 MB Quad SPI flash, the same
  13.2 x 12.5 x 2.4 mm body and pinout, and the H4 a wider **-40 to 105 C** grade against the N4's
  85. Strictly better, in stock, about 1.20 EUR more per unit.
- **J1 was rejected by the matcher** and left in Unselected Parts with no reason given. **A hub
  without J1 has no power input**, and its pads are under the body so no iron fixes it afterwards.
  Resolve before ordering assembly; see the power-only USB-C candidate in
  [jlcpcb-sourcing.md](jlcpcb-sourcing.md), which becomes attractive precisely when J1 has to change
  anyway.

**Check the assembly placement preview part by part before paying**, with particular attention to
J1, U3 and U4. JLCPCB's desktop DFM tool overlays its own lead models per the CPL and flagged
pin-to-pad misalignment concentrated on those three; that is the tool's part origin and rotation
conventions disagreeing with the KiCad footprints, not a pad error, but the same disagreement is
exactly what puts a part down rotated at assembly. The order preview renders their model on these
pads; rotate or nudge any body that sits wrong there.

#### The desktop DFM report on the hub, reconciled

JLCPCB's desktop DFM tool (run 2026-08-20 on `hub_gerbers.zip`) raises dangers that `make pcb-dfm`
does not. Each was checked against the published capabilities and the gerbers themselves; none
needs a board change:

| Report says | What it is | Verdict |
| --- | --- | --- |
| Slot width 0.6 mm, danger x4 | The USB-C shield slots of the GCT USB4105 land pattern | Within capability: JLCPCB's published floor for plated slots on 2 layers is 0.5 mm |
| Mask opening exposing trace, danger x2 at 0.03 mm | Same-net copper passing the shield slot openings | The tool reads gerbers without nets. The mask is exported 1:1 and the copper DRC passes, so foreign-net copper cannot sit closer than the copper clearance |
| THT to SMD 0.85 mm, danger x4 | The USB-C's shield slots against its own pins | Fixed by the connector's package drawing; JLCPCB assembles C3020560 from its own library |
| Annular ring 0.15 mm, warning x100 | Every via, 0.3 mm drill in 0.6 mm pad | The standard-tier via the order form selects; 0.15 mm is the published absolute minimum |
| Silkscreen dangers, 0.12 mm line width | Refdes text near pads and openings | Silk over openings is clipped by the fab as a matter of course; lines under 0.15 mm print thin |
| SMT pin and lead dangers, about 150 | Tool lead models against the footprints of J1, U3, U4 | Origin and rotation conventions, not pad geometry; caught at the placement preview above |
| PCB size 18.2 x 4.6 cm | The tool adds its own margin | Edge_Cuts measures exactly 162 x 46 mm and no layer content extends past the outline |

## What the upload pairs deliberately exclude

**The upload pair is the plan, not the inventory.** Anything an iron can reach is hand-fitted and
therefore absent from it, which is what keeps the feeder bill at 4 rows instead of 19.

| Board | Upload pair | Max-assembly pair | Feeder fees, plan vs alternative |
| --- | --- | --- | ---: |
| hub | 25 rows, 67 placements | 40 rows, 90 placements | **10.80** vs 51.30 EUR |
| power | 18 rows, 41 placements | 28 rows, 52 placements | **8.10** vs 35.10 EUR |
| quad | none, hand populated | 11 rows, 44 placements | 0 vs 16.20 EUR |
| lightbar | none, below assembly size | 3 rows, 16 placements | 0 |
| matrix | superseded, do not order | 11 rows, 165 placements | 0 |

Uploading the max-assembly pairs by mistake costs **67.50 EUR of feeder changes** the design does
not intend. That is the single most expensive slip available at the ordering step.

## Do not order

- **`generated/matrix/`** in any form. The 300 x 300 mm monolith is the superseded baseline
  ([matrix.md](matrix.md)); the quad replaced it. It is still exported because it is the recorded
  comparison, not because it is orderable.
- **`generated/panel/`** in any form, until the Edge_Cuts and tab defects above are fixed. The
  boards it carries are ordered individually instead.

## What is not in any of these files

Purchased accessories on no board BOM. An order that forgets them is incomplete; see
[boards.md](boards.md) and [cost.md](cost.md).

- Four JST GH cable assemblies, **all the same length** (`quad_geometry.HARNESS_LENGTH_MM`, 100 mm)
- Two ER-OLEDM3.12-1W display modules, from EastRising
- 32 piece tags
- The protected cell assembly and its Micro-Fit mating hardware
- One 2.4 GHz FPC antenna, **MHF3 / W.FL / IPEX3, not U.FL**
- Every part in the four `_self_solder_bom.csv` files, 270 references, from LCSC

**Combine the LCSC order with the JLCPCB order into one shipment**: place both, then ask
`support@lcsc.com` to combine them, or bind the JLCPCB order during LCSC checkout. Same currency and
customer ID, and it must happen before either ships because a combined order cannot be split.

## Options to set in the order form

The board files carry no explicit stackup, so KiCad defaults apply and these are chosen in the order
form rather than read from the upload:

- **Copper weight:** 1 oz.
- **Layers:** 2, on every board.
- **Minimum via:** 0.3 mm drill into 0.6 mm pad on every shipping board, which is the standard tier.

### Surface finish, which is not the same on every board

**HASL is not offered at 0.6 mm**, so the sensing plane has to choose between OSP and ENIG. That
turns out to be a real engineering choice rather than a cost one, and it goes the opposite way from
the other boards.

| Board | Finish | Why |
| --- | --- | --- |
| **quad (sensing)** | **OSP** | Lowest RF loss, and the antenna is the whole point of the board. |
| hub | ENIG preferred, HASL acceptable | QFN-40 reader and a module with a ground-pad array; flatness is worth more here than anywhere else. |
| panel | ENIG preferred, HASL acceptable | The power board's two QFNs are the only fine pitch on it. |

**Why OSP on the sensing plane, positively rather than by elimination.** ENIG is
gold over a **nickel underplate 3 to 6 um thick**, and nickel-phosphorus has a resistivity around
70 uohm-cm, roughly forty times copper's, and is magnetic. At 13.56 MHz the skin depth in that
nickel is about 3.6 um, *comparable to the layer itself*, so a real fraction of the antenna current
would run in the lossy layer instead of the copper beneath it. That directly costs loop Q, which is
the single quantity the [test article](test-article-quad.md) exists to measure. OSP is bare copper
under a thin organic film and has the lowest loss of any common finish.

So the cheapest option is also the right one here, which does not happen often. Note this is
specifically OSP against **ENIG**; the usual advice that NFC boards prefer ENIG is advice against
*HASL*, whose thick uneven solder coat is worse than either.

**What OSP costs, and why it does not bite here.** OSP has a shelf life of roughly six to twelve
months and degrades with handling and humidity, and it is an organic film rather than a conductive
surface. Neither matters for this board:

- The loop terminals are through-hole pads, so the VNA connects through a soldered pigtail rather
  than a probe touched to a coated pad. Soldering removes the film where contact is needed.
- The board is bare copper for measurement first and populated later. **Solder the 176 joints
  reasonably soon after delivery and store the boards dry**, and do not order the sensing plane
  years before building it.

If the plane is ever going to sit for a long time before assembly, ENIG is the finish that tolerates
that, and the cost is measurable antenna Q.
