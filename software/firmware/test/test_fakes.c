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

static void a_game_of(game_record_t *record, uint16_t plies)
{
    game_record_clear(record);
    record->ply_count = plies;
    for (uint16_t index = 0u; index < plies; index++) {
        record->moves[index] = move_make((square_t)12, (square_t)28, PIECE_TYPE_NONE, 0u);
    }
    record->has_time_control = true;
    record->remaining_ms[0] = 300000u;
    record->remaining_ms[1] = 297000u;
    game_record_seal(record);
}

static void test_storage_round_trip(void)
{
    game_record_t saved;
    a_game_of(&saved, 3u);
    TEST_ASSERT_TRUE(hw_storage_save_game(&saved));

    game_record_t loaded;
    TEST_ASSERT_TRUE(hw_storage_load_game(&loaded));
    TEST_ASSERT_EQUAL_UINT16(3u, loaded.ply_count);
    TEST_ASSERT_EQUAL_UINT32(297000u, loaded.remaining_ms[1]);
}

static void test_nothing_loads_before_anything_is_saved(void)
{
    game_record_t loaded;
    TEST_ASSERT_FALSE(hw_storage_load_game(&loaded));
}

/* V5 requires injecting write failure at every transaction boundary. A failed
 * write must not leave a half-written game that later loads as valid. */
static void test_failed_write_leaves_nothing_loadable(void)
{
    game_record_t saved;
    a_game_of(&saved, 2u);
    TEST_ASSERT_TRUE(hw_storage_save_game(&saved));

    fake_storage_fail_writes(1u);
    TEST_ASSERT_FALSE(hw_storage_save_game(&saved));
    TEST_ASSERT_FALSE(fake_storage_has_game());

    game_record_t loaded;
    TEST_ASSERT_FALSE(hw_storage_load_game(&loaded));
    TEST_ASSERT_EQUAL_UINT(2u, fake_storage_write_count());
}

/* A record that survived the write but not intact must be refused rather than
 * half-trusted: a plausible garbage board is worse than no board. */
static void test_a_corrupt_record_does_not_load(void)
{
    game_record_t saved;
    a_game_of(&saved, 4u);
    TEST_ASSERT_TRUE(hw_storage_save_game(&saved));

    fake_storage_corrupt();
    game_record_t loaded;
    TEST_ASSERT_FALSE(hw_storage_load_game(&loaded));
}

static void test_clear_removes_the_game(void)
{
    game_record_t saved;
    a_game_of(&saved, 1u);
    TEST_ASSERT_TRUE(hw_storage_save_game(&saved));
    TEST_ASSERT_TRUE(hw_storage_clear_game());
    TEST_ASSERT_FALSE(fake_storage_has_game());
}

/* The registry has to outlive a game, or a board forgets what its pieces are
 * the first time someone starts a new one. */
static void test_the_registry_survives_the_game_being_cleared(void)
{
    piece_registry_t registry;
    registry_init(&registry);
    TEST_ASSERT_TRUE(registry_add(&registry, 0x77u, PIECE_COLOR_BLACK, PIECE_TYPE_KING, 0u));
    registry_seal(&registry);
    TEST_ASSERT_TRUE(hw_storage_save_registry(&registry));

    game_record_t saved;
    a_game_of(&saved, 1u);
    TEST_ASSERT_TRUE(hw_storage_save_game(&saved));
    TEST_ASSERT_TRUE(hw_storage_clear_game());

    piece_registry_t loaded;
    TEST_ASSERT_TRUE(hw_storage_load_registry(&loaded));
    TEST_ASSERT_TRUE(registry_contains(&loaded, 0x77u));
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
    RUN_TEST(test_a_corrupt_record_does_not_load);
    RUN_TEST(test_clear_removes_the_game);
    RUN_TEST(test_the_registry_survives_the_game_being_cleared);
    return UNITY_END();
}
