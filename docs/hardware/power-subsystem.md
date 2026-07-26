# Commercial power subsystem

The battery, charger, protection, power-path, and 5 V conversion are one purchased and replaceable
subassembly. This boundary avoids reproducing a lithium charger on the hub while retaining the
verification evidence required by [the simulation workflow](../simulation-workflow.md).

## Selected module

The selected subsystem is one PiSugar 3 Plus with its supplied 5000 mAh, 3.7 V pouch cell. The
manufacturer specifies a 5 V input and output, both rated up to 3 A, full UPS behavior during source
insertion and removal, and an I2C interface at address `0x57`. The hub uses the extension header's
5 V, ground, SDA, and SCL signals. A two-wire harness from the hub's protected 5 V charge output
terminates at the documented PiSugar 5 V input pad. The PiSugar USB connectors stay internal and
unused.

The subsystem is outside the custom hub BOM and is not reproduced from an unpublished schematic.
Its immutable evidence is the [product documentation](../../Vault/Scacchiera/Datasheets/PISUGAR3_PLUS_product.md),
[I2C documentation](../../Vault/Scacchiera/Datasheets/PISUGAR3_PLUS_i2c.md),
[safety instructions](../../Vault/Scacchiera/Datasheets/PISUGAR3_PLUS_safety.md),
[cell UN 38.3 report](../../Vault/Scacchiera/Datasheets/955465_PISUGAR5000_UN38.3.pdf), and
[manufacturer STEP assembly](../../Vault/Scacchiera/Datasheets/PISUGAR3_PLUS.step).

## Electrical boundary

PiSugar supplies the hub with regulated 5 V. The light-bar branch uses that rail through its
existing latch-off current limiter. An AP63203WU-7 buck generates 3.3 V for the MCU, reader,
displays, and matrix. PiSugar I2C supplies external-power presence, charge enable, output enable,
delayed output shutdown, battery voltage, and estimated percentage. Its temperature register is
the charger IC temperature, not cell temperature.

The product's power-only USB-C inlet feeds an AP22811AW5-7 switch whose enable comes from a
TLV7042DGKR analog window around a cell-bonded NTCLE317E4103SBA thermistor. Nominal trip points near
8 and 34 degrees Celsius deliberately stay inside the published 0 to 40 degree boundary. Open or
short thermistor wiring disables the switch. Firmware reads a divided copy for status, but cannot
override the hardware cutoff. Debug uses the locking UART service connector.

## Mechanical boundary

The manufacturer's PCB is 65 x 56 mm and the filed STEP assembly measures about 65 x 57 x 9.22 mm.
The included 955465 cell is 65 x 54 x 9.5 mm. This is wider than a 50 mm player rail, so it cannot
be hidden there without changing the fixed product geometry. V7 must define a ventilated,
serviceable rear cassette outside the NFC sensing area, with strain relief, impact protection, no
cell compression, and access to the charging connector.

The manufacturer's safety instructions prohibit heat buildup in an enclosed 3D-printed case.
Ventilation is therefore a safety requirement, not an optional cosmetic feature.

## V8 measurements

The exact received module and firmware revision must be recorded before testing. V8 measures:

- 10-to-80 and 10-to-full charge time from a compliant 5 V, 2 A source at 20 to 25 degrees Celsius;
- runtime under the representative gameplay profile;
- 5 V continuity and minimum voltage during source insertion and removal;
- input current, output voltage, charger IC temperature, and cell-surface temperature while idle
  and under a representative active load;
- independent charge inhibition below 0 degrees Celsius and at or above 40 degrees Celsius;
- I2C status accuracy, charge disable, delayed shutdown, and recovery from loss of communication;
- enclosure ventilation, connector strain relief, and NFC performance with the module installed.

UN 38.3 is transport evidence for the supplied cell. It is not completed-product certification
and does not waive any V8 or V9 check.
