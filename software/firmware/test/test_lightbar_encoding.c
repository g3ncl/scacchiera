#include "unity.h"

#include <string.h>

#include "port/lightbar_encoding.h"

static uint8_t stream[LIGHTBAR_STREAM_BYTES];

void setUp(void)
{
    memset(stream, 0, sizeof(stream));
}

void tearDown(void) {}

/* The Harvatek part takes red, green, blue in that order (datasheet page 8),
 * not the GRB that WS2812 parts use. Getting it wrong would swap red and
 * green, turning the red illegal-position flash green, which is a functional
 * failure rather than a cosmetic one. */
static void test_order_is_rgb_not_grb(void)
{
    lightbar_pack(stream, 0, 0xAA, 0xBB, 0xCC);
    TEST_ASSERT_EQUAL_HEX8(0xAA, stream[0]);
    TEST_ASSERT_EQUAL_HEX8(0xBB, stream[1]);
    TEST_ASSERT_EQUAL_HEX8(0xCC, stream[2]);
}

static void test_pure_red_lights_only_the_red_byte(void)
{
    lightbar_pack(stream, 0, 0xFF, 0x00, 0x00);
    TEST_ASSERT_EQUAL_HEX8(0xFF, stream[0]);
    TEST_ASSERT_EQUAL_HEX8(0x00, stream[1]);
    TEST_ASSERT_EQUAL_HEX8(0x00, stream[2]);
}

static void test_pixels_do_not_overlap(void)
{
    for (uint8_t index = 0; index < LIGHTBAR_PIXEL_COUNT; index++) {
        lightbar_pack(stream, index, (uint8_t)(index + 1u), 0, 0);
    }
    for (uint8_t index = 0; index < LIGHTBAR_PIXEL_COUNT; index++) {
        TEST_ASSERT_EQUAL_HEX8((uint8_t)(index + 1u),
                               stream[(size_t)index * LIGHTBAR_BYTES_PER_PIXEL]);
    }
}

/* The bars are daisy-chained, so the hub drives one stream of 28 rather than
 * two of 14. The second bar's pixels are the back half. */
static void test_the_chain_is_one_stream_of_both_bars(void)
{
    TEST_ASSERT_EQUAL_INT(28, LIGHTBAR_PIXEL_COUNT);
    TEST_ASSERT_EQUAL_INT(84, LIGHTBAR_STREAM_BYTES);

    lightbar_pack(stream, LIGHTBAR_PIXELS_PER_BAR, 0x11, 0x22, 0x33);
    const size_t offset = (size_t)LIGHTBAR_PIXELS_PER_BAR * LIGHTBAR_BYTES_PER_PIXEL;
    TEST_ASSERT_EQUAL_HEX8(0x11, stream[offset]);
    /* Nothing before it moved. */
    TEST_ASSERT_EQUAL_HEX8(0x00, stream[offset - 1u]);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_order_is_rgb_not_grb);
    RUN_TEST(test_pure_red_lights_only_the_red_byte);
    RUN_TEST(test_pixels_do_not_overlap);
    RUN_TEST(test_the_chain_is_one_stream_of_both_bars);
    return UNITY_END();
}
