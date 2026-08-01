#include "unity.h"

#include "core/hw/clock.h"
#include "core/hw/output.h"
#include "core/hw/scan.h"
#include "core/hw/storage.h"
#include "fake_clock.h"
#include "fake_output.h"
#include "fake_scan.h"
#include "fake_storage.h"

void setUp(void)
{
    fake_clock_reset();
    fake_scan_reset();
    fake_output_reset();
    fake_storage_reset();
}

void tearDown(void) {}

static void test_clock_is_deterministic(void)
{
    TEST_ASSERT_EQUAL_UINT32(0u, hw_clock_now_ms());
    fake_clock_advance(1500u);
    TEST_ASSERT_EQUAL_UINT32(1500u, hw_clock_now_ms());
    fake_clock_set(20u * 60u * 1000u);
    TEST_ASSERT_EQUAL_UINT32(1200000u, hw_clock_now_ms());
}

static void test_scan_returns_the_configured_position(void)
{
    board_snapshot_t configured;
    board_snapshot_clear(&configured);
    board_snapshot_place(&configured, square_from_file_rank('d', 4),
                         PIECE_COLOR_BLACK, PIECE_TYPE_KNIGHT, 9u);
    fake_scan_set_result(&configured);

    board_snapshot_t read;
    TEST_ASSERT_TRUE(hw_scan_board(&read));
    TEST_ASSERT_TRUE(board_snapshot_equal(&read, &configured));
    TEST_ASSERT_EQUAL_UINT(1u, fake_scan_call_count());
}

/* A scan that cannot complete is different from a scan that completed and
 * found a fault. The fake has to be able to produce both. */
static void test_scan_failure_is_distinct_from_a_fault(void)
{
    board_snapshot_t read;
    fake_scan_fail_next(2u);
    TEST_ASSERT_FALSE(hw_scan_board(&read));
    TEST_ASSERT_FALSE(hw_scan_board(&read));
    TEST_ASSERT_TRUE(hw_scan_board(&read));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, read.fault.fault);
    TEST_ASSERT_EQUAL_UINT(3u, fake_scan_call_count());
}

static void test_output_records_both_sides_separately(void)
{
    hw_output_display_text(PIECE_COLOR_WHITE, "05:00");
    hw_output_display_text(PIECE_COLOR_BLACK, "04:58");
    hw_output_light_cue(PIECE_COLOR_BLACK, LIGHT_CUE_ILLEGAL);
    TEST_ASSERT_EQUAL_STRING("05:00", fake_output_last_text(PIECE_COLOR_WHITE));
    TEST_ASSERT_EQUAL_STRING("04:58", fake_output_last_text(PIECE_COLOR_BLACK));
    TEST_ASSERT_EQUAL_INT(LIGHT_CUE_NONE, fake_output_last_cue(PIECE_COLOR_WHITE));
    TEST_ASSERT_EQUAL_INT(LIGHT_CUE_ILLEGAL, fake_output_last_cue(PIECE_COLOR_BLACK));
}

static void test_storage_round_trip(void)
{
    board_snapshot_t saved;
    board_snapshot_clear(&saved);
    board_snapshot_place(&saved, 12u, PIECE_COLOR_WHITE, PIECE_TYPE_BISHOP, 3u);
    TEST_ASSERT_TRUE(hw_storage_save_snapshot(&saved));

    board_snapshot_t loaded;
    TEST_ASSERT_TRUE(hw_storage_load_snapshot(&loaded));
    TEST_ASSERT_TRUE(board_snapshot_equal(&loaded, &saved));
}

static void test_nothing_loads_before_anything_is_saved(void)
{
    board_snapshot_t loaded;
    TEST_ASSERT_FALSE(hw_storage_load_snapshot(&loaded));
}

/* V5 requires injecting write failure at every transaction boundary. A failed
 * write must not leave a half-written snapshot that later loads as valid. */
static void test_failed_write_leaves_nothing_loadable(void)
{
    board_snapshot_t saved;
    board_snapshot_clear(&saved);
    board_snapshot_place(&saved, 12u, PIECE_COLOR_WHITE, PIECE_TYPE_BISHOP, 3u);
    TEST_ASSERT_TRUE(hw_storage_save_snapshot(&saved));

    fake_storage_fail_writes(1u);
    TEST_ASSERT_FALSE(hw_storage_save_snapshot(&saved));
    TEST_ASSERT_FALSE(fake_storage_has_snapshot());

    board_snapshot_t loaded;
    TEST_ASSERT_FALSE(hw_storage_load_snapshot(&loaded));
    TEST_ASSERT_EQUAL_UINT(2u, fake_storage_write_count());
}

static void test_clear_removes_the_snapshot(void)
{
    board_snapshot_t saved;
    board_snapshot_clear(&saved);
    TEST_ASSERT_TRUE(hw_storage_save_snapshot(&saved));
    TEST_ASSERT_TRUE(hw_storage_clear());
    TEST_ASSERT_FALSE(fake_storage_has_snapshot());
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_clock_is_deterministic);
    RUN_TEST(test_scan_returns_the_configured_position);
    RUN_TEST(test_scan_failure_is_distinct_from_a_fault);
    RUN_TEST(test_output_records_both_sides_separately);
    RUN_TEST(test_storage_round_trip);
    RUN_TEST(test_nothing_loads_before_anything_is_saved);
    RUN_TEST(test_failed_write_leaves_nothing_loadable);
    RUN_TEST(test_clear_removes_the_snapshot);
    return UNITY_END();
}
