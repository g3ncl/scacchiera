# NTCLE317E4103SBA R/T curve coefficients (Vishay curve material A, B25/85 = 3984 K)

Extracted source, not a summary. The NTCLE317E4103SBA data sheet
(`NTCLE317E4103SBA_C3154341.pdf`) gives R25, B25/85 and R85 but prints no R/T table; it directs the
reader to Vishay's curve list for the resistance-versus-temperature characteristic. This file holds
that characteristic for the exact ceramic material this part uses, so the values are traceable
without the 13 MB workbook in the repository.

## Provenance

- Publisher: Vishay Intertechnology (Vishay BCcomponents)
- Document: `https://www.vishay.com/doc?29130`, reached from
  `https://www.vishay.com/en/thermistors/ntc-curve-list/`
- Archive member: `my_Vishay_NTC_curvev6_11/my_VISHAY_NTC_curvev6_11.xls`, workbook version v6_11,
  file date 2022-06-22
- Sheet `dbase ceramic types`, header row 6, data row 10
- Retrieved: 2026-07-26

## Part to material binding

Sheet `dbase coomponents` (Vishay's spelling), row 4798, verbatim fields:

```
NTCLE317E4103SBA, R25 = 10000, Tmin = -55, Tmax = 150, Tref = 25,
B reference points 25 / 85, B tolerance 0,5, sensor type "two point", ceramic type "SP"
```

## Curve coefficients, verbatim

Sheet `dbase ceramic types`, row 10, `number = 10`, `name = mat A. with Bn=3984K`,
`tol Bvalue = 0,5`:

```
A  = -14,65719769
B  =  4798,842
C  = -115334
D  = -3730535
A1 =  0,00335401643468053
B1 =  0,000256523550896126
C1 =  0,00000260597012072052
D1 =  0,0000000632926126487455
```

Vishay writes decimals with a comma. In point notation:

| Coefficient | Value | Direction |
| --- | --- | --- |
| A | -14.65719769 | resistance from temperature |
| B | 4798.842 | resistance from temperature |
| C | -115334.0 | resistance from temperature |
| D | -3730535.0 | resistance from temperature |
| A1 | 0.00335401643468053 | temperature from resistance |
| B1 | 0.000256523550896126 | temperature from resistance |
| C1 | 2.60597012072052e-06 | temperature from resistance |
| D1 | 6.32926126487455e-08 | temperature from resistance |

## Forms

Temperature in kelvin, resistance in ohms:

```
R(T)  = R25 * exp(A + B/T + C/T^2 + D/T^3)
1/T   = A1 + B1*ln(R/R25) + C1*ln(R/R25)^2 + D1*ln(R/R25)^3
```

A1 is 1/298.15 to fifteen digits, which is the 25 degree Celsius reference the second form is
built around.

## Agreement with the immutable part data sheet

Evaluating the first form with R25 = 10000 ohm reproduces the two resistance values the part data
sheet publishes, and the coefficients imply the published B constant:

| Quantity | From these coefficients | Part data sheet |
| --- | --- | --- |
| R at 25 degrees Celsius | 10000.00 ohm | 10 000 ohm (Quick Reference Data) |
| R at 85 degrees Celsius | 1066.11 ohm | 1066.1 ohm (Quick Reference Data) |
| Implied B25/85 | 3984.0 K | 3984 K (Quick Reference Data) |
