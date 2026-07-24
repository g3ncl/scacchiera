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

- [x] Light bar schematic: `hardware/pcb/lightbar.py`, ERC clean, BOM totals 1.46 EUR in parts,
  spec in [hardware/lightbar.md](hardware/lightbar.md).
- [x] Matrix board schematic: `hardware/pcb/matrix.py`, ERC clean, BOM 6.02 EUR in parts, spec
  in [hardware/matrix.md](hardware/matrix.md).
- [x] Hub board schematic: `hardware/pcb/hub.py`, ERC clean, BOM 14.94 EUR in parts, spec in
  [hardware/hub.md](hardware/hub.md).

### M3: SPICE validation (per board)

Description: validate the schematic automatically in ngspice (`hardware/sim/`, invoked from the
test suite) against numeric limits recorded in `docs/hardware/criteria.yaml`.

DoD: an automatic test in `hardware/tests/` builds the board's SPICE deck, runs it, and passes
against its `criteria.yaml` limits, in the ordinary test suite. A board is not done while its only
evidence is an analytical formula; it needs a passing simulation.

- [x] Light bar SPICE validation: `hardware/tests/test_sim_lightbar.py` solves the resistor
  network extracted from the routed board in ngspice; worst supply-loop droop 24.6 mV against the
  100 mV limit in [hardware/criteria.yaml](hardware/criteria.yaml). Ran after layout because the
  copper supplies the resistances.
- [x] Matrix board SPICE validation: `hardware/tests/test_sim_matrix.py`, antenna inductance and
  AC resistance derived from the routed loop geometry (`hardware/sim/loop.py`). Selected cell
  resonates at 14.18 MHz, loaded 16-line bus at 13.70 MHz, off/on suppression 90 dB, steering
  bias 9.7 mA, all inside [hardware/criteria.yaml](hardware/criteria.yaml).
- [x] Hub board SPICE validation: `hardware/tests/test_sim_hub.py` drives the 16-cell bus
  through the PN5180 TX path; the selected loop's field peaks at 13.86 MHz at 60 mA per volt of
  drive. The 68 pF series match value came from this bench.

### M4: PCB layout, as code (per board)

Description: lay out the board from its schematic in code (SKiDL/KiCad-generation, `hardware/pcb/`),
not by hand in a GUI, so the layout stays reproducible and versioned like the schematic.

DoD: the layout is generated from code, DRC is clean, and it fits the board's envelope in
[functional/physical.md](functional/physical.md).

- [x] Light bar layout: `hardware/pcb/lightbar_layout.py` generates the routed 120 x 8.5 mm
  board, DRC clean (`make pcb-lightbar-drc`).
- [x] Matrix board layout: `hardware/pcb/matrix_layout.py` generates placement, antenna copper,
  and both-face ground pours; Freerouting autoroute (`make pcb-matrix-route`) plus a
  deterministic U1-serial escape (front-copper lanes with 0.4 mm vias threading the register's
  0.65 mm pitch, connected to the router's copper). `make pcb-matrix-drc` is clean: 0 violations,
  0 unconnected.
- [x] Hub board layout: `hardware/pcb/hub_layout.py` generates placement and both-face ground
  pours; Freerouting autoroute (`make pcb-hub-route`) plus an adaptive post-route closer that
  bridges any pad the router leaves open to its net's nearest copper (surviving the router's
  run-to-run variation). `make pcb-hub-drc` is clean: 0 violations, 0 unconnected.

## Definition of done for the rebuild

Every board from Milestone 1 has cleared Milestones 2 through 4. No board counts as done while its
schematic is unwritten, its SPICE validation is missing or failing, or its only PCB evidence is a
description rather than a laid-out, DRC-clean board. `docs/hardware/` and `docs/software/` return,
one file per board or subsystem, as each clears its milestones, mirroring `docs/functional/`'s
one-topic-per-file scoping.

## Status

All three boards are done. The light bar, matrix, and hub have each cleared Milestones 2 through
4: schematic (ERC clean, costed BOM), SPICE validation (passing ngspice test against
[hardware/criteria.yaml](hardware/criteria.yaml) in the ordinary suite), and PCB layout
(generated from code, `make pcb-<board>-drc` clean at 0 violations and 0 unconnected). Per the
rebuild's definition of done, every board from Milestone 1 has cleared Milestones 2 through 4,
so the hardware rebuild is complete. Firmware and the companion app have not started.
