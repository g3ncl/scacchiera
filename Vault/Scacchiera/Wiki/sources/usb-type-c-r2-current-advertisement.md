---
type: source-summary
tags:
  - wiki/source
  - wiki/power
date_updated: 2026-07-29
source_file: "Clippings/usb-type-c-r2-current-advertisement-extract.pdf"
source_title: "USB Type-C Cable and Connector Specification Release 2.0, current-advertisement extract"
publisher: USB 3.0 Promoter Group
---

# USB Type-C Release 2.0 current advertisement

Five immutable pages extracted from the official specification cover only the sink power states,
CC debounce, and CC voltage tables used by [[usb-type-c-5v-current-advertisement]].

## Sink obligations (sections 4.5.2.3.1 to 4.5.2.3.3)

A sink that wants more than default USB current monitors the voltage across Rd. It may draw at most
1.5 A in the 1.5 A state and at most 3.0 A in the 3.0 A state. A changed Rp advertisement must be
stable for `tRpValueChange` before the state changes, and a downward change requires input current
to be reduced within `tSinkAdj`.

## Timing (Table 4-31)

For a sink that cannot detect idle USB PD signalling, `tRpValueChange` is 10 to 20 ms. The hub's
1 ms RC filter therefore fits inside, rather than replacing, the required digital debounce.

## Sink-side voltage thresholds (Table 4-36)

| Detection | Valid range | Decision threshold |
| --- | --- | --- |
| Rd connected | 0.25 to 2.04 V | attachment envelope |
| Default USB | 0.25 to 0.61 V | 0.66 V |
| 1.5 A at 5 V | 0.70 to 1.16 V | 1.23 V |
| 3.0 A at 5 V | 1.31 to 2.04 V | above 1.23 V |

The ranges include cable-ground voltage drop. Voltages in the gaps between guaranteed bands are
not evidence for the higher current class.

Related: [[esp32-c6-mini-1u]], [[usb-c-pd-fast-charging]]
