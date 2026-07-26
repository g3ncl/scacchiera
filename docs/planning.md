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

- [x] V0 requirement traceability: 80 atomic requirements in
  [verification/traceability.yaml](verification/traceability.yaml) map the complete functional
  specification and fitted-part absolute-maximum audit to stable test IDs. The manifest pins the
  reviewed functional sources by SHA-256. Forty-two numeric criteria in
  [hardware/criteria.yaml](hardware/criteria.yaml) record units, evidence, conditions, and margin.
  `hardware/tests/test_traceability.py` enforces source freshness, schema completeness, unique IDs,
  and bidirectional requirement/criterion links. The 2026-07-26 revision specifies runtime,
  5 V/2 A charge-time, fallback, protection, and cell-temperature requirements without requiring
  USB Power Delivery. Evidence: 5 tests passed on 2026-07-26.
- [ ] V1 component and library proof: the former 59-part proof remains valid for the lightbar and
  matrix, but the hub portion is reopened by the new commercial 5 V boundary. The selected PiSugar
  3 Plus manufacturer documents, I2C register map, safety instructions, STEP assembly, and supplied
  cell UN 38.3 report are filed in the vault. The AP63203WU-7 buck, SWPA5045S4R7MT inductor,
  AP22811AW5-7 input switch, TLV7042DGKR comparator, and NTCLE317E4103SBA cell sensor are now exact
  selections with immutable manufacturer data sheets. Their schematic binding, PiSugar harness,
  library audit, ratings audit, and model classification remain before this gate can pass again.
  Historical evidence follows:
  [verification/v1-components.yaml](verification/v1-components.yaml) have exact supplier and order
  codes, dated availability, immutable manufacturer datasheets, per-part wiki ingestion, complete
  library and rating audits, declared model treatment, and no open document conflict. The audit
  replaced the lightbar LED and both matrix MOSFET selections rather than waiving conflicts.
  Evidence: 6 component-proof tests and 4 matrix vendor-model tests passed on 2026-07-25.
- [ ] V2 connectivity and static electrical checks: the lightbar and matrix remain valid. The hub
  schematic and route are superseded by the commercial 5 V boundary and must be regenerated and
  re-reviewed. Historical evidence follows: clean generation runs full SKiDL and KiCad ERC,
  imports reviewed deterministic routing sessions, and runs PCB DRC with schematic parity on all
  three boards. [verification/v2-static.yaml](verification/v2-static.yaml) records the four
  reviewed generated-schematic warning classes, every datasheet-traced no-connect, and the zero
  finding board results. Four focused tests cover both ends of every cable, exact USB-C pins,
  startup pulls, recovery pads, enable/reset nets, and exposed pads. Evidence: `make check` passed
  with 43 tests, mypy clean, and all boards at 0 violations, 0 unconnected, and 0 parity issues on
  2026-07-26.
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
- [ ] Hub board schematic: the previous MCP73871 design in `hardware/pcb/hub.py` is superseded. It
  must accept the PiSugar 3 Plus regulated 5 V and I2C interface, implement the selected AP63203
  buck and independent analog cell-temperature cutoff, and distribute protected 5 V to the light
  bars before this milestone closes again. The subsystem boundary is
  in [hardware/power-subsystem.md](hardware/power-subsystem.md), and hub rationale is in
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
- [ ] Hub board SPICE validation: the existing RF-only bench still drives the 16-cell bus
  through the PN5180 TX path; the selected loop's field peaks at 13.86 MHz at 60 mA per volt of
  drive and preserves useful RF evidence, but it does not validate the replacement 5 V-to-3.3 V
  buck, current limiter, cell-temperature interlock, startup, shutdown, or fault behavior. PiSugar
  charge and handover behavior is measured at V8 rather than represented by an invented internal
  model. The 68 pF series match value came from this bench.

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
  and both-face ground pours. The reviewed route session excludes four deterministic serial nets,
  and the Q24 rail escape is deterministic as well. `make pcb-matrix-drc` is reproducibly clean:
  0 violations, 0 unconnected, and 0 schematic parity issues.
- [ ] Hub board layout: the existing `hardware/pcb/hub_layout.py` route belongs to the superseded
  charger and must be replaced after the simplified 5 V-input schematic is complete. Its historical
  placement, routing, and clean DRC are not current release evidence.

## Legacy definition of done for design generation

Every board from Milestone 1 must clear Milestones 2 through 4. These milestones establish that the
schematic, initial SPICE validation, and PCB layout exist. They are necessary inputs to the current
verification workflow, not evidence that a board is final or safe to order. Final completion is V9
in [simulation-workflow.md](simulation-workflow.md).

## Status

Revised 2026-07-26. V0 passes with ordinary 5 V/2 A charging and bounded recharge time included.
The PiSugar 3 Plus is the selected purchased battery subsystem. V1 and V2 remain open for the hub
because the former MCP73871 schematic and route do not implement this boundary. The lightbar and
matrix retain their passing component, static, simulation, and layout evidence. The 10 uH matrix
choke's ambiguous 15 mA datasheet rating remains a V3 corner and fault-model concern, not a waived
check.

No board is authorized for a test-article order until V3 through V7 pass. Firmware and the companion
app have not started, so V5 and V6 remain open.

The named V8 article is the exact production-intent PiSugar 3 Plus and supplied cell described in
[hardware/power-subsystem.md](hardware/power-subsystem.md). V8 must measure charge time, runtime,
cable handover, thermals, I2C behavior, and NFC performance in the representative ventilated
enclosure. The module does not measure cell temperature, so an independent fail-safe charge
interlock remains mandatory and open. No purchase or test-article order is authorized until V3
through V7 pass.
