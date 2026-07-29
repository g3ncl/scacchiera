# Power module interface

The battery, charger, protection, power path and 5 V conversion live in a purchased module outside
the custom boards. This file is the contract that module must satisfy, so it can be swapped for a
different one without changing the hub, its firmware, or the enclosure's electrical assumptions.

The hub owns the safety gate regardless of which module is fitted: qualified 5 V leaves the hub, and
a module that misbehaves cannot charge a cell outside the window proven in
[hub.md](hub.md).

## Signals

Two harnesses, both JST GH 1.25 mm, both seven-way. Every contact in this family is rated 1.0 A, so
the supply is spread across contacts rather than trusted to one.

**J2, hub to module input.** Qualified 5 V, gated by cell temperature.

| Pin | Signal | Direction | Note |
| --- | --- | --- | --- |
| 1 to 3 | CHARGE_5V | hub to module | three contacts, 3.0 A capability |
| 4 to 7 | GND | shared | four contacts |

While an adapter is connected this harness carries charge current and system load together, which is
why it has more supply contacts than J3.

**J3, module to hub.** The module's regulated output and its optional telemetry.

| Pin | Signal | Direction | Required |
| --- | --- | --- | --- |
| 1, 2 | MODULE_5V | module to hub | yes, two contacts, 2.0 A capability |
| 3, 4 | GND | shared | yes |
| 5 | I2C_SCL | hub to module | no |
| 6 | I2C_SDA | bidirectional | no |
| 7 | BAT_RAW | module to hub | yes, the cell terminal |

## Mandatory properties

A candidate module must provide all of these:

- **5 V output at 1.3 A continuous, never sagging below 4.0 V.** The board's worst case is both
  light bars white (448 mA) plus the 3.3 V rail under an ESP32-C6 transmit peak, reader, displays and
  matrix. The floor comes from the hub side: its buck holds 3.3 V until its input falls to 3.51 V at
  that load, and 4.0 V keeps half a volt in hand for the cable and connector drops that figure
  excludes. A module that sags further browns out the MCU, and the hub cannot ride it out; its
  output capacitance is worth about five microseconds.
- **Charging from a 5 V input at 1 A or more**, which meets `POWER-CHARGE-10-80` at 240 minutes.
- **Uninterrupted output across source insertion and removal.** The board must not reset when the
  adapter is connected or pulled. This is the property the module exists for, and V8 measures it.
- **Output that stays up at a few milliamps indefinitely.** The board sleeps after twenty idle
  minutes under `GAME-IDLE-SLEEP` and draws far less than the 45 to 50 mA at which power-bank
  controllers switch themselves off. If a module needs a register write to disable that shutdown,
  the setting must survive a brownout and a power cycle, and V8 must show it.
- **Cell terminal available** on a pad or pin, for the hub's own battery reading.
- **Cell protection**: overcharge, over-discharge, overcurrent and short circuit, on the module or
  on the cell's own protection board.
- **Fits the service volume**: no dimension across the rail above 46 mm, including the cell.

## Deliberately not required

- **I2C telemetry.** The hub reads cell voltage itself through the divider on `BAT_RAW`, so battery
  level and estimated play time do not depend on a module's register map. Where a module does expose
  I2C, the hub can use it for source presence and charge control, but nothing required by
  `docs/functional/` rests on it. This is what lets a module with an undocumented or absent I2C
  interface be fitted.
- **A cell thermistor.** The hub carries its own cell-bonded sensor and analog window, so a module
  without an NTC input is acceptable and a module with one is redundant rather than trusted.
- **USB Power Delivery.** The inlet is power-only and presents passive sink resistors.
- **A specific cell format.** Any cell meeting the runtime requirement and the 46 mm width fits;
  see [the format survey](../../Vault/Scacchiera/Wiki/synthesis/battery-format-and-module-alternatives.md)
  for why a 1S pouch is the current choice.

## Fitted module

None bound yet. Binding one is a V1 action: file its manufacturer documentation in the vault, record
the exact product and revision, and check it against every mandatory property above. The previously
selected PiSugar 3 Plus satisfies the electrical contract but fails the 46 mm width, which is why
the interface is written as a contract rather than around one product.

## Verification

- V2 checks both connector pin maps against this table from the schematic.
- V3 proves the temperature gate holds for any module, since the gate is on the hub, and derives the
  4.0 V output floor above from the hub's own dropout.
- V8 measures, on the fitted module: charge time against `POWER-CHARGE-10-80` and
  `POWER-CHARGE-10-FULL`, output continuity across source insertion and removal, output held during
  sleep, and cell-surface temperature under charge.
