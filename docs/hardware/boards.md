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

Three custom board designs, four physical PCBs. The two OLED displays are purchased
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

### 2. Hub board (controller and power)

- **Responsibility:** everything that thinks or powers. WiFi MCU running the game logic
  ([gameplay.md](../functional/gameplay.md) entirely, including clock, PGN storage, browser
  client), the NFC reader IC with its matched front end driving the matrix RF bus, USB-C charging
  of a 1-cell Li-ion battery with voltage monitoring for the low-battery shutdown behavior, 3.3 V
  regulation, the PIN-diode reverse-bias supply, the single button, and the connectors fanning out
  to every other surface.
- **Interfaces:** matrix board (RF feed, line select, bias); two display modules (shared bus,
  I2C or SPI, decided at schematic time); two light bars (few-wire serial); button; USB-C;
  battery.
- **Envelope:** fits the service volume under one 50 mm player rail, conductive parts kept out of
  the play area per the read-budget rule.
- **Cost target:** 30 EUR (MCU module, reader IC, charger, regulators, connectors).

### 3. Light bar board (x2, one design)

- **Responsibility:** the diffused feedback bar fixed by
  [interface.md](../functional/interface.md): 120 x 8.5 mm, 17 low-current LEDs, all components
  on the front side behind a replaceable diffuser. Both rails use the identical design.
- **Interfaces:** 4-wire JST GH from the hub: 5 V, ground, WS2812 data in, chain out (see
  [lightbar.md](lightbar.md)).
- **Cost target:** 5 EUR per bar including fab.

## Why this split

- The matrix board is large but cheap and dumb; the hub is small but dense. Separating them means
  a controller respin never pays for 900 square centimeters of fab, and the big board has no
  fine-pitch assembly.
- The functional spec already forces the split physically: the battery, shields, and hub must sit
  under the rails, while the sensing plane must sit under the play area with nothing conductive
  within 10 mm behind it.
- The light bars are separate because they live in a different mechanical position (behind the
  rail diffusers) and are trivially small; folding them into the hub would tie the hub's outline
  to the diffuser geometry.
- Rough total per unit in customs parts and fab: about 65 EUR plus the two purchased display
  modules.

## Build order

Light bar first (smallest board, stands up the schematic-ERC-BOM-simulation-layout pipeline end to
end), then the matrix board (the architectural risk, and its SPICE validation needs layout-derived
antenna values, so its layout comes before its simulation per the plan), then the hub (its RF
front end must match the measured matrix, so it goes last).
