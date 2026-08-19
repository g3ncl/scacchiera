#include "unity.h"

#include <string.h>

#include "core/chessclock.h"

static chessclock_t clock_state;

void setUp(void)
{
    chessclock_init_preset(&clock_state, 0u, PIECE_COLOR_WHITE, 0u);
}

void tearDown(void) {}

static uint32_t white_ms(void)
{
    return chessclock_remaining_ms(&clock_state, PIECE_COLOR_WHITE);
}

static uint32_t black_ms(void)
{
    return chessclock_remaining_ms(&clock_state, PIECE_COLOR_BLACK);
}

static void test_the_presets_sit_on_the_squares_the_gesture_uses(void)
{
    TEST_ASSERT_EQUAL_UINT8(square_from_file_rank('d', 4), time_preset_square(0u));
    TEST_ASSERT_EQUAL_UINT8(square_from_file_rank('d', 5), time_preset_square(1u));
    TEST_ASSERT_EQUAL_UINT8(square_from_file_rank('e', 4), time_preset_square(2u));
    TEST_ASSERT_EQUAL_UINT8(square_from_file_rank('e', 5), time_preset_square(3u));
    TEST_ASSERT_EQUAL_UINT8(SQUARE_INVALID, time_preset_square(TIME_PRESET_COUNT));

    TEST_ASSERT_EQUAL_UINT8(2u, time_preset_for_square(square_from_file_rank('e', 4)));
    TEST_ASSERT_EQUAL_UINT8(TIME_PRESET_NONE,
                            time_preset_for_square(square_from_file_rank('a', 1)));
}

static void test_an_untimed_clock_never_flags(void)
{
    chessclock_init_untimed(&clock_state);
    chessclock_tick(&clock_state, 3600000u);
    TEST_ASSERT_FALSE(chessclock_flagged(&clock_state, NULL));
    TEST_ASSERT_EQUAL_UINT32(0u, white_ms());
}

static void test_only_the_running_side_is_charged(void)
{
    const uint32_t initial = white_ms();
    chessclock_tick(&clock_state, 5000u);
    TEST_ASSERT_EQUAL_UINT32(initial - 5000u, white_ms());
    TEST_ASSERT_EQUAL_UINT32(initial, black_ms());
}

/* Calling tick twice with the same reading must not charge twice. */
static void test_a_repeated_reading_charges_once(void)
{
    const uint32_t initial = white_ms();
    chessclock_tick(&clock_state, 4000u);
    chessclock_tick(&clock_state, 4000u);
    TEST_ASSERT_EQUAL_UINT32(initial - 4000u, white_ms());
}

static void test_switching_charges_the_outgoing_side_first(void)
{
    const uint32_t initial = white_ms();
    chessclock_switch(&clock_state, 7000u);
    TEST_ASSERT_EQUAL_UINT32(initial - 7000u, white_ms());
    TEST_ASSERT_EQUAL_UINT32(initial, black_ms());

    chessclock_tick(&clock_state, 9000u);
    TEST_ASSERT_EQUAL_UINT32(initial - 2000u, black_ms());
    TEST_ASSERT_EQUAL_UINT32(initial - 7000u, white_ms());
}

/* A pause must not be charged to anyone, and resuming must not backdate it. */
static void test_a_pause_costs_nobody_anything(void)
{
    const uint32_t initial = white_ms();
    chessclock_tick(&clock_state, 1000u);
    chessclock_pause(&clock_state, 2000u);
    TEST_ASSERT_TRUE(chessclock_is_paused(&clock_state));

    chessclock_tick(&clock_state, 60000u);
    TEST_ASSERT_EQUAL_UINT32(initial - 2000u, white_ms());

    chessclock_resume(&clock_state, 60000u);
    chessclock_tick(&clock_state, 61000u);
    TEST_ASSERT_EQUAL_UINT32(initial - 3000u, white_ms());
}

static void test_the_flag_falls_at_zero_and_stays_fallen(void)
{
    chessclock_tick(&clock_state, 10u * 60u * 1000u);

    piece_color_t side = PIECE_COLOR_BLACK;
    TEST_ASSERT_TRUE(chessclock_flagged(&clock_state, &side));
    TEST_ASSERT_EQUAL_INT(PIECE_COLOR_WHITE, side);
    TEST_ASSERT_EQUAL_UINT32(0u, white_ms());

    chessclock_tick(&clock_state, 20u * 60u * 1000u);
    TEST_ASSERT_EQUAL_UINT32(0u, white_ms());
}

static void test_the_increment_goes_to_the_side_that_earned_it(void)
{
    const uint32_t initial = white_ms();
    chessclock_tick(&clock_state, 5000u);
    chessclock_credit_increment(&clock_state, PIECE_COLOR_WHITE);
    TEST_ASSERT_EQUAL_UINT32(initial - 5000u + TIME_PRESETS[0].increment_ms, white_ms());
    TEST_ASSERT_EQUAL_UINT32(initial, black_ms());
}

/* The millisecond source wraps every 49.7 days, and every calculation here is
 * a delta, so a wrap must charge the elapsed time rather than the whole range. */
static void test_the_millisecond_wrap_is_a_non_event(void)
{
    chessclock_init_preset(&clock_state, 2u, PIECE_COLOR_WHITE, 0xFFFFF000u);
    const uint32_t initial = white_ms();

    chessclock_tick(&clock_state, 0x00000FA0u);
    TEST_ASSERT_EQUAL_UINT32(initial - 8096u, white_ms());
}

static void test_formatting(void)
{
    char text[8];

    chessclock_init_preset(&clock_state, 2u, PIECE_COLOR_WHITE, 0u);
    TEST_ASSERT_GREATER_THAN_UINT8(0u,
        chessclock_format(&clock_state, PIECE_COLOR_WHITE, text, sizeof(text)));
    TEST_ASSERT_EQUAL_STRING("10:00", text);

    chessclock_tick(&clock_state, 9u * 60u * 1000u + 1000u);
    (void)chessclock_format(&clock_state, PIECE_COLOR_WHITE, text, sizeof(text));
    TEST_ASSERT_EQUAL_STRING("0:59", text);

    /* Under ten seconds the tenths start to matter, so the format changes. */
    chessclock_tick(&clock_state, 9u * 60u * 1000u + 55600u);
    (void)chessclock_format(&clock_state, PIECE_COLOR_WHITE, text, sizeof(text));
    TEST_ASSERT_EQUAL_STRING("0:04.4", text);

    chessclock_tick(&clock_state, 30u * 60u * 1000u);
    (void)chessclock_format(&clock_state, PIECE_COLOR_WHITE, text, sizeof(text));
    TEST_ASSERT_EQUAL_STRING("0:00.0", text);

    TEST_ASSERT_EQUAL_UINT8(0u,
        chessclock_format(&clock_state, PIECE_COLOR_WHITE, text, 4u));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_the_presets_sit_on_the_squares_the_gesture_uses);
    RUN_TEST(test_an_untimed_clock_never_flags);
    RUN_TEST(test_only_the_running_side_is_charged);
    RUN_TEST(test_a_repeated_reading_charges_once);
    RUN_TEST(test_switching_charges_the_outgoing_side_first);
    RUN_TEST(test_a_pause_costs_nobody_anything);
    RUN_TEST(test_the_flag_falls_at_zero_and_stays_fallen);
    RUN_TEST(test_the_increment_goes_to_the_side_that_earned_it);
    RUN_TEST(test_the_millisecond_wrap_is_a_non_event);
    RUN_TEST(test_formatting);
    return UNITY_END();
}
