#ifndef CHESSBOARD_PORT_MATRIX_ENCODING_H
#define CHESSBOARD_PORT_MATRIX_ENCODING_H

#include <stdint.h>

/* The selection word, kept apart from matrix.c so the host gate can test it
 * without ESP-IDF. Getting the polarity backwards would select all sixteen
 * lines at once instead of none, so it is tested rather than trusted.
 *
 * Bit n of the word drives SEL n. That mapping is not a convention chosen
 * here, it falls out of the wiring: the word goes out MSB first, the first bit
 * clocked travels furthest along the daisy chain, U1's overflow feeds U2, and
 * U2's outputs are SEL8 to SEL15. So the first bit sent lands on SEL15 and the
 * last on SEL0, which is exactly bit-n-drives-SEL-n.
 *
 * Selection is active low: a line is selected when its bit is 0, which
 * releases its shunt FET and turns on its bias steering. All ones is the
 * all-deselected state. */

#define MATRIX_PATTERN_NONE ((uint16_t)0xFFFFu)

static inline uint16_t matrix_pattern_for_line(uint8_t line)
{
    return (uint16_t)(MATRIX_PATTERN_NONE ^ (uint16_t)(1u << line));
}

#endif
