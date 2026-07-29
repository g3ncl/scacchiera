---
type: source-summary
date_updated: 2026-07-29
tags: [wiki/source, wiki/power]
---

# TPS61088RHLR data sheet

Texas Instruments data sheet revision D, August 2021, for the [[tps61088rhlr]] synchronous boost
converter. The immutable source is [[../../Datasheets/TPS61088RHLR_C87357.pdf]].

## Design-dependent values

| Parameter | Published value | Locator |
| --- | ---: | --- |
| Input range | 2.7 to 12 V | Features |
| Package | 20-pin 4.5 x 3.5 mm VQFN, RHL | Sections 3 and 5 |
| Inductor range | 0.47 to 10 uH | Section 8.2.2.5 |
| Switching-frequency range | 200 kHz to 2.2 MHz | Detailed Description |
| Current limit | resistor programmable | Sections 7.3.5 and 8.2.2.3 |
| Current-limit worst-case allowance | calculated value minus 1.3 A | Section 8.2.2.3 |
| VCC capacitor | at least 1 uF | Section 8.2.2.6 |

TI requires the worst-case inductor peak to use minimum input voltage, maximum output and load,
minimum switching frequency, minus 30 percent inductance tolerance, and conservative efficiency.
External compensation must be designed and validated for the chosen 5 V power stage.

[mpn::TPS61088RHLR] [order_code::C87357] [package::RHL-VQFN-20]
