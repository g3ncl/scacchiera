# Simulation and verification workflow

This document defines the evidence required before a board may be called final or sent to a PCB
manufacturer. Its purpose is to make hardware confidence reproducible rather than dependent on a
reviewer's intuition. Passing ERC, DRC, or one nominal SPICE operating point is necessary but is
not sufficient.

## Rule

PCB ordering is blocked by default. Every applicable milestone below must have passing automated
evidence before a design is finalized or a fabrication package is released. A waived, missing,
provisional, guessed, or undocumented result is a failure, not a warning.

There are two release types:

- A **test-article release** orders only the minimum hardware needed to measure a risk that cannot
  be resolved in software. It must pass milestones V0 through V7 and must state the exact unknown
  it will measure. It is a prototype, never a finished board.
- A **final-board release** orders the intended assembled design. It must pass V0 through V9,
  including calibration of simulation models against test-article measurements and an independent
  review.

An agent must not describe a board as done, production-ready, validated, or safe to order until the
corresponding release gate passes. If evidence is incomplete, report the blocking milestone and
stop.

## Evidence classes

Every acceptance claim in `docs/hardware/criteria.yaml` and every release decision must use one of
these evidence classes:

- **Datasheet:** a limit or requirement quoted from a filed manufacturer datasheet, with its
  section or table recorded in the component's wiki source summary.
- **Derived:** a deterministic calculation whose inputs all have Datasheet or Measured evidence.
- **Simulated:** a passing automated test using the production connectivity and a documented model.
- **Measured:** a repeatable test on a named test article with the instrument, setup, raw result,
  and uncertainty recorded.
- **Assumed:** an unverified value or behavior. Assumed evidence blocks both release types when it
  can affect function, safety, damage, fabrication, assembly, or firmware recovery.

Typical values are not worst-case limits. A typical-only parameter must be swept over a justified
range and remains Assumed until its range is supported or measured.

## Single sources of truth

Verification must exercise the artifacts that will be manufactured and flashed:

- SKiDL is the authoritative schematic connectivity.
- The routed KiCad PCB is the authoritative copper geometry and footprint placement.
- The ESP-IDF build output is the firmware executed in system simulation.
- `docs/functional/` is the authoritative product behavior.
- `docs/hardware/criteria.yaml` contains numeric pass and fail limits, with their evidence source.
- Fabrication ZIP, BOM, CPL, firmware binary, and test results belong to one immutable release
  candidate identified by a Git commit and file hashes.

Do not maintain a second hand-written representation of connectivity. Generate SPICE connectivity,
electromagnetic geometry, virtual-hardware wiring, BOM, and CPL from the authoritative design, or
automatically prove parity with it.

## Required toolchain

The reference toolchain is:

- SKiDL and KiCad CLI for schematic generation, ERC, PCB DRC, schematic-to-PCB parity, fabrication
  exports, and 3D export.
- pytest and mypy for executable acceptance tests and typed verification code.
- ngspice for DC, AC, transient, fault, parameter-corner, and statistical circuit analysis.
- openEMS with its Python interface for three-dimensional electromagnetic extraction from the
  routed RF copper and surrounding materials.
- scikit-rf, or an equivalent scripted Touchstone workflow, for combining extracted RF networks
  with matching and receiver networks.
- ESP-IDF host tests with Unity and CMock for firmware logic and driver isolation.
- Wokwi ESP32-C6 simulation with custom SPI and I2C device models for execution of the real firmware
  binary against virtual peripherals.
- build123d and KiCad STEP exports for deterministic enclosure, connector, and keepout checks.

An equivalent tool may replace one of these only when it produces at least the same automated
evidence. The replacement and reason must be recorded in `docs/planning.md`.

## Milestones

Milestones are sequential gates. A later milestone cannot compensate for an earlier failure.

### V0: Requirement traceability

Map every relevant statement in `docs/functional/` and every component absolute maximum to one or
more tests. Record numeric pass limits in `docs/hardware/criteria.yaml`. Each limit must name its
Datasheet, Derived, or Measured source and include deliberate margin.

Definition of done:

- Every electrical, sensing, interface, power, thermal, recovery, and mechanical requirement has a
  test identifier.
- Every numeric criterion has units, source, operating conditions, and margin.
- No test merely checks that a result is nonzero or inside a broad arbitrary band.

### V1: Component and library proof

Audit every fitted part before using it in simulation or fabrication.

Definition of done:

- The exact MPN and order code are bound and available.
- The immutable manufacturer datasheet is filed and ingested according to the Datasheets workflow.
- Symbol pin numbers, names, electrical types, exposed pads, no-connect pins, footprint pad numbers,
  package dimensions, polarity, assembly side, and CPL rotation are checked against the datasheet.
- Voltage, current, power, temperature, tolerance, derating, startup state, and absolute maximums
  used by the design are recorded.
- A vendor simulation model is used where one exists. A substitute model documents every fitted
  parameter, its source, valid operating region, and conservative sweep range.
- Conflicting documentation or a provisional model blocks release.

### V2: Connectivity and static electrical checks

Generate fresh schematics and boards from a clean workspace. Run SKiDL ERC, KiCad ERC, KiCad DRC,
and KiCad PCB DRC with `--schematic-parity` and exit-on-violation behavior.

Definition of done:

- Zero unreviewed ERC errors or warnings, DRC violations, and unconnected items.
- Every reviewed no-connect is enumerated in code and traced to a datasheet.
- Connector pin order and cable mirroring are tested at both ends.
- Boot straps, reset, programming recovery, power-off defaults, bus pullups, and enable pins are
  checked against the relevant datasheets.
- The generated netlist and the routed board agree.

### V3: Power, analog, timing, and fault simulation

Simulate the complete power path and every analog circuit from its real connectivity. Use exhaustive
corner sweeps for bounded tolerances. Fixed-seed Monte Carlo may supplement corner testing but cannot
replace it.

Required cases include, where applicable:

- Minimum and maximum USB voltage, battery voltage, temperature, load, tolerance, capacitor bias
  derating, ESR, and inductor loss.
- Cold start, warm reset, power-off discharge, USB insertion and removal, battery insertion and
  removal, rail handover, and repeated brownout.
- ESP32-C6 radio current steps, both light bars at maximum load, display activity, NFC transmit, and
  coincident worst-case loads.
- Short circuit, current-limit latch, open load, reversed battery, missing battery, stuck control
  signal, and disabled or unpowered peripheral behavior.
- Regulator stability, ripple, overshoot, undershoot, sequencing, absolute maximums, component power,
  junction-temperature estimate, and logic threshold margins.
- USB, SPI, I2C, shift-register, and LED waveform integrity at the real trace and cable loads.

Definition of done: every corner and fault remains inside its sourced criteria, or reaches the
specified safe state, with no provisional device model affecting the result.

### V4: Layout-derived electromagnetic validation

RF validation must use the routed production copper, stack-up, vias, ground regions, connectors, and
relevant enclosure materials. An analytical loop formula is useful as a cross-check but is not
release evidence by itself.

For the matrix and PN5180 path, simulate at least:

- Resistance, inductance, capacitance, Q, impedance, and mutual coupling for all 16 antennas.
- Each legal one-hot selection, power-up and reset states, and relevant illegal selection states.
- Loading from all deselected cells and all row-column crossings.
- The exact selected tag IC and tag antenna at center, edge, corner, rotation, lateral displacement,
  and minimum and maximum separation.
- Empty board, starting position, maximum credible tag population, adjacent tags, conductive objects,
  battery, display shields, fasteners, and enclosure materials.
- Matching-network tolerances, switch parasitics, received load modulation, selected-line margin, and
  adjacent-line crosstalk.

Definition of done:

- The exact tag MPN and geometry are bound and documented.
- Extracted network data are consumed automatically by the circuit tests.
- Every antenna and placement corner passes field, receive, tuning, voltage, current, and crosstalk
  criteria.
- Results are stable against a justified mesh refinement.

### V5: Firmware host verification

Keep gameplay and product state logic independent of ESP32 register access. Run it on the host with
hardware interfaces replaced by deterministic fakes.

Definition of done:

- Unit and state-machine tests cover every gameplay behavior and fault in `docs/functional/`.
- Generated sequences cover legal moves, illegal changes, captures, castling, promotion, duplicated
  UIDs, unstable reads, crosstalk, clock events, button gestures, sleep, low battery, and restart.
- Persistence tests inject reset and write failure at every transaction boundary.
- Host builds pass strict compiler warnings, static analysis, and available sanitizers.
- The firmware also builds reproducibly for the exact ESP32-C6 target and partition layout.

### V6: Firmware-in-simulation system verification

Run the real ESP32-C6 firmware image in Wokwi. Generate its virtual wiring from the authoritative
netlist. Implement behavioral models for the PN5180, TCA9535, displays, LEDs, matrix register chain,
button, charger signals, and rail faults where a trustworthy built-in model does not exist.

The PN5180 model must implement the used registers and commands, SPI framing, BUSY, IRQ, reset,
timeouts, inventory responses, and injected protocol failures. It is a digital protocol model, not
RF evidence.

Definition of done:

- Automated scenarios cover complete games and every functional fault and recovery path.
- Assertions check serial logs, GPIO and bus traces, display content, LED state, persistent state,
  browser-visible state, timing deadlines, and safe outputs during boot and reset.
- Fault injection covers missing, slow, malformed, duplicated, and contradictory peripheral data.
- No test-only firmware replaces the binary intended for the final board.

### V7: Mechanical and fabrication preflight

Validate the physical and manufacturing artifacts, not only the design source.

Definition of done:

- Generated STEP models fit the enclosure with checked connector access, cable bend space, diffuser
  clearance, component height, fasteners, antenna keepouts, and service access.
- Board outline, holes, stack-up, copper weight, impedance requirements, mask, paste, silkscreen,
  edge clearances, castellations if any, and assembly side match the order specification.
- BOM and CPL contain exactly the intended fitted designators. MPN, order code, package, side,
  centroid, and rotation are checked.
- Gerbers and drills regenerated from a clean workspace match the reviewed board and pass the
  manufacturer's DFM checks.
- A rendered review package shows every copper, mask, paste, silkscreen, drill, and 3D side.

Passing V0 through V7 permits only a documented test-article release.

### V8: Test-article measurement and model calibration

Some behavior cannot be certified from published models. Build or buy the smallest article that can
measure it. Prefer development kits, evaluation boards, breakout modules, copper antenna samples,
and partially populated boards over a complete assembled set.

Required measurements include, where applicable:

- Actual antenna complex impedance and Q with a calibrated VNA.
- Coupling and crosstalk with the selected tags across the full mechanical tolerance range.
- PN5180 tuning, transmit current, receive reliability, and scan timing.
- Rail startup, ripple, transient response, load handover, current limit, and temperatures.
- ESP32-C6 boot, programming recovery, USB, radio throughput, and antenna placement.
- Digital bus voltage and timing at the far end of each real cable.

Feed measured parasitics and limits back into the models. Re-run V0 through V7 and require the
simulation to reproduce the measurements within a stated error bound. A test article that disagrees
with the model invalidates the model, even if the hardware appears to work once.

### V9: Independent review and final release

An independent reviewer with electronics experience checks the release candidate without relying on
the conclusions of the agent that created it.

Definition of done:

- The reviewer signs off component pinouts, footprints, power, reset and programming, RF topology,
  protection, connectors, layout, fabrication outputs, and the remaining risk register.
- The complete clean-build test command passes, including all three boards, firmware host tests,
  Wokwi scenarios, ngspice corners, electromagnetic tests, ERC, DRC, and schematic parity.
- No critical Assumed evidence, open sourcing conflict, unexplained waiver, or manual-only test
  remains.
- `docs/planning.md` records the passing evidence, tool versions, test-article identity, release Git
  commit, and hashes of the exact Gerber ZIP, BOM, CPL, and firmware image.

Only after V9 passes may the intended assembled boards be ordered or described as final.

## Board-specific minimum evidence

The general milestones remain mandatory. These are additional minimum checks, not replacements.

### Light bar

- Exact LED pinout and mounting orientation proven from authoritative evidence.
- Layout-extracted supply and ground droop at tolerance and maximum load.
- First-pixel and far-end data waveform margins, power-up darkness, maximum thermal load, and chain
  failure behavior.
- Generated LED count agrees across functional documentation, schematic, layout, simulation, BOM,
  firmware, and criteria comments.

### Matrix

- Full layout-derived electromagnetic network including mutual coupling and actual surroundings.
- All 16 selected paths and deselected loading validated at component corners.
- Exact tags pass the complete placement and population matrix with sourced read and crosstalk
  margins.
- Power-up and firmware-reset states cannot unintentionally energize or mistune the array.

### Hub

- Complete charger, battery protection, 3.3 V, 5 V, and load-switch simulations.
- PN5180 transmit and receive networks use extracted matrix data and a justified driver model.
- ESP32-C6 module, USB, boot straps, recovery pads, decoupling, external antenna connector, and radio
  placement follow the current manufacturer guidance.
- Every connector is checked against its mating board and cable, including power direction and
  unpowered backfeed.

### Complete system

- The final firmware image passes host and Wokwi scenario suites.
- Simultaneous worst-case power and interface activity remains valid.
- A real PN5180 and ESP32-C6 development setup runs the intended driver and scan sequence before the
  final custom hub is ordered.

## Required release command

The repository must provide one non-interactive command, conventionally `make release-check`, that
rebuilds and runs every automated V0 through V7 and V9 check from a clean generated state. Slow tests
may be cached by content hash, but they may not be silently omitted. Missing implementations of this
command or any milestone are open work and block release.

The command must fail on warnings treated as release blockers, missing tools, missing models,
missing test artifacts, stale generated outputs, or differences between reviewed and generated
fabrication files. A green result is necessary but does not replace the V8 measurements or V9
independent review.
