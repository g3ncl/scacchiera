---
type: source-summary
tags:
  - wiki/source
  - wiki/component
date_updated: 2026-07-30
source_file: "Datasheets/SSD1362_SOLOMON.pdf"
source_title: "SSD1362 Rev 1.0 Advance Information"
publisher: "Solomon Systech"
---

# SSD1362 datasheet

Solomon Systech's February 2015 Rev 1.0 advance-information data sheet for the
[[ssd1362]] 256 by 64, 16-gray-scale OLED controller fitted inside both
[[er-oledm3-12-1w]] modules. The filed copy is the manufacturer's 62-page document mirrored by
OSPTEK because the manufacturer-linked display sites rejected automated download.

[mpn::SSD1362] [revision::1.0] [document_status::advance information]

## Interface and reset

Section 6 and Tables 6-1 and 6-2 define four-wire SPI as BS[2:0] = 000, with D0 as SCLK, D1 as
SDIN, CS# active low, D/C# selecting command or data, and RES# active low. Unused D2 through D7,
E, and R/W# are tied low. Section 7.1.3 says SDIN is sampled on each SCLK rising edge, most
significant bit first, and serial operation is write-only.

Section 7.9 requires stable VCI and VDDIO for at least 1 ms before a reset pulse of at least 100 us.
Commands wait at least 50 ms after those rails become stable. Section 7.11 records that reset turns
the display off, clears the serial shift register, and restores the documented register defaults.

## Electrical limits used by the design

Table 10-1 limits an input to VSS - 0.3 V through VDDIO + 0.3 V and lists operation from -40 to
85 degrees Celsius. Table 11-1 specifies VIH at 0.8 VDDIO minimum and VIL at 0.2 VDDIO maximum.

Table 12-4 covers four-wire SPI at VCI from 1.65 to 3.5 V and 25 degrees Celsius. Its minimum clock
period is 100 ns. Minimum clock high and low times are 20 ns and 25 ns. Write data needs 15 ns of
setup and 30 ns of hold. Chip select needs 20 ns of setup and 10 ns of hold, while D/C# needs 15 ns
of setup and 40 ns of hold. Both rise and fall time are limited to 15 ns maximum.

The document contains only a 25-degree SPI timing table and remains labelled advance information.
Those limitations stay visible when its timing is used as V3 evidence.
