---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-08-18
source_file: "Datasheets/PN5180A0HN-C3E_C1526287.pdf"
source_title: "PN5180A0HN/C3E manufacturer datasheet"
publisher: "NXP Semiconductors"
---

# PN5180A0HN/C3E datasheet

This source binds [PN5180A0HN/C3E](../entities/pn5180a0hn-c3e.md) to supplier order
code `C1526287`. It is used by hub U3 (PN5180A0HN/C3E).

[mpn::PN5180A0HN/C3E] [order_code::C1526287]
[manufacturer::NXP Semiconductors] [footprint::Package_DFN_QFN:QFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm]

## Design facts reviewed

- Library proof: manufacturer pin and package drawing checked against the SKiDL pin numbers, KiCad pad numbers, polarity, top assembly side and KiCad zero-degree orientation.
- Ratings used by the design: pinout, no-connect and exposed-pad treatment, recommended operating range, absolute maximum voltage, current, power and temperature, startup state, thermal data and package.
- Exact selected limits: See the filed data sheet and structured audit..
- Datasheet locator: pin description, absolute maximum, recommended operation, electrical, thermal and package tables.
- Simulation treatment: datasheet_bounded, valid only for
  no distributable vendor ngspice model was identified; V3 may use only parameters enumerated in this part's filed datasheet and must sweep their full published limits; digital protocol behavior belongs to V6.
- Conflicts: none open. Any later catalog or document mismatch reopens V1.

## Host interface facts (section 11.4, rev 4.3)

Filed because the SPI framing and BUSY handling in `software/firmware/port/pn5180.c` are built on
them, and a driver contract sourced only from a code comment cannot be checked by a reviewer or by
the V6 peripheral model.

- SPI is fixed at CPOL 0, CPHA 0, 7 Mbit/s maximum, half duplex, MSB first. No chaining: the whole
  instruction is sent and the whole response read as single frames, with no NSS toggle inside a
  frame. MISO is high-ohmic while NSS is high. [section::11.4.1]
- BUSY goes ACTIVE during frame reception and returns to IDLE when the part can accept a new frame
  or has data available; "any data available to be read from the SPI interface is indicated by the
  BUSY signal de-asserted". A parameter error raises the IRQ line with GENERAL_ERROR_IRQ instead of
  a BUSY change. [section::11.4.1] [section::11.4.2]
- Recommended host sequence: assert NSS, perform the data exchange, wait until BUSY is high (step 3,
  optional in normal mode, mandatory with the test bus enabled), deassert NSS, wait until BUSY is
  low. No BUSY rise-latency figure is published, which is why the firmware's rise window is marked
  chosen rather than sourced. [section::11.4.1]
- A read is two SPI frames, the GET instruction and then the response clocked out against dummy
  0xFF bytes, and NSS must go high between the two data streams. [section::11.4.1, figures 6, 8, 9]
  [section::11.4.2]
- Register values in payloads travel least significant byte first; a direct instruction is one
  command byte plus up to 260 parameter bytes; the transmit buffer holds 260 bytes and the receive
  buffer 508. [section::11.4.3]

## Interrupt facts (sections 11.3.2 and the register tables)

- IRQ_STATUS is register 0002h; a flag clears by writing IRQ_CLEAR (0003h) or, per EEPROM
  configuration, on reading IRQ_STATUS. [section::11.3.2]
- Bits the firmware uses or has weighed: bit 0 RX_IRQ_STAT (end of RF reception, the driver's
  slot-answer flag), bit 1 TX_IRQ_STAT (end of RF transmission), bit 14 RX_SOF_DET_IRQ_STAT (RX
  start-of-frame detection), bit 15 RX_SC_DET_IRQ_STAT (RX subcarrier detection, the faster
  empty-slot decision that SLOT_TIMEOUT_US's comment defers to a bench measurement). [table::77]
