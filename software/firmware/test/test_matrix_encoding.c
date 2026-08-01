#include "unity.h"

#include "port/matrix_encoding.h"

void setUp(void) {}
void tearDown(void) {}

#define LINE_COUNT 16

/* Active low, so all ones is nothing selected. Inverting this would forward
 * bias all sixteen PIN diodes at once rather than none. */
static void test_none_selected_is_all_ones(void)
{
    TEST_ASSERT_EQUAL_HEX16(0xFFFFu, MATRIX_PATTERN_NONE);
}

static void test_each_line_clears_exactly_its_own_bit(void)
{
    for (uint8_t line = 0; line < LINE_COUNT; line++) {
        const uint16_t pattern = matrix_pattern_for_line(line);
        const uint16_t cleared = (uint16_t)(~pattern);
        TEST_ASSERT_EQUAL_HEX16((uint16_t)(1u << line), cleared);
    }
}

static void test_exactly_one_line_is_ever_selected(void)
{
    for (uint8_t line = 0; line < LINE_COUNT; line++) {
        const uint16_t pattern = matrix_pattern_for_line(line);
        int selected = 0;
        for (uint8_t bit = 0; bit < LINE_COUNT; bit++) {
            if ((pattern & (uint16_t)(1u << bit)) == 0u) {
                selected++;
            }
        }
        TEST_ASSERT_EQUAL_INT(1, selected);
    }
}

/* Rows are 0 to 7 and columns 8 to 15, and a square is the intersection of
 * one of each. A row pattern must never disturb a column bit. */
static void test_rows_and_columns_do_not_overlap(void)
{
    for (uint8_t row = 0; row < 8u; row++) {
        TEST_ASSERT_EQUAL_HEX16(0xFF00u, matrix_pattern_for_line(row) & 0xFF00u);
    }
    for (uint8_t column = 8u; column < LINE_COUNT; column++) {
        TEST_ASSERT_EQUAL_HEX16(0x00FFu, matrix_pattern_for_line(column) & 0x00FFu);
    }
}

/* The wire order, pinned so a refactor cannot silently transpose the board.
 * The word goes out MSB first, so the high byte reaches the far register and
 * becomes SEL8 to SEL15. */
static void test_byte_order_puts_columns_in_the_high_byte(void)
{
    const uint16_t row0 = matrix_pattern_for_line(0);
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(row0 >> 8));
    TEST_ASSERT_EQUAL_HEX8(0xFEu, (uint8_t)(row0 & 0xFFu));

    const uint16_t column15 = matrix_pattern_for_line(15);
    TEST_ASSERT_EQUAL_HEX8(0x7Fu, (uint8_t)(column15 >> 8));
    TEST_ASSERT_EQUAL_HEX8(0xFFu, (uint8_t)(column15 & 0xFFu));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_none_selected_is_all_ones);
    RUN_TEST(test_each_line_clears_exactly_its_own_bit);
    RUN_TEST(test_exactly_one_line_is_ever_selected);
    RUN_TEST(test_rows_and_columns_do_not_overlap);
    RUN_TEST(test_byte_order_puts_columns_in_the_high_byte);
    return UNITY_END();
}
