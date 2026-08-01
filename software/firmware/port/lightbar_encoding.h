#ifndef CHESSBOARD_PORT_LIGHTBAR_ENCODING_H
#define CHESSBOARD_PORT_LIGHTBAR_ENCODING_H

#include <stdint.h>

/* Pixel packing for the Harvatek T37K3RGB, kept apart from lightbar.c so the
 * host gate can test it.
 *
 * The order is RGB, not the GRB that WS2812 parts use. Datasheet page 8: "The
 * 24-bit data consist of red, green and blue data, each with 8-bit width, and
 * are transferred with MSB first." Assuming the WS2812 convention here would
 * swap red and green, which would turn the red illegal-position flash green,
 * so it is tested rather than remembered.
 *
 * Both bars are one chain: bar 0's data output feeds bar 1's data input, so
 * the hub drives 28 pixels in a single stream. Indices 0 to 13 are the first
 * bar and 14 to 27 the second. */

#define LIGHTBAR_PIXELS_PER_BAR 14
#define LIGHTBAR_BAR_COUNT 2
#define LIGHTBAR_PIXEL_COUNT (LIGHTBAR_PIXELS_PER_BAR * LIGHTBAR_BAR_COUNT)
#define LIGHTBAR_BYTES_PER_PIXEL 3
#define LIGHTBAR_STREAM_BYTES (LIGHTBAR_PIXEL_COUNT * LIGHTBAR_BYTES_PER_PIXEL)

static inline void lightbar_pack(uint8_t *stream, uint8_t index,
                                 uint8_t red, uint8_t green, uint8_t blue)
{
    uint8_t *pixel = &stream[(size_t)index * LIGHTBAR_BYTES_PER_PIXEL];
    pixel[0] = red;
    pixel[1] = green;
    pixel[2] = blue;
}

#endif
