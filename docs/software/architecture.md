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

## Status

Not started. V5 and V6 are open in [planning.md](../planning.md), and this file is the plan they
follow rather than a description of code that exists.
