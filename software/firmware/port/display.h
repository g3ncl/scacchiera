#ifndef CHESSBOARD_PORT_DISPLAY_H
#define CHESSBOARD_PORT_DISPLAY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "esp_err.h"

/* Two ER-OLEDM3.12-1W modules, SSD1362 controllers, on the shared SPI bus.
 *
 * Three wiring facts shape this driver, all from the hub netlist.
 *
 * Only chip select is per display. OLED_DC and OLED_RESET_N are single nets
 * feeding both modules, so a reset resets the pair and the command/data line
 * is shared. That is fine because only one display is addressed at a time,
 * but it means the pair must be initialised together.
 *
 * D/C sits on the expander, not a GPIO. Every switch between command and data
 * costs an I2C transaction of tens of microseconds. So commands are batched
 * and data is batched, and the two are never interleaved per byte.
 *
 * The panel is 256 by 64 with four bits per pixel, so two pixels share a byte
 * and a column address covers two pixels: 128 columns, 64 rows, 8192 bytes for
 * a full frame. */

#define DISPLAY_COUNT 2
#define DISPLAY_WIDTH_PIXELS 256
#define DISPLAY_HEIGHT_PIXELS 64
#define DISPLAY_COLUMNS 128
#define DISPLAY_ROWS 64
#define DISPLAY_FRAME_BYTES (DISPLAY_COLUMNS * DISPLAY_ROWS)

/* Resets both modules and brings both up. Must run after expander_init,
 * which is what holds them in reset until then. */
esp_err_t display_init(void);

esp_err_t display_set_window(uint8_t display, uint8_t column_start, uint8_t column_end,
                             uint8_t row_start, uint8_t row_end);

/* Writes pixel bytes into the current window. Two pixels per byte, high nibble
 * first. */
esp_err_t display_write(uint8_t display, const uint8_t *data, size_t length);

esp_err_t display_clear(uint8_t display);
esp_err_t display_set_on(uint8_t display, bool on);
esp_err_t display_set_contrast(uint8_t display, uint8_t contrast);

#endif
