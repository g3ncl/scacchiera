# ER-OLEDM3.12-1W manufacturer evidence capture

Captured from EastRising/BuyDisplay on 2026-07-29.

- Product page: https://www.buydisplay.com/white-grayscale-3-12-inch-oled-display-module-256x64-arduino-raspberry-pi
- Manufacturer datasheet: https://www.buydisplay.com/download/manual/ER-OLEDM3.12-1_Datasheet.pdf
- Datasheet revision: 1.0, preliminary release, 2025-08-07
- Exact order number: ER-OLEDM3.12-1W, white display module
- Controller: SSD1362
- Outline: 100.00 by 33.00 mm
- Interface options: 6800 8-bit, 8080 8-bit, I2C and four-wire serial SPI
- Header pinout for four-wire SPI: pin 1 VCC; pins 2 and 3 GND; pin 4 RES; pin 5 CS; pin 6 D/C; pins 7 and 8 tied to ground; pin 9 D0/SCLK; pin 10 D1/SID; unused D2 through D7 tied low.
- VCC absolute maximum: 3.6 V
- Logic supply operating range: 3.0 to 3.5 V
- Supply current at 3.3 V with 100 percent display area on: 320 mA maximum
- Sleep current: 2 mA maximum
- Operating temperature: -40 to 85 degrees Celsius in the datasheet absolute maximum table; the product page states -40 to 70 degrees Celsius.
- Product availability: in stock at USD 20.25 when checked.

## Open contradiction

The product page labels 2 mA as the module maximum supply current, while datasheet section 4.3 labels 320 mA as the maximum active current and 2 mA as the maximum sleep current. The design uses 320 mA per display because it is the conservative direction. The supplier must clarify the product-page error before V1 can close.

The supplier site denied an automated download of the PDF with HTTP 403, so this immutable text capture records the design-relevant fields read from the manufacturer PDF. Filing the original PDF remains open.
