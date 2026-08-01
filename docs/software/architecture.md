# Firmware architecture

How the firmware is split so that the behaviour in [functional/gameplay.md](../functional/gameplay.md)
can be tested on a development machine rather than only on a board. This file covers the split, the
build targets, and the rule that keeps them apart. Driver detail belongs in its own file per
peripheral, not here.

## The split

V5 in [simulation-workflow.md](../simulation-workflow.md) requires gameplay and product state logic
to be independent of ESP32 register access. That is not a testing convenience, it follows from the
first principle in [functional/overview.md](../functional/overview.md): the typed physical position
is authoritative and a sensing fault is never converted into a move. Deciding what the position
means has to be separable from deciding what the hardware just reported, or the two get to influence
each other.

So there are two layers and one boundary.

`core/` holds the position, the rules, move derivation from typed snapshots, the clock, the game
state machine, the fault table, provisioning, and PGN. It includes no ESP-IDF header, touches no
register, and blocks on nothing. It is C that runs anywhere.

`port/` holds the PN5180, the TCA9535, the displays, the light bars, the matrix scan, the button,
persistence, and the network. It is where ESP-IDF appears.

The boundary is a small set of headers in `core/` that `port/` implements: a scan returns a typed
snapshot, a clock returns monotonic milliseconds, an output surface accepts display text and light
cues, and storage accepts and returns a game snapshot. On the host the same headers are implemented
by deterministic fakes, which is what makes generated move sequences and injected faults possible.

Nothing in `core/` calls into `port/`. The application in `main/` owns the wiring and is the only
place that knows both exist.

## Why C

The target build has to be the exact ESP32-C6 image V6 runs in Wokwi and V9 releases, and ESP-IDF is
a C toolchain. Using anything else in `core/` would mean either a second toolchain in the image or a
host-only reimplementation of the rules, and a rules engine that is not the shipped one is not
evidence. Strict warnings, static analysis, and the address and undefined-behaviour sanitizers all
run on the host build, where they are cheap.

## Build targets

Two, from the same sources:

- **Host tests.** Plain CMake and CTest over `core/` plus the fakes, with Unity and CMock. This is
  the V5 gate. It builds with warnings as errors and runs under the sanitizers.
- **Target image.** The ESP-IDF build over `core/`, `port/` and `main/` for the ESP32-C6 and its
  partition layout. This is the binary V6 executes and V9 releases.

A file that will not compile in both is in the wrong layer.

## Layout

```
software/firmware/
  core/          rules, state, clock, faults, PGN; no ESP-IDF
  core/hw/       the headers port and the fakes both implement
  port/          ESP-IDF drivers
  main/          application wiring and entry point
  test/          host tests and deterministic fakes
```

The browser client is a separate concern and gets its own directory and its own document when it
starts. It mirrors state and configures the board; nothing required by `docs/functional/` depends on
it being connected.

## Scope for hardware validation

V5 and V6 exist here to de-risk hardware before it is fabricated, not to finish the product. So the
work is ordered by what a board can teach us and nothing else.

**In scope now**, because it is what exercises the hardware: the PN5180 driver down to SPI framing,
BUSY, IRQ, reset and inventory; the TCA9535 and everything hanging off it; the display SPI at the
timing the SSD1362 table fixes; the matrix register chain and its scan; the light-bar data stream;
the button; the charger and rail signals; power-up, warm reset and the recovery path. These are the
parts whose failure means a board respin, so they are the parts V6 has to run in simulation against
behavioural peripheral models.

**Stubbed as TBD**: the chess rules engine. `core/` gets the position type, the typed-snapshot
interface and a stub that accepts a snapshot and returns "not implemented", enough for the layers
above and below it to be exercised and for V6 scenarios to drive real scans through real drivers. No
rule in [functional/gameplay.md](../functional/gameplay.md) can invalidate a PCB, so implementing
castling before the reader driver works would be effort spent in the wrong order.

The stub is a stub, not a shortcut: V5's definition of done in
[simulation-workflow.md](../simulation-workflow.md) still requires generated sequences over every
gameplay behaviour, and that bullet stays open until the engine is real. What this ordering buys is
that the hardware-facing bullets can close first.

## Status

**Foundation exists as of 2026-08-01.** `software/firmware/` holds the host build, the boundary
headers, the core types and the deterministic fakes, and `make firmware-test` is part of
`make check`.

What is there:

- CMake and CTest over `core/` plus the fakes, building with `-Werror`, `-Wconversion`,
  `-Wsign-conversion`, `-Wshadow` and the rest, and with gcc's `-fanalyzer` as the static analysis
  step. `clang-tidy` and `cppcheck` are not installed on this machine.
- `core/`: `square` (zero based, aligned with the sensor array), `piece`, `fault` (the five faults
  from [functional/gameplay.md](../functional/gameplay.md) with a test that fails if the table
  drifts), `snapshot` (typed 64-square reading with UID, plus equality, occupancy and duplicate-UID
  detection), and the `engine` stub.
- `core/hw/`: `clock`, `scan`, `output`, `storage`, the four headers `port/` and the fakes both
  implement as free functions. No indirection layer, because link-time substitution already does
  the job.
- `test/`: deterministic fakes for all four, and five test executables covering square indexing,
  snapshot semantics, the fault table, the stub's contract, and the fakes themselves.

The engine stub is pinned by tests deliberately. It records a clean snapshot, refuses a faulted
one, and never returns ACCEPTED, so a caller cannot mistake "not implemented" for "legal". Those
tests are expected to be rewritten when the engine is real.

Two gaps, both recorded rather than assumed away:

- **Sanitizers do not run.** gcc accepts `-fsanitize=address,undefined` whether or not the runtime
  libraries exist and only fails at link, so the build probes a real link and falls back with a
  warning. Installing `libasan` and `libubsan` closes it.
**The target image builds**, as of 2026-08-01. `make firmware-target` produces a 119 KB
`chessboard.bin` for the ESP32-C6, leaving 92 percent of its app partition free.

- **Pinned to ESP-IDF v5.5.5**, commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`, with the
  riscv32 toolchain at esp-14.2.0. v5.5 rather than v6.0 because V6 has to run this exact image in
  Wokwi and the v5.5 line has the most mileage there.
- The IDF project root is `target/`, kept separate because the host gate owns
  `software/firmware/CMakeLists.txt` and two build systems cannot share one project root.
  `core/CMakeLists.txt` registers itself either as an IDF component or as a plain static library
  depending on `ESP_PLATFORM`, so both builds compile the same sources rather than a copy.
- `target/partitions.csv` fixes the layout: two 1.5 MB OTA app slots so a failed update cannot
  leave a board that will not boot, NVS for the in-progress snapshot because it is rewritten after
  every committed move and NVS wear-levels, and a 896 KB SPIFFS partition for PGN.
- `port/board_pins.h` is generated from the hub netlist by `hardware/pcb/firmware_pins.py`, and
  `hardware/tests/test_firmware_pins.py` fails if the committed copy drifts. A stale pin map is not
  a compile error, it is a board that boots and does the wrong thing.

`firmware-target` is deliberately not part of `make check`, because it needs a 2 GB toolchain
exported rather than a checkout dependency.

## Drivers

`port/` holds six drivers and the boundary implementation, all compiling for the C6. Boot order is
not arbitrary; each step depends on the previous one.

| Step | What it establishes |
| --- | --- |
| `expander_init` | resets asserted, light-bar rail off, matrix latch idle low |
| `spi_bus_init` | the one bus shared by reader, both displays and the matrix registers |
| `matrix_init` | shifts and latches all-deselected, the only path to a known selection |
| `pn5180_init` | reset, then an EEPROM version read that proves the framing |
| `display_init` | shared reset, 50 ms settle, init sequence, clear, on |
| `lightbar_init` | blank the pixels, then enable the rail |
| `board_hw_storage_init` | NVS for the in-progress snapshot |

Three properties of the wiring shape all of this, and each was read from the netlist rather than
assumed:

- **The matrix registers have no chip select**, so every byte sent to the reader or a display is
  also shifted into them. Their outputs only move on a latch edge, so the shift and the latch must
  be atomic against all other SPI traffic. Every driver that transacts acquires the bus.
- **The expander's outputs power up high**, so values are written before directions. Otherwise the
  reader and displays leave reset uncontrolled, the light-bar rail switches on, and the matrix
  latches random selection.
- **The matrix cannot be blanked**, so shifting a known pattern is mandatory rather than tidy.

## What is real and what is not

Real: the expander, the matrix selection, the PN5180 framing down to BUSY and single-slot ISO 15693
inventory, the SSD1362 command path, the light-bar stream, the clock, light cues, NVS persistence,
and a full sixteen-line sweep joined into a snapshot.

Not real, and deliberately so:

- **The rules engine** is still the stub, per the ordering above.
- **Display text** is logged rather than rendered. The driver can address any window and push
  pixels, but there is no glyph source, and generating a font the way `board_pins.h` is generated
  beats hand-typing a table.
- **Piece identity.** The scan resolves a square and a UID; mapping a UID to a colour and type is
  provisioning's job and provisioning does not exist, so a scanned square carries `PIECE_TYPE_NONE`
  rather than a guess. A host test pins that, so nobody later "fixes" it by defaulting to a pawn.
- **Sixteen-slot anticollision** and the BitwiseID scheme above it. This is a larger gap than it
  first sounds and is the next firmware work, not a refinement.

  Single-slot inventory means every tag in the field answers in the same window, so it can only
  read a line carrying exactly one tag. A chess starting position puts eight pieces on rank 1, so
  row 0 sees eight tags collide and reports nothing but a fault. The row-and-column architecture
  guarantees this: sixteen antennas covering sixty-four squares means a line is shared by eight
  squares, and [the BitwiseID research](../../Vault/Scacchiera/Wiki/concepts/bitwiseid-method.md)
  exists precisely because a line scan returns several tags at once.

  So what is implemented proves the RF path end to end and reads a sparse board, but it cannot
  read a real game. The mechanism for the fix is confirmed in the datasheet rather than guessed:
  sixteen-slot inventory uses flags 0x06 instead of 0x26, and a slot is advanced by emitting an
  EOF, which TX_CONFIG bit 10 provides. That bit is TX_DATA_ENABLE, and clearing it makes a
  transmission send "only symbols" (Table 98), which is the EOF pulse ISO 15693 anticollision
  needs.

The join from sixteen line reads to sixty-four squares lives in `core/scan_join.c`, not in a
driver, because that is where the ghost-piece and crosstalk faults live and it is testable without
hardware. Nine tests cover it, including that a tag heard on two lines never becomes a piece and
that a tag heard on one axis is not placed at a guessed square.
