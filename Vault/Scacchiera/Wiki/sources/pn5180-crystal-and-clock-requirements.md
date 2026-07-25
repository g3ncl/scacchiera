---
type: source-summary
tags:
  - wiki/source
date_updated: 2026-07-25
source_file: "Datasheets/PN5180A0HN-C3E_C1526287.pdf"
source_title: "PN5180 High-performance multiprotocol full NFC frontend, data sheet"
publisher: NXP Semiconductors
---

# PN5180 clock and crystal requirements

Scoped extract from the [[pn5180]] data sheet covering the clock chain only,
filed because it is what fixes the hub's [[txc-7m27100009]] choice and its load
capacitors. The wider reader architecture is covered by
[[nfcgameboard-schematics]] and [[row-column-antenna-matrix-technique]].

[mpn::PN5180A0HN/C3E] [lcsc::C1526287]

## Why 27.12 MHz

The PN5180 uses an external 27.12 MHz crystal as the clock source for
generating the RF field and its internal timing. 27.12 divided by two is
13.56 MHz, the NFC carrier, so the value is not arbitrary: the datasheet
describes the carrier as "27.12 MHz quartz divided by 2".

The internal PLL can instead take an accurate external clock of 8, 12, 16 or
24 MHz, which "saves the 27.12 MHz crystal" in systems that already have one of
those frequencies. A 27.12 MHz external clock may also be applied at pin CLK1,
in which case duty cycle and jitter need special care.

The ESP32 module's own 40 MHz crystal is not in that list and is not brought
out to a module pin, so it cannot serve this role. [needs_own_crystal::yes]

## Table 142, crystal requirements for ISO/IEC14443 compliant operation

| Symbol | Parameter | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| fxtal | crystal frequency | -100 | - | +100 | ppm |
| ESR | equivalent series resistance | - | 50 | 100 | ohm |
| CL | load capacitance | - | 10 | - | pF |
| Pxtal | crystal power dissipation | - | - | 100 | uW |

[required_cl_pf::10] [max_esr_ohm::100] [max_drive_uw::100] [tolerance_ppm::100]

## Oscillator circuit (section 11.2, Figure 5)

The crystal connects across CLK1 and CLK2, each through a series resistor RD1,
with a load capacitor CL1 from each side to VSS. The datasheet states:

- clock frequency stability "is an important factor for correct operation" and
  jitter must be minimised;
- the crystal "is a component which is impacting the overall performance of the
  system. A high-quality component is recommended here";
- RD1 "reduces the start-up time of the crystal", which matters particularly
  when low-power card detection is used;
- the values of these resistors depend on which crystal is used.

The hub implements this as CLK1/CLK2 through R27/R28 into Y1, with C31/C32 to
ground.

## Load capacitor arithmetic this drives

Two equal capacitors present `CL = C/2 + Cstray` to the crystal. For the
required 10 pF with 2 to 4 pF of trace and CLK-pin stray, C is about 14 pF, so
the design uses 15 pF (about 10.5 pF presented, roughly 10 ppm of pull). The
previous 10 pF pair presented about 8 pF, roughly 41 ppm of pull, spending most
of the ± 100 ppm budget before the crystal's own tolerance was counted.

Related: [[clrc632]], [[esp32-c6-mini-1u]]
