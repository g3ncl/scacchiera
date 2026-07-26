---
type: source-summary
date_updated: 2026-07-26
tags: [wiki/source, wiki/safety]
---

# TLV7042 data sheet

Texas Instruments data sheet for the [[tlv7042]] dual nanopower comparator. The immutable source
is [[../../Datasheets/TLV7042DGKR_C2760466.pdf]].

The device accepts 1.6 to 6.5 V, has rail-to-rail inputs, two open-drain outputs, internal
hysteresis, power-on reset, and fail-safe inputs. Typical supply current is 315 nA and maximum
input offset at 25 degrees Celsius is 8 mV. The DGK package is VSSOP-8, with OUTA pin 1, INA- pin 2,
INA+ pin 3, ground pin 4, INB+ pin 5, INB- pin 6, OUTB pin 7, and VCC pin 8.

[mpn::TLV7042DGKR] [order_code::C2760466] [package::VSSOP-8]

The two outputs wire together so either a too-cold or too-hot comparison disables charging. The
comparator is powered from USB input, independently of hub firmware.
