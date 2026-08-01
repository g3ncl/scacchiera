#ifndef CHESSBOARD_PORT_EXPANDER_H
#define CHESSBOARD_PORT_EXPANDER_H

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

/* TCA9535 on the hub's I2C bus. Everything slow hangs off it: the matrix
 * latch, the reader and display resets, the display command/data line, the
 * light-bar rail enable, the button, and three fault inputs. Coordinates come
 * from board_pins.h, which is generated from the netlist.
 *
 * expander_init() must run before any peripheral driver that owns a reset
 * line, because until it does the reader and both displays are floating
 * rather than held. */

esp_err_t expander_init(void);

esp_err_t expander_set(uint8_t port, uint8_t bit, bool level);
esp_err_t expander_get(uint8_t port, uint8_t bit, bool *level);

/* Drive one output low, then high, then low again. The matrix latches its
 * selection on the rising edge of SEL_RCLK, and this is the only place that
 * edge is produced. */
esp_err_t expander_pulse(uint8_t port, uint8_t bit);

#endif
