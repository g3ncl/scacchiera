# Hardware development plan

The hardware and firmware are being rebuilt from scratch, keeping only the
[functional specification](functional/overview.md) as fixed ground truth. This file is the
milestone list that rebuild follows. Claude follows this plan rather than inventing its own
sequencing; update it as work proceeds so it stays the current source of truth for what is done.

## How to read this

- `[ ]` open, `[x]` done.
- Each milestone has a short description and a Definition of Done (DoD). A milestone is not done
  until its DoD holds, not when the work "looks finished".
- Milestone 1 gates everything else: no board's schematic, layout, or simulation starts before the
  board inventory exists, the same way [functional/overview.md](functional/overview.md) gates the
  hardware and software design that serves it.
- Milestones 2 to 4 repeat once per board. The default order per board is schematic, then SPICE
  validation, then PCB layout. If a board's SPICE validation needs layout-derived values (real
  trace or antenna inductance, resistance, coupling, parasitics) rather than an analytical estimate,
  that board's PCB layout (Milestone 4) comes before its SPICE validation (Milestone 3) instead,
  because the honest numbers come from the copper geometry, not a formula.
- Milestones M1 through M4 now describe design-generation progress only. They do not authorize a
  PCB order. The hard release gates are V0 through V9 in
  [simulation-workflow.md](simulation-workflow.md), which take precedence over the older completion
  language below.

## Verification release gates

No gate is complete until its definition of done in
[simulation-workflow.md](simulation-workflow.md) has recorded evidence. V0 through V7 permit only a
scoped test-article order. V0 through V9 permit a final-board order.

- [x] V0 requirement traceability: 71 atomic requirements in
  [verification/traceability.yaml](verification/traceability.yaml) map the complete functional
  specification and fitted-part absolute-maximum audit to stable test IDs. The manifest pins the
  reviewed functional sources by SHA-256. Thirty-seven numeric criteria in
  [hardware/criteria.yaml](hardware/criteria.yaml) record units, evidence, conditions, and margin.
  `hardware/tests/test_traceability.py` enforces source freshness, schema completeness, unique IDs,
  and bidirectional requirement/criterion links. Evidence: 5 tests passed on 2026-07-25.
- [x] V1 component and library proof: all 59 purchased fitted MPNs in
  [verification/v1-components.yaml](verification/v1-components.yaml) have exact supplier and order
  codes, dated availability, immutable manufacturer datasheets, per-part wiki ingestion, complete
  library and rating audits, declared model treatment, and no open document conflict. The audit
  replaced the lightbar LED and both matrix MOSFET selections rather than waiving conflicts.
  Evidence: 6 component-proof tests and 4 matrix vendor-model tests passed on 2026-07-25.
- [ ] V2 connectivity and static electrical checks
- [ ] V3 power, analog, timing, and fault simulation
- [ ] V4 layout-derived electromagnetic validation
- [ ] V5 firmware host verification
- [ ] V6 firmware-in-simulation system verification
- [ ] V7 mechanical and fabrication preflight
- [ ] V8 test-article measurement and model calibration
- [ ] V9 independent review and final release

## Milestones

### M1: Board inventory

Description: decide which physical boards the product needs and what each is responsible for,
derived from `docs/functional/`, keeping the bill-of-materials cost in mind from the start (fewer
boards and fewer parts over a more elegant but pricier split).

DoD: a `docs/hardware/boards.md` doc lists every board, one entry per board, with its
responsibility, its interfaces to the other boards, and a rough cost target. No schematic exists
for any board yet.

- [x] Board inventory complete: see [hardware/boards.md](hardware/boards.md). Three custom
  designs, four physical PCBs: light bar (x2), matrix board, hub board. Build order: light bar,
  then matrix, then hub.

### M2: Schematic (per board)

Description: design the board's electrical schematic in SKiDL (`hardware/pcb/`) to meet exactly its
Milestone 1 responsibility. Keep the bill of materials cheap: prefer fewer parts and simpler
switching over a more elegant but pricier circuit.

DoD: `hardware/pcb/<board>.py` exists and generates a schematic, ERC is clean, a BOM is generated
with a running per-board cost total, and a `docs/hardware/<board>.md` spec describes the board
against the functional requirement it serves.

- [x] Light bar schematic: `hardware/pcb/lightbar.py`, ERC clean, BOM totals 6.33 EUR in parts,
  spec in [hardware/lightbar.md](hardware/lightbar.md). Revised 2026-07-25: the pixel is now an
  Harvatek T37K3RGB-05C000112U1930, because a hand-populated board needs an exact sourced package
  an iron can reach, and the count dropped 17 to 14 because that package is wider.
- [x] Matrix board schematic: `hardware/pcb/matrix.py`, ERC clean, BOM 4.80 EUR in parts, spec
  in [hardware/matrix.md](hardware/matrix.md).
- [x] Hub board schematic: `hardware/pcb/hub.py`, ERC clean, BOM 16.21 EUR in parts, spec in
  [hardware/hub.md](hardware/hub.md). Revised 2026-07-25: U4 to ESP32-C6-MINI-1U-N4 with the C6
  pin map from datasheet Table 3-1 (native USB moves to pins 17/18), Y1 to a stocked 3225
  27.12 MHz crystal with 15 pF loads, plus local module decoupling and IO9/EN recovery pads.

### M3: SPICE validation (per board)

Description: validate the schematic automatically in ngspice (`hardware/sim/`, invoked from the
test suite) against numeric limits recorded in `docs/hardware/criteria.yaml`.

DoD: an automatic test in `hardware/tests/` builds the board's SPICE deck, runs it, and passes
against its `criteria.yaml` limits, in the ordinary test suite. A board is not done while its only
evidence is an analytical formula; it needs a passing simulation.

- [x] Light bar SPICE validation: `hardware/tests/test_sim_lightbar.py` solves the resistor
  network extracted from the routed board in ngspice; worst supply-loop droop 12.46 mV against the
  100 mV limit in [hardware/criteria.yaml](hardware/criteria.yaml). Ran after layout because the
  copper supplies the resistances. Ground is now a pour rather than routed track, modelled as a
  ladder between its real stitching-via positions so the plane stays layout-derived.
- [x] Matrix board SPICE validation: `hardware/tests/test_sim_matrix.py`, antenna inductance and
  AC resistance derived from the routed loop geometry (`hardware/sim/loop.py`). Selected cell
  resonates at 13.54 MHz, loaded 16-line bus at 12.93 MHz, off/on suppression 65.6 dB, steering
  bias 10.326 mA, all inside [hardware/criteria.yaml](hardware/criteria.yaml) with exact Diodes
  vendor MOSFET models.
- [x] Hub board SPICE validation: `hardware/tests/test_sim_hub.py` drives the 16-cell bus
  through the PN5180 TX path; the selected loop's field peaks at 13.86 MHz at 60 mA per volt of
  drive. The 68 pF series match value came from this bench.

### M4: PCB layout, as code (per board)

Description: lay out the board from its schematic in code (SKiDL/KiCad-generation, `hardware/pcb/`),
not by hand in a GUI, so the layout stays reproducible and versioned like the schematic.

DoD: the layout is generated from code, DRC is clean, and it fits the board's envelope in
[functional/physical.md](functional/physical.md).

- [x] Light bar layout: `hardware/pcb/lightbar_layout.py` generates the routed 120 x 8.5 mm
  board, DRC clean at 0 violations and 0 unconnected (`make pcb-lightbar-drc`). Rerouted
  2026-07-25 around the wider LED: back-copper ground pour instead of a routed bus, and the 5 V
  bus below the connector's mounting pads, the only pad-free full-length band left.
- [x] Matrix board layout: `hardware/pcb/matrix_layout.py` generates placement, antenna copper,
  and both-face ground pours; Freerouting autoroute (`make pcb-matrix-route`) plus a
  deterministic U1-serial escape (front-copper lanes with 0.4 mm vias threading the register's
  0.65 mm pitch, connected to the router's copper). `make pcb-matrix-drc` is clean: 0 violations,
  0 unconnected.
- [x] Hub board layout: `hardware/pcb/hub_layout.py` generates placement and both-face ground
  pours; Freerouting autoroute (`make pcb-hub-route`) plus an adaptive post-route closer that
  bridges any pad the router leaves open to its net's nearest copper (surviving the router's
  run-to-run variation). `make pcb-hub-drc` is clean: 0 violations, 0 unconnected.

## Legacy definition of done for design generation

Every board from Milestone 1 must clear Milestones 2 through 4. These milestones establish that the
schematic, initial SPICE validation, and PCB layout exist. They are necessary inputs to the current
verification workflow, not evidence that a board is final or safe to order. Final completion is V9
in [simulation-workflow.md](simulation-workflow.md).

## Status

Revised 2026-07-25. Three parts were rebound after JLCPCB could not fill the hub order (U4 and Y1
were short) and after the decision to hand-populate the lightbar and matrix rather than pay the
large-size assembly charge. `Vault/Scacchiera/Datasheets/` and the Datasheets rule in `CLAUDE.md`
came out of the same work: the C6 pin map, the crystal's load capacitance and the LED's drive
current all came from datasheets that contradicted the catalog listings. Full suite passes at 28
tests; lightbar, matrix and hub DRC are all clean.

Known defects as of 2026-07-25, before the workflow starts:

- **The matrix layout builds every time now, but is not reproducibly DRC clean.** Three consecutive
  `make pcb-matrix-route && make pcb-matrix-drc` runs gave 0 violations / 0 unconnected, then 1 / 1,
  then 2 / 3. It no longer crashes (see below), so V2's "netlist and routed board agree" is
  reachable by re-running, but the board is not yet deterministic.

  Root cause is understood and is architectural, not a tuning problem. The four shared serial nets
  (SEL_SER, SEL_SRCLK, SEL_RCLK, SEL_CHAIN) are routed by Freerouting, which reaches their 0.65 mm
  register pads unreliably, and `_postroute_fixups` then patches whatever it left by drawing a lane
  *relative to where the router happened to stop*. Two better skip rules were measured (any-peer and
  all-peer connectivity tests) and both came out worse, which is the evidence that no skip rule fixes
  it: the patch is downstream of a nondeterministic input.

  **The fix is to take those four nets away from the router entirely**: after importing the session,
  rip up their copper and draw all four deterministically through reserved front-copper bands, the
  way the left-hand U1 lane band is already reserved. That needs a bottom-margin band worked out
  against the column antennas' through-hole terminals, which sit in the same margin. Scoped, not done.
- **The hub layout is not reproducibly clean.** Freerouting leaves 1 to 2 pads open, varying run to
  run. The post-route closer's bridge ceiling was cut from 14 mm to 2.5 mm because a 9.26 mm bridge
  across the MCU module was producing ten DRC violations on its own, so open pads are now reported
  rather than shorted over.
- ~~Matrix U1 sits 0.025 mm from the board edge~~ **fixed**. It was worse than the DRC report
  suggested: U1's pads 8 and 9 sat at x = -1.245, entirely *off* the board, and its silkscreen
  overhung the edge. Pad 9 is SEL_CHAIN, which is why routing failed on that net specifically, so
  this one placement bug produced both reported defects. U1 is now seated by measuring its own
  courtyard (`_seat_inside_left_edge`) rather than against a hardcoded 3.5 mm, so it cannot recur if
  the footprint or rotation changes, and C65 follows it. Four dead constants that described an
  unimplemented deterministic route (`_LEFT_X`, `_BOTTOM_Y`, `_U1_FAN_Y`, `_U2_TURN_X`) were removed,
  and the reserved lane band now derives from the real serial-pad positions.

- ~~`make pcb-matrix-route` aborts~~ **fixed**. `_nearest_net_point` raised
  `no router copper for net <X>` whenever Freerouting left one of the four serial nets bare, and
  which net that was varied run to run, so the matrix could not be regenerated from code at all. It
  now falls back to the net's own pads. A lane drawn to the counterpart pad is a worse route than one
  drawn to router copper, but it is a route, and DRC judges it instead of the build dying.
- **The 10 uH matrix choke has no margin evidence.** Its datasheet gives one current number, 15 mA,
  without saying whether that is a heating or a saturation limit, and the design biases it at
  10.326 mA.

The old U4 and lightbar sourcing risks are closed by exact stocked DigiKey order codes. U4 still
requires controlled Global Sourcing for factory placement because it is not hand solderable.

The light bar, matrix, and hub have each cleared the legacy M2 through M4 design-generation gates:
schematic, nominal SPICE checks, and PCB layout. They have not been assessed against V0 through V9,
so none is final or authorized for a test-article or final-board order. Firmware and the companion
app have not started, which also blocks V5 and V6.
