#ifndef CHESSBOARD_PORT_LIGHTBAR_H
#define CHESSBOARD_PORT_LIGHTBAR_H

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

#include "port/lightbar_encoding.h"

/* The two player bars, driven as one 28-pixel chain through a 3.3 V to 5 V
 * buffer on IO14. The 5 V rail behind them is gated by LED_EN on the expander
 * and current limited by a TPS2553 whose latch-off fault comes back on
 * LED_FAULT_N, also on the expander. */

esp_err_t lightbar_init(void);

void lightbar_set(uint8_t index, uint8_t red, uint8_t green, uint8_t blue);
void lightbar_set_bar(uint8_t bar, uint8_t red, uint8_t green, uint8_t blue);
void lightbar_clear(void);

/* Pushes the buffer out. Nothing changes on the bars until this is called. */
esp_err_t lightbar_show(void);

esp_err_t lightbar_set_rail(bool on);
esp_err_t lightbar_rail_faulted(bool *faulted);

#endif
