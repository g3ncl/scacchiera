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
- **No target build.** `port/` and `main/` are empty directories. The reproducible ESP32-C6 image
  is the remaining V5 bullet and needs ESP-IDF, which is not installed.
