#ifndef CHESSBOARD_PORT_MATRIX_ENCODING_H
#define CHESSBOARD_PORT_MATRIX_ENCODING_H

#include <stdint.h>

/* The selection word, kept apart from matrix.c so the host gate can test it
 * without ESP-IDF. Getting the polarity backwards would select all sixteen
 * lines at once instead of none, so it is tested rather than trusted.
 *
 * The sensing plane is four boards of four lanes (docs/hardware/quad.md), each
 * with its own 74HC595, chained hub to board 0 to board 3. Four eight-bit
 * registers make this a 32-bit shift where the superseded monolith's two made
 * it 16.
 *
 * **Half of every register is wired to nothing**, and that is what makes the
 * mapping non-obvious. A board uses QA to QD for its four lanes and leaves QE
 * to QH open, so the word carries four bits of payload in every byte and four
 * of padding.
 *
 * Which four falls out of the wiring rather than being chosen. The word goes
 * out MSB first, so the first bit clocked travels furthest along the chain and
 * the last byte sent settles in board 0, nearest the hub. Inside a register,
 * the last bit clocked in sits at QA and the first at QH. So the byte for a
 * board holds its four lanes in the byte's **low** nibble, and:
 *
 *     line 0 to 3   -> board 0, word bits 0 to 3
 *     line 4 to 7   -> board 1, word bits 8 to 11
 *     line 8 to 11  -> board 2, word bits 16 to 19
 *     line 12 to 15 -> board 3, word bits 24 to 27
 *
 * which is the stride below. Lines 0 to 7 are rows and 8 to 15 are columns, so
 * boards 0 and 1 are the row plane and boards 2 and 3 the column plane, in
 * chain order. That ordering is an assembly convention this file fixes: the
 * boards are identical, so nothing on them records which is which.
 *
 * Selection is active low: a line is selected when its bit is 0, which
 * releases its shunt FET and turns on its bias steering. All ones is the
 * all-deselected state. The padding bits stay 1 with the rest; they drive
 * open pins, so their value is arbitrary, and keeping them at the deselected
 * level means a stuck-at-zero fault reads as one of ours rather than hiding. */

#define MATRIX_PATTERN_NONE ((uint32_t)0xFFFFFFFFu)

/* Lanes per board, and so the number of payload bits in each byte. */
#define MATRIX_LANES_PER_BOARD 4u

static inline uint8_t matrix_bit_for_line(uint8_t line)
{
    const uint8_t board = (uint8_t)(line / MATRIX_LANES_PER_BOARD);
    const uint8_t lane = (uint8_t)(line % MATRIX_LANES_PER_BOARD);
    return (uint8_t)(board * 8u + lane);
}

static inline uint32_t matrix_pattern_for_line(uint8_t line)
{
    return (uint32_t)(MATRIX_PATTERN_NONE ^ (uint32_t)(1u << matrix_bit_for_line(line)));
}

#endif
