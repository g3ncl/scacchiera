---
type: entity
tags:
  - wiki/entity
  - wiki/component
date_updated: 2026-07-25
source_count: 1
---

# SK6805MINI-E

The addressable RGB pixel on the [light bar](../../../../docs/hardware/lightbar.md),
designators **D1 to D14**. Controller inside the LED, 800 kHz single-wire chain,
5 mA per colour channel.

[mpn::SK6805MINI-E] [lcsc::C5200774] [board::lightbar] [jlc_library::Extended]
[package_mm::3.2x2.8x1.78] [channel_current_ma::5] [unit_cost_eur::0.10]

Datasheet facts and the contradiction between revisions:
[[sk68xx-mini-e-led-datasheets]].

## Why this part

JLCPCB cannot assemble a 120 x 8.5 mm outline, so the light bar is populated by
hand. That rules out the WS2812C-2020 it replaced, whose four pads sit
underneath the body where an iron cannot reach. The `-E` suffix means the legs
extend **outside** the body, so every joint is reachable with a tip. It is the
part the mechanical-keyboard community hand-solders by the hundred.

The 5 mA `SK6805` variant was chosen over the 12 mA `SK6812` in the same package
because it keeps the same current class as the WS2812C-2020, so the hub's 5 V
rail needs no change and no firmware brightness cap:

| | per pixel white | 14 pixels | both bars |
| --- | --- | --- | --- |
| SK6805, 5 mA/ch + 1 mA IDD | 16 mA | 224 mA | **448 mA** |
| SK6812, 12 mA/ch + 1 mA IDD | 37 mA | 518 mA | 1.04 A |

The TPS2553 limiter is set near 0.67 A by R17, so the 5 mA variant fits with
margin while the 12 mA variant would latch the bars off.

## What it cost: pixel count

Its legs make it wide. Pad span is 6.80 mm and courtyard 7.30 mm, against the
WS2812C-2020's 2.0 mm body. With the 4-pin JST GH taking 9.46 mm of exclusive
length, only **14 pixels fit** on the 120 mm bar where the functional spec
originally asked for 17. 15 is reachable only by letting courtyards overlap; 16
does not fit at any pitch that keeps the pads apart. This is a real change to
[functional/interface.md](../../../../docs/functional/interface.md), not an
implementation detail.

## Open risk: the part is not fully verifiable

Recorded rather than smoothed over, because the design is committed to it:

- LCSC returns **404** for C5200774. It is a JLCPCB-internal code, so no
  authoritative datasheet exists for the exact ordering code.
- JLCPCB lists its manufacturer as **Normand** and its package as **SMD3528**,
  which matches neither the rev 02 (3.2 x 2.8) nor rev 08 (3.5 x 3.7) document.
- The two OPSCO documents give **different pinouts**. The design uses rev 02
  (1 VDD, 2 DOUT, 3 GND, 4 DIN) because LCSC C5149201's manufacturer and MPN
  match that document exactly, and C5149201 is the same package family.
- The footprint's pad geometry comes from KiCad's `LED_SK6812MINI-E` land
  pattern, whose description cites the C5149201 datasheet. KiCad ships only a
  **ReverseMount** variant, so the project's top-mount version is its mirror.

Before this board is ordered, confirm the delivered part's pinout and mount side
against a physical sample. Getting VDD and GND swapped destroys 14 pixels per
bar. The lower-risk alternative is SK6812MINI-E (C5149201), which has a real
LCSC listing and matching datasheet, at the cost of needing a firmware
brightness cap.

Related: [[jlcpcb]], [[jlcpcb-basic-part-sourcing]]
