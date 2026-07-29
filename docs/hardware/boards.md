# Board inventory

Which physical boards the product needs and what each one is responsible for. This is the
Milestone 1 deliverable of [the hardware plan](../planning.md), derived from
[the functional specification](../functional/overview.md). Each board gets its own
`docs/hardware/<board>.md` spec as it clears Milestone 2; this page stays the map of what exists
and why the split is this way.

## Sensing architecture (implementation choice)

The functional spec fixes what must be read (occupant, color, and type on 64 squares through a
3.0 mm stack) but not how. The rebuild uses the row-column antenna matrix from the research wiki
(`Vault/Scacchiera/Wiki/`): 8 row antennas plus 8 column antennas under the play area, one shared
NFC reader, and a tag's square found by intersecting which row and which column saw its UID.
16 antennas instead of 64 is the main bill-of-materials lever, and the NFC Game Board project
provides measured prior art that long, imperfectly tuned line antennas are good enough because a
line only has to reject tags outside its own footprint. Line switching uses series PIN diodes;
both the prior art and our own earlier SPICE work show analog-switch off-capacitance detunes a
shared 13.56 MHz bus, while reverse-biased PIN diodes stay under a picofarad.

## The boards

Four custom board designs, five physical PCBs. The two OLED displays are purchased
ER-OLEDM3.12-1W modules (fixed by [interface.md](../functional/interface.md)), so they appear
here only as interfaces, not as boards.

### 1. Matrix board (sensing)

- **Responsibility:** carry the 8+8 line antennas under the whole 280 x 280 mm play area and the
  per-line PIN diode switches, so exactly one line at a time couples to the shared RF bus. No
  intelligence: it is copper geometry plus switching, with every component on the underside so the
  top face stays flat against the controlled air gap in
  [physical.md](../functional/physical.md).
- **Interfaces:**
  - one shared 13.56 MHz RF feed from the hub (short controlled-impedance link, board-to-board
    connector);
  - line-select control from the hub (serial shift register driving 16 bias steers, so the
    inter-board cable stays small);
  - PIN reverse-bias rail and ground from the hub.
- **Envelope:** about 300 x 300 mm, 2-layer. Mounts independently of the top surface per the
  functional spec, metal-free zone maintained under the play area.
- **Cost target:** 25 EUR (area-dominated fab around 15 EUR, plus 16 PIN diodes, shift
  registers, and passives).

### 2. Hub board (controller and power distribution)

- **Responsibility:** everything that thinks or powers. WiFi MCU running the game logic
  ([gameplay.md](../functional/gameplay.md) entirely, including clock, PGN storage, browser
  client), the NFC reader IC with its matched front end driving the matrix RF bus, one regulated
  5 V input, 3.3 V regulation, the PIN-diode reverse-bias supply, the independent cell-temperature
  interlock, the single button, and the connectors fanning out to every other surface.
- **Interfaces:** matrix board (RF feed, line select, bias); two display modules (shared bus,
  I2C or SPI, decided at schematic time); two light bars (few-wire serial); button; power module
  qualified 5 V out and managed 5 V back; service-only debug.
- **Envelope:** 162 x 46 mm, 2-layer, in the service volume under one 50 mm player rail, conductive
  parts kept out of the play area per the read-budget rule. Long rather than layered: the rail is
  310 mm and holds only this board, so length is cheaper than copper layers.
- **Cost target:** 25 EUR (MCU module, reader IC, buck regulator, safety interlock, connectors).

### 3. Light bar board (x2, one design)

- **Responsibility:** the diffused feedback bar fixed by
  [interface.md](../functional/interface.md): 120 x 8.5 mm, 14 low-current LEDs, all components
  on the front side behind a replaceable diffuser. Both rails use the identical design. The count
  dropped from 17 because a hand-solderable LED package is wider; see
  [lightbar.md](lightbar.md).
- **Interfaces:** 4-wire JST GH from the hub: 5 V, ground, WS2812 data in, chain out (see
  [lightbar.md](lightbar.md)).
- **Cost target:** 5 EUR per bar including fab.

### 4. Power board

- **Responsibility:** connect a protected 1S cell, isolate reversed polarity, charge it from the
  qualified 5 V input, manage source handover, and deliver a regulated 5 V at 2 A to the hub using
  BQ25895 and TPS61088.
- **Interfaces:** qualified charge input, regulated 5 V return and raw cell sense through the same
  [power module contract](power-module-interface.md) a purchased replacement would implement.
- **Envelope:** 90 x 32 mm, 2-layer. It is a snap-off part of the panel carrying both light bars.
- **Cost target:** fabrication rides on the light-bar panel; component cost remains to be quoted.

### Purchased accessories (not boards)

Bought parts that appear on no board BOM but without which the product does not work. Recorded here
for the same reason the display modules are: an order that forgets them is incomplete.

- **Two ER-OLEDM3.12-1W display modules**, fixed by [interface.md](../functional/interface.md).
- **One 2.4 GHz antenna with pigtail** for the hub's ESP32-C6-MINI-1U. The module has an external
  antenna connector rather than a PCB antenna, which makes the antenna replaceable for about a euro
  instead of a hub respin. The connector is **MHF3 / W.FL / IPEX3**, not U.FL: a U.FL pigtail is
  larger and will not mate. Prefer an adhesive FPC antenna, pre-tuned to 50 ohm, stuck to the inside
  of a plastic rail wall and kept roughly 15 mm clear of the battery, shields and copper. A custom
  antenna PCB was considered and rejected: its radiation pattern is the one thing in this project
  that no ngspice test can validate, and per-attempt iteration costs a fabrication run rather than
  a euro.
- **One protected 1S cell assembly** for the custom [power board](power.md). A cylindrical cell may
  lie lengthwise in the player rail. The filed 21.7 x 70.2 mm Molicel 21700 candidate demonstrates
  that the geometry and discharge current are feasible, but the protected assembly is not bound.
- **Micro-Fit mating hardware:** two Molex 430250800 eight-circuit receptacle housings for the
  hub-to-power harness, one 430250200 two-circuit housing for the battery, and 430300038 female
  terminals for 18 AWG wire. Exact wire, pre-crimped leads or qualified crimp process, color coding,
  and strain relief remain open.
- **Superseded option, one purchased power module**, meeting [power-module-interface.md](power-module-interface.md).
  It provides charging, protection, the UPS power path and the regulated 5 V output. No product is
  bound yet; the contract caps it at 46 mm across the rail, cell included, so that it fits the
  player-rail service volume rather than needing a separate cassette. Selection status is in
  [power-subsystem.md](power-subsystem.md).

## Why this split

- The matrix board is large but cheap and dumb; the hub is small but dense. Separating them means
  a controller respin never pays for 900 square centimeters of fab, and the big board has no
  fine-pitch assembly.
- The functional spec already forces the split physically: the hub and shields sit under the
  rails, the commercial battery subsystem sits in a rear service cassette, and the sensing plane
  stays free of conductive parts within its required clearance.
- The light bars are separate because they live in a different mechanical position (behind the
  rail diffusers) and are trivially small; folding them into the hub would tie the hub's outline
  to the diffuser geometry.
- Rough total per unit in custom parts and fab remains to be regenerated, with the power module,
  its cell and the two display modules counted as purchased accessories.

## Build order

Light bar first (smallest board, stands up the schematic-ERC-BOM-simulation-layout pipeline end to
end), then the matrix board (the architectural risk, and its SPICE validation needs layout-derived
antenna values, so its layout comes before its simulation per the plan), then the hub (its RF
front end must match the measured matrix, so it goes last).
