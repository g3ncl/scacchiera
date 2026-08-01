#include "unity.h"

#include <string.h>

#include "core/text.h"

#define CANVAS_COLUMNS 16
#define CANVAS_ROWS 16

static uint8_t pixels[CANVAS_COLUMNS * CANVAS_ROWS];
static text_canvas_t canvas;

void setUp(void)
{
    canvas.pixels = pixels;
    canvas.columns = CANVAS_COLUMNS;
    canvas.rows = CANVAS_ROWS;
    text_clear(&canvas);
}

void tearDown(void) {}

static uint8_t pixel_at(uint16_t x, uint8_t y)
{
    const size_t offset = ((size_t)y * CANVAS_COLUMNS) + (x / 2u);
    return (x % 2u) == 0u ? (uint8_t)(pixels[offset] >> 4)
                          : (uint8_t)(pixels[offset] & 0x0Fu);
}

static void test_clear_leaves_nothing_lit(void)
{
    text_set_pixel(&canvas, 3, 3, 15);
    text_clear(&canvas);
    TEST_ASSERT_EQUAL_UINT8(0u, pixel_at(3, 3));
}

/* Two pixels share a byte, high nibble first. Getting that backwards mirrors
 * every character in pairs, which is subtle enough to be worth pinning. */
static void test_even_pixels_are_the_high_nibble(void)
{
    text_set_pixel(&canvas, 0, 0, 0xF);
    TEST_ASSERT_EQUAL_HEX8(0xF0, pixels[0]);
    text_set_pixel(&canvas, 1, 0, 0x5);
    TEST_ASSERT_EQUAL_HEX8(0xF5, pixels[0]);
}

static void test_neighbouring_pixels_do_not_disturb_each_other(void)
{
    text_set_pixel(&canvas, 4, 2, 0xA);
    text_set_pixel(&canvas, 5, 2, 0x3);
    TEST_ASSERT_EQUAL_UINT8(0xA, pixel_at(4, 2));
    TEST_ASSERT_EQUAL_UINT8(0x3, pixel_at(5, 2));
}

/* Off-canvas writes are dropped, not wrapped: text running past the edge must
 * truncate rather than reappear on the next row. */
static void test_out_of_range_pixels_are_dropped(void)
{
    text_set_pixel(&canvas, CANVAS_COLUMNS * 2u, 0, 0xF);
    text_set_pixel(&canvas, 0, CANVAS_ROWS, 0xF);
    for (size_t index = 0; index < sizeof(pixels); index++) {
        TEST_ASSERT_EQUAL_HEX8(0x00, pixels[index]);
    }
}

/* '1' is drawn as a stem with a flag and a foot. Checking a couple of its
 * pixels proves the column packing and the row bit order agree with the
 * generator, which is the pair most likely to be transposed. */
static void test_a_digit_lands_where_the_art_says(void)
{
    text_draw(&canvas, 0, 0, "1", 1, 0xF);
    /* Top row of '1' is 00100, so column 2 lit and column 0 dark. */
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(2, 0));
    TEST_ASSERT_EQUAL_UINT8(0x0, pixel_at(0, 0));
    /* Bottom row is 01110: columns 1, 2 and 3 lit. */
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(1, 6));
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(3, 6));
    TEST_ASSERT_EQUAL_UINT8(0x0, pixel_at(4, 6));
}

static void test_space_draws_nothing_but_advances(void)
{
    const uint16_t after = text_draw(&canvas, 0, 0, " ", 1, 0xF);
    TEST_ASSERT_EQUAL_UINT16(FONT_CELL_WIDTH, after);
    for (size_t index = 0; index < sizeof(pixels); index++) {
        TEST_ASSERT_EQUAL_HEX8(0x00, pixels[index]);
    }
}

static void test_scale_multiplies_every_pixel_into_a_block(void)
{
    text_draw(&canvas, 0, 0, "1", 2, 0xF);
    /* Column 2 of the top row becomes columns 4 and 5, rows 0 and 1. */
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(4, 0));
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(5, 0));
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(4, 1));
    TEST_ASSERT_EQUAL_UINT8(0xF, pixel_at(5, 1));
}

static void test_width_matches_where_drawing_ends(void)
{
    const uint16_t after = text_draw(&canvas, 0, 0, "12:34", 1, 0xF);
    TEST_ASSERT_EQUAL_UINT16(text_width("12:34", 1), after);
    TEST_ASSERT_EQUAL_UINT16(5u * FONT_CELL_WIDTH, after);
}

/* A caller passing mixed case should not silently lose letters. */
static void test_lowercase_folds_to_uppercase(void)
{
    uint8_t upper[CANVAS_COLUMNS * CANVAS_ROWS];
    text_draw(&canvas, 0, 0, "A", 1, 0xF);
    memcpy(upper, pixels, sizeof(upper));
    text_clear(&canvas);
    text_draw(&canvas, 0, 0, "a", 1, 0xF);
    TEST_ASSERT_EQUAL_HEX8_ARRAY(upper, pixels, sizeof(upper));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_clear_leaves_nothing_lit);
    RUN_TEST(test_even_pixels_are_the_high_nibble);
    RUN_TEST(test_neighbouring_pixels_do_not_disturb_each_other);
    RUN_TEST(test_out_of_range_pixels_are_dropped);
    RUN_TEST(test_a_digit_lands_where_the_art_says);
    RUN_TEST(test_space_draws_nothing_but_advances);
    RUN_TEST(test_scale_multiplies_every_pixel_into_a_block);
    RUN_TEST(test_width_matches_where_drawing_ends);
    RUN_TEST(test_lowercase_folds_to_uppercase);
    return UNITY_END();
}
