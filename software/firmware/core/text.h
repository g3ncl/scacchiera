#ifndef CHESSBOARD_CORE_TEXT_H
#define CHESSBOARD_CORE_TEXT_H

#include <stdint.h>

#include "core/font_glyphs.h"

/* Rendering text into the display's pixel format, kept in core/ so it is
 * testable without a panel.
 *
 * The SSD1362 stores four bits per pixel, two pixels to a byte, high nibble
 * first. A buffer here is therefore `columns` bytes per row, where a column
 * covers two pixels, matching what display_write expects. */

typedef struct {
    uint8_t *pixels;
    uint16_t columns; /* bytes per row, so twice this many pixels wide */
    uint8_t rows;
} text_canvas_t;

void text_clear(const text_canvas_t *canvas);

/* Draws one pixel at the given greyscale level, 0 to 15. Out-of-range
 * coordinates are dropped rather than wrapping, so a string running off the
 * edge truncates instead of reappearing on the next line. */
void text_set_pixel(const text_canvas_t *canvas, uint16_t x, uint8_t y, uint8_t level);

/* Draws text with its top-left at (x, y), each glyph pixel becoming a
 * scale-by-scale block. Returns the x just past the last glyph, so callers can
 * lay out a line without recomputing widths. */
uint16_t text_draw(const text_canvas_t *canvas, uint16_t x, uint8_t y,
                   const char *text, uint8_t scale, uint8_t level);

/* Width in pixels that text_draw would occupy, including the blank column
 * after each cell. */
uint16_t text_width(const char *text, uint8_t scale);

#endif
