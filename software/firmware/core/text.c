#include "core/text.h"

#include <string.h>

void text_clear(const text_canvas_t *canvas)
{
    memset(canvas->pixels, 0, (size_t)canvas->columns * canvas->rows);
}

void text_set_pixel(const text_canvas_t *canvas, uint16_t x, uint8_t y, uint8_t level)
{
    const uint16_t width_pixels = (uint16_t)(canvas->columns * 2u);
    if (x >= width_pixels || y >= canvas->rows) {
        return;
    }
    const size_t offset = ((size_t)y * canvas->columns) + (x / 2u);
    const uint8_t clamped = (uint8_t)(level & 0x0Fu);
    if ((x % 2u) == 0u) {
        /* Even pixels are the high nibble: the controller reads a byte left
         * to right, so the first of the pair is the most significant. */
        canvas->pixels[offset] = (uint8_t)((canvas->pixels[offset] & 0x0Fu) | (clamped << 4));
    } else {
        canvas->pixels[offset] = (uint8_t)((canvas->pixels[offset] & 0xF0u) | clamped);
    }
}

uint16_t text_width(const char *text, uint8_t scale)
{
    if (text == NULL || scale == 0u) {
        return 0;
    }
    return (uint16_t)(strlen(text) * FONT_CELL_WIDTH * scale);
}

uint16_t text_draw(const text_canvas_t *canvas, uint16_t x, uint8_t y,
                   const char *text, uint8_t scale, uint8_t level)
{
    if (text == NULL || scale == 0u) {
        return x;
    }
    uint16_t pen = x;
    for (const char *cursor = text; *cursor != '\0'; cursor++) {
        unsigned char code = (unsigned char)*cursor;
        /* Lowercase folds to uppercase rather than rendering blank, because a
         * caller passing "Check" should not silently lose four letters. */
        if (code >= 'a' && code <= 'z') {
            code = (unsigned char)(code - 'a' + 'A');
        }
        if (code < FONT_FIRST_CODE || code > FONT_LAST_CODE) {
            /* Unknown characters advance without drawing, so alignment of
             * everything after them survives. */
            pen = (uint16_t)(pen + (FONT_CELL_WIDTH * scale));
            continue;
        }
        const uint8_t *glyph = FONT_GLYPHS[code - FONT_FIRST_CODE];
        for (uint8_t column = 0; column < FONT_GLYPH_WIDTH; column++) {
            for (uint8_t row = 0; row < FONT_GLYPH_HEIGHT; row++) {
                if ((glyph[column] & (uint8_t)(1u << row)) == 0u) {
                    continue;
                }
                for (uint8_t dx = 0; dx < scale; dx++) {
                    for (uint8_t dy = 0; dy < scale; dy++) {
                        text_set_pixel(canvas,
                                       (uint16_t)(pen + (column * scale) + dx),
                                       (uint8_t)(y + (row * scale) + dy),
                                       level);
                    }
                }
            }
        }
        pen = (uint16_t)(pen + (FONT_CELL_WIDTH * scale));
    }
    return pen;
}
