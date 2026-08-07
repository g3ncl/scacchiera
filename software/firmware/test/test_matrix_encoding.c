#include "unity.h"

#include "port/matrix_encoding.h"

void setUp(void) {}
void tearDown(void) {}

#define LINE_COUNT 16
#define BOARD_COUNT 4

/* Active low, so all ones is nothing selected. Inverting this would forward
 * bias all sixteen PIN diodes at once rather than none. */
static void test_none_selected_is_all_ones(void)
{
    TEST_ASSERT_EQUAL_HEX32(0xFFFFFFFFu, MATRIX_PATTERN_NONE);
}

static void test_each_line_clears_exactly_its_own_bit(void)
{
    for (uint8_t line = 0; line < LINE_COUNT; line++) {
        const uint32_t pattern = matrix_pattern_for_line(line);
        const uint32_t cleared = (uint32_t)(~pattern);
        TEST_ASSERT_EQUAL_HEX32((uint32_t)(1u << matrix_bit_for_line(line)), cleared);
    }
}

static void test_exactly_one_line_is_ever_selected(void)
{
    for (uint8_t line = 0; line < LINE_COUNT; line++) {
        const uint32_t pattern = matrix_pattern_for_line(line);
        int selected = 0;
        for (uint8_t bit = 0; bit < 32u; bit++) {
            if ((pattern & (uint32_t)(1u << bit)) == 0u) {
                selected++;
            }
        }
        TEST_ASSERT_EQUAL_INT(1, selected);
    }
}

/* No two lines may share a bit. With half of every register unused this is no
 * longer implied by the arithmetic, so it is checked rather than assumed: a
 * stride of 8 with a lane count of 4 is correct and a stride of 4 would alias
 * two boards onto each other. */
static void test_no_two_lines_share_a_bit(void)
{
    uint32_t seen = 0u;
    for (uint8_t line = 0; line < LINE_COUNT; line++) {
        const uint32_t bit = (uint32_t)(1u << matrix_bit_for_line(line));
        TEST_ASSERT_EQUAL_HEX32(0u, seen & bit);
        seen |= bit;
    }
}

/* The unused half of every register. QE to QH drive open pins on all four
 * boards, and they must stay at the deselected level so an all-ones word is
 * genuinely all ones on the wire. */
static void test_the_unused_nibbles_stay_deselected(void)
{
    for (uint8_t line = 0; line < LINE_COUNT; line++) {
        const uint32_t pattern = matrix_pattern_for_line(line);
        for (uint8_t board = 0; board < BOARD_COUNT; board++) {
            const uint8_t byte = (uint8_t)(pattern >> (board * 8u));
            TEST_ASSERT_EQUAL_HEX8(0xF0u, (uint8_t)(byte & 0xF0u));
        }
    }
}

/* Rows are 0 to 7 and columns 8 to 15, and a square is the intersection of
 * one of each. Rows live in boards 0 and 1, the low half of the word; columns
 * in boards 2 and 3, the high half. A row pattern must never disturb a column
 * bit. */
static void test_rows_and_columns_do_not_overlap(void)
{
    for (uint8_t row = 0; row < 8u; row++) {
        TEST_ASSERT_EQUAL_HEX32(0xFFFF0000u, matrix_pattern_for_line(row) & 0xFFFF0000u);
    }
    for (uint8_t column = 8u; column < LINE_COUNT; column++) {
        TEST_ASSERT_EQUAL_HEX32(0x0000FFFFu, matrix_pattern_for_line(column) & 0x0000FFFFu);
    }
}

/* The wire order, pinned so a refactor cannot silently transpose the board.
 * The word goes out MSB first over four bytes, so the first byte sent travels
 * furthest and lands in board 3, which carries lines 12 to 15. The last byte
 * sent stays in board 0, nearest the hub, carrying lines 0 to 3.
 *
 * Line 0 is board 0 lane 0, so it clears the lowest bit of the last byte sent.
 * Line 15 is board 3 lane 3, so it clears bit 3 of the first byte sent. Both
 * are spelled out as literal bytes rather than derived, because deriving them
 * from the same expression the header uses would test nothing. */
static void test_byte_order_places_each_board_in_the_chain(void)
{
    const uint32_t line0 = matrix_pattern_for_line(0);
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line0 >> 24));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line0 >> 16));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line0 >> 8));
    TEST_ASSERT_EQUAL_HEX8(0xFEu, (uint8_t)(line0));

    const uint32_t line15 = matrix_pattern_for_line(15);
    TEST_ASSERT_EQUAL_HEX8(0xF7u, (uint8_t)(line15 >> 24));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line15 >> 16));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line15 >> 8));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line15));

    /* The first line of the second board, which is where a stride mistake
     * shows up: line 4 must move to the next byte, not to bit 4. */
    const uint32_t line4 = matrix_pattern_for_line(4);
    TEST_ASSERT_EQUAL_HEX8(0xFEu, (uint8_t)(line4 >> 8));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(line4));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_none_selected_is_all_ones);
    RUN_TEST(test_each_line_clears_exactly_its_own_bit);
    RUN_TEST(test_exactly_one_line_is_ever_selected);
    RUN_TEST(test_no_two_lines_share_a_bit);
    RUN_TEST(test_the_unused_nibbles_stay_deselected);
    RUN_TEST(test_rows_and_columns_do_not_overlap);
    RUN_TEST(test_byte_order_places_each_board_in_the_chain);
    return UNITY_END();
}
