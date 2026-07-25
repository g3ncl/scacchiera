---
type: source-summary
tags:
  - wiki/source
date_updated: 2026-07-25
source_file: "Datasheets/7M27100009_C90919.pdf"
source_title: "TXC 7M Series SMD Seam Sealing Crystals, 3.2 x 2.5 x 0.7 mm"
publisher: TXC Corporation
---

# TXC 7M series crystal datasheet

Filed because [[txc-7m27100009]] is the 27.12 MHz reference for the
[hub board](../../../../docs/hardware/hub.md)'s [[pn5180]]. Series datasheet
plus the LCSC catalog values for the specific ordering code.

[mpn::7M27100009] [lcsc::C90919] [frequency_mhz::27.12]

## Series specifications (7M, from the datasheet)

| Parameter | Value |
| --- | --- |
| Package | 3.2 x 2.5 x 0.7 mm |
| Frequency range | 10 to 64 MHz |
| Frequency tolerance at 25 C | ± 30 ppm, or specify |
| Frequency stability over temperature | ± 30 ppm, or specify |
| Operating temperature | -10 to +70 C, or specify |
| Shunt capacitance C0 | **3 pF max** |
| Drive level | 1 to 200 uW, **100 uW typical** |
| Load capacitance | **10 pF, or specify** |
| Aging at 25 C | ± 3 ppm/year max |
| Storage temperature | -40 to +85 C |

## Ordering-code values for C90919 (LCSC catalog)

| Parameter | Value |
| --- | --- |
| Frequency | 27.12 MHz |
| Load capacitance | 10 pF |
| ESR | 60 ohm |
| Frequency tolerance | ± 10 ppm |
| Frequency stability | ± 15 ppm |
| Operating temperature | -20 to +70 C |
| Package | SMD3225-4P |
| JLCPCB library | Extended |
| Stock at capture | 1,905 |
| Unit price at 5+ | $0.1681 |

[load_capacitance_pf::10] [esr_ohm::60] [tolerance_ppm::10] [stability_ppm::15]

## Fit against the PN5180 requirement

Every value clears [[pn5180]] Table 142 (see
[[pn5180-crystal-and-clock-requirements]]):

| Requirement | PN5180 limit | This part |
| --- | --- | --- |
| Load capacitance | 10 pF typ | 10 pF |
| ESR | 50 typ, 100 max | 60 |
| Frequency tolerance | ± 100 ppm | ± 10 ppm, ± 15 ppm over temperature |
| Crystal power dissipation | 100 uW max | 100 uW typical |

Drive level sits at the PN5180's ceiling rather than below it, which is the one
value with no margin. The datasheet's series range allows up to 200 uW, so the
part tolerates it; the constraint is the reader's, not the crystal's.

Related: [[jlcpcb]], [[esp32-c6-mini-1u]]
