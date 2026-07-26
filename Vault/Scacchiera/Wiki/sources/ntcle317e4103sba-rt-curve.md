---
type: source-summary
tags:
  - wiki/source
  - wiki/component
  - wiki/battery
date_updated: 2026-07-26
source_file: "Datasheets/NTCLE317E4103SBA_C3154341_rt-curve.md"
source_title: "Vishay NTC curve coefficients for ceramic material A, B25/85 = 3984 K"
publisher: "Vishay Intertechnology"
---

# NTCLE317E4103SBA R/T curve

Second source for [[ntcle317e4103sba]], filling the gap its
[[ntcle317e4103sba-datasheet|part data sheet]] leaves open. That data sheet publishes R25, B25/85
and R85 and then points at Vishay's curve list for the resistance-versus-temperature
characteristic, so the design had no filed curve to compute a threshold from.

[mpn::NTCLE317E4103SBA] [order_code::C3154341] [vishay_document::29130]
[ceramic_curve::mat A. with Bn=3984K] [curve_number::10]

## Values the design depends on

The extracted source holds the eight coefficients verbatim. The design uses the
resistance-from-temperature form:

```
R(T) = R25 * exp(A + B/T + C/T^2 + D/T^3)
```

| Coefficient | Value |
| --- | --- |
| A | -14.65719769 |
| B | 4798.842 |
| C | -115334.0 |
| D | -3730535.0 |

Vishay's component database binds this exact part to ceramic type `SP`, whose curve is the
`B25/85 = 3984 K` material above (sheet `dbase coomponents` row 4798, sheet `dbase ceramic types`
row 10).

## Why it matters

The gate's cold cutoff sits near 4.5 degrees Celsius against a 0 degree limit, so a few tenths of a
kelvin of curve error is a real fraction of the margin. A single-beta fit from R25 and B25/85 alone,
which is all the part data sheet supports, reads 4.14 percent high at 0 degrees Celsius: 0.80 K of
false warmth exactly where the margin is thinnest, and in the unsafe direction.

| Temperature | This curve | Single-beta fit | Error of the fit |
| --- | --- | --- | --- |
| 0 degrees Celsius | 32624 ohm | 33973 ohm | -0.80 K |
| 25 degrees Celsius | 10000 ohm | 10000 ohm | 0 K |
| 40 degrees Celsius | 5324 ohm | 5273 ohm | +0.24 K |

## Agreement with the immutable part data sheet

Two independent Vishay statements about the same bead agree to the digits the part data sheet
prints: this curve gives 10000.00 ohm at 25 degrees Celsius and 1066.11 ohm at 85, against the
published 10 000 ohm and 1066.1 ohm, and implies B25/85 = 3984.0 K against the published 3984 K.
`hardware/tests/test_sim_interlock.py` asserts that agreement, so a wrong coefficient cannot pass
unnoticed.

## Simulation treatment

The curve is `datasheet_bounded` and used directly, not fitted. Sensor tolerance enters the
[[v3-charge-interlock|corner sweep]] as the part data sheet's temperature accuracy (0.5 K from 25 to
85 degrees Celsius, 1.0 K over the wider range) rather than as a perturbation of R25, because that
accuracy line already carries the R25 and B tolerances and counting both would double them.

## Conflicts

None open. The two Vishay sources agree.
