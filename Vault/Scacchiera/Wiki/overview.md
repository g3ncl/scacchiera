---
type: overview
date_updated: 2026-07-29
tags:
  - wiki/overview
---

# Overview

High level synthesis of everything the wiki knows. This page is regenerated as
the big picture changes during ingestion. Start here for the shape of the
knowledge base, then follow [[wikilinks]] into [[index|the index]] and the
individual pages.

## Verification state

The legacy schematic, nominal simulation, and generated-layout milestones are inputs rather than
release authority. [[verification-evidence-model]] records the executable V0 structure. The new
functional power specification adds bounded runtime, charge time, source fallback, and battery
safety requirements after the original 500 mA architecture proved unsuitable.

The power boundary remains a written contract, but the default implementation is now a custom
90 x 32 mm board panelized with the light bars. [[bq25895rtwr]] owns charging and power-path
management, while [[tps61088rhlr]] produces the regulated 5 V return. The hub still measures cell
voltage and gates charging from its independent temperature window, so the implementation can be
replaced without moving safety or telemetry across the boundary. See
[[battery-format-and-module-alternatives]].

The inlet remains a 5 V-only passive sink. [[usb-type-c-5v-current-advertisement]] adds two filtered
CC ADC readings, so ordinary Type-C and laptop PD chargers can be distinguished as default, 1.5 A,
or 3.0 A sources without a PD contract. Invalid or changing readings retain the lower input limit.

[[v1-component-proof|V1]] audits the exact fitted tuples with no fitted-part sourcing blocker. The
power inductor is now exact [[dfe252012f-1r0m-p2]]. V1 remains open on the
[[er-oledm3-12-1w]] documentation conflict and its cable definition; a purchased power module is
only an optional replacement, not a fitted dependency. [[v2-static-connectivity|V2]] passes on all four board designs, and all
four are two copper layers. The
hub reached that by growing to 162 x 46 mm rather than by adding layers, since the rail it lives in
has length to spare and a four-layer panel costs a multiple of a two-layer one.

V3 power and fault simulation is the open gate. Three hub results and two power-board benches exist.
[[v3-charge-interlock]]: the cell-temperature cutoff holds inside the qualified 0 to 40 degree range
across 384 published tolerance corners and both sensor failure directions.
[[v3-led-rail-current-limit]]: the light-bar limiter carries both bars at full white and clamps a
short inside its harness rating, on TI's own transient model, replacing a value that had only a
formula behind it. [[v3-buck-power-stage]]: the 3.3 V rail's ripple and inductor stress over 72
corners, from a model that deliberately holds no control behaviour, so regulation and stability stay
data sheet claims for V8. The power-board boost has a 162-corner ngspice stage sweep plus a separate
80 percent efficiency current bound. Its averaged NVDC model covers adapter priority, battery
supplement, removal, missing and depleted cells, a shorted cell, and a stuck charge command.
Its [[0402b223k500nt]] compensation capacitor is selected by a 4,374-corner small-signal
sensitivity analysis, which reaches 54.64 degrees minimum phase margin and rejects the former 4.7
nF value. TI gives no guaranteed error-amplifier transconductance range, so this narrows the design
without closing V3 loop evidence.
[[csd25404q3]] and [[tlv7021dckr]] now isolate a reversed cell before the charger BAT node. The
ngspice bench covers cold and already-powered insertion at both polarities, while physical fault
insertion remains mandatory at V8. The AP22811 input switch and many transient cases remain
unsimulated.

The display evidence raises coincident load from 1.14 A to 1.48 A. The current 2 A interface and
[[tps61088rhlr]] stage cover the full 10 W stress case. Replacing BQ25619 with [[bq25895rtwr]] raises
the guaranteed battery path from 5 A to 6 A continuous and 9 A for one second, clearing the
efficiency-bounded 4.442 A RMS and 5.871 A peak boost currents. Its third 22 uF output capacitor
keeps ripple to 138 mV after initial tolerance, X5R temperature shift, the 50 percent DC-bias
sensitivity bound, TI's recommended minus 30 percent inductor corner, and a 15 milliohm
assembled-bank ESR limit. The fitted bank still needs an ESR measurement.

The earlier [[chessboard-quick-charge-architecture|custom PD architecture]] and
[[quick-charge-module-evaluation|RBS18634 article]] remain historical evidence rather than active
designs. The current open risks are the protected cell assembly, physical reversed-cell response, switching
loop evidence, enclosure ventilation, measured recharge time, and representative runtime. The selected
[[fail-safe-cell-temperature-window]] uses a wired thermistor and analog comparators so firmware
cannot override the qualified charge range. Hub L1 is the fully documented [[nr6045s4r7mt]];
the earlier [[swpa5045s4r7mt]] catalog binding is rejected because its claimed MPN is absent from
the manufacturer series table.

## NFC Game Board: the reference project

The wiki's first ingest covers [[nfc-game-board-project|NFC Game Board]], [[ben-bulsink|Ben
Bulsink]]'s open Scrabble-board project (nfcgameboard.com), captured because it built and measured
the same core idea the chessboard's sensing design is built on: **one RFID reader, a row+column
antenna matrix instead of one antenna per position** (see
[[row-column-antenna-matrix-technique]]), an 8+8 matrix (16 antennas) on our 8x8 board. The
chessboard's own hardware implementation is being rebuilt from scratch on top of the functional
spec in [[../../../docs/functional/overview.md|docs/functional/]], tracked milestone by milestone in
[[../../../docs/planning.md|docs/planning.md]]; this project supplies real, measured prior art for
two of the row-column technique's three coupled risks:

- **Antenna geometry and tuning** (low risk): the source project tolerates "bad tuning and long
  feeding lines" because antennas only need to reject tags outside their own footprint, not tune
  precisely.
- **Multi-tag anticollision per scan** (the real work): solved on the source project's side by
  [[bitwiseid-method|BitwiseID]], a one-hot bit-coding technique that reads an entire row or
  column of tags in one operation by relying on the reader's logical-OR collision behavior,
  holding 0.35 s response time flat up to 225 tiles. [[bitwisexy-method|BitwiseXY]] extends it for
  larger tag counts by coding coordinates instead of identity, and
  [[set-management-and-setid|set management]] keeps one system's tags from colliding with a
  foreign set's. None of this is yet proven on our own tag protocol (ISO/IEC 14443-A, versus the
  source project's ISO/IEC 15693); that gap is explicit in [[bitwiseid-method]].
- **Overlap tuning between adjacent lines**: not directly addressed by this source; still an open
  item for our own design.

The source project also independently converged on
[[pin-diode-antenna-switching|PIN diode antenna switching]] to keep parallel switch capacitance
off a shared HF bus, the same fix an earlier iteration of our own SPICE simulation reached for the
same reason (see [[pin-diode-antenna-switching]] for that result; the switch device is an open
decision again in the from-scratch rebuild).

See [[nfc-game-board-project]] for the full architecture and [[bitwiseid-whitepaper]] for the
detection method in detail.

## Assembly sourcing

[[jlcpcb]] is the intended assembly service. The captured
[[jlcpcb-economic-parts-2026-07-24|economic-parts catalog]] supplies a dated Basic-part inventory
for the production pass. Only substitutions that preserve value, package, dielectric, and electrical
limits are assigned to the JLC BOM; RF, power, IC, and mechanical items without a verified match
are kept explicit in [[jlcpcb-basic-part-sourcing]] and
[[../../../docs/hardware/jlcpcb-sourcing.md|the project sourcing register]].

The matrix production BOM is now fully bound. [[jlcpcb-matrix-bom-review]] records how exact MPN
comments, live inventory checks, assembly-only reference filtering, and conservative RF simulation
turned JLCPCB's ambiguous first match into an 11-line BOM whose 165 references exactly match its
CPL.

The follow-up [[jlcpcb-matrix-live-stock-2026-07-25|live inventory capture]] confirms that every
matrix line is available from JLCPCB's public Basic or Extended library above the five-board order
requirement. Pre-Order and Global Sourcing remain fallback paths, not current requirements.

[[schemalyzer-jlcpcb-design-rules-2025|Schemalyzer's captured JLCPCB DFM guide]] adds a general
fabrication and release checklist. It is deliberately treated as secondary guidance: the project
checks the chosen stack-up and PCBA limits in JLCPCB's live order flow before payment.
