#ifndef CHESSBOARD_PORT_MATRIX_H
#define CHESSBOARD_PORT_MATRIX_H

#include <stdint.h>

#include "esp_err.h"

/* The sixteen line antennas: eight rows then eight columns, selected one at a
 * time by two daisy-chained 74HC595 registers on the matrix board.
 *
 * Two properties of the wiring drive this whole driver.
 *
 * The registers have no chip select. They share SCLK and MOSI with the reader
 * and both displays, so every byte sent to any of those also shifts into them.
 * Their outputs only change on the SEL_RCLK edge, so that is harmless in
 * itself, but it means the shift and the latch must be atomic with respect to
 * all other SPI traffic. The latch arrives over I2C through the expander,
 * which takes tens of microseconds, so the window is wide and the bus is held
 * across it.
 *
 * The registers also cannot be cleared: SRCLR_N is tied high and OE_N low on
 * the matrix board, and the hub's SEL_SRCLR_N reaches nothing. So the outputs
 * are live with undefined content from power-up, and shifting a known pattern
 * is matrix_init's job rather than a convenience. See docs/hardware/matrix.md.
 */

#define MATRIX_LINE_COUNT 16
#define MATRIX_ROW_COUNT 8

esp_err_t matrix_init(void);

/* Selection is one-hot active low: the selected line goes low, releasing its
 * shunt and turning on its bias steering. Lines 0 to 7 are rows, 8 to 15 are
 * columns. */
esp_err_t matrix_select(uint8_t line);
esp_err_t matrix_deselect_all(void);

#endif
