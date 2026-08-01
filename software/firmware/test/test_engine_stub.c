#include "unity.h"

#include "core/engine.h"

static engine_state_t engine;
static board_snapshot_t snapshot;

void setUp(void)
{
    engine_init(&engine);
    board_snapshot_clear(&snapshot);
}

void tearDown(void) {}

/* These tests pin the stub's contract deliberately. They are expected to be
 * rewritten when the engine is real; until then they stop a caller from
 * quietly treating "not implemented" as "legal". */

static void test_stub_reports_itself_unimplemented(void)
{
    TEST_ASSERT_FALSE(engine_is_implemented());
}

static void test_init_leaves_no_position(void)
{
    TEST_ASSERT_FALSE(engine.has_position);
}

static void test_clean_snapshot_is_recorded_but_never_accepted(void)
{
    board_snapshot_place(&snapshot, square_from_file_rank('e', 2),
                         PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 5u);
    const engine_result_t result = engine_apply_snapshot(&engine, &snapshot);
    TEST_ASSERT_EQUAL_INT(ENGINE_RESULT_NOT_IMPLEMENTED, result);
    TEST_ASSERT_TRUE(engine.has_position);
    TEST_ASSERT_TRUE(board_snapshot_equal(&engine.position, &snapshot));
}

/* The first principle in docs/functional/overview.md: a sensing fault is never
 * converted into a move, and faults never change the stored position. */
static void test_faulted_snapshot_does_not_become_the_position(void)
{
    board_snapshot_place(&snapshot, square_from_file_rank('e', 2),
                         PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 5u);
    TEST_ASSERT_EQUAL_INT(ENGINE_RESULT_NOT_IMPLEMENTED,
                          engine_apply_snapshot(&engine, &snapshot));

    board_snapshot_t faulted;
    board_snapshot_clear(&faulted);
    board_snapshot_place(&faulted, square_from_file_rank('e', 4),
                         PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 5u);
    faulted.fault.fault = BOARD_FAULT_RF_CROSSTALK;
    faulted.fault.square = square_from_file_rank('e', 4);

    TEST_ASSERT_EQUAL_INT(ENGINE_RESULT_NOT_IMPLEMENTED,
                          engine_apply_snapshot(&engine, &faulted));
    TEST_ASSERT_TRUE(board_snapshot_equal(&engine.position, &snapshot));
}

static void test_every_fault_is_refused(void)
{
    for (int fault = BOARD_FAULT_TAG_FAULT; fault < BOARD_FAULT_COUNT; fault++) {
        engine_init(&engine);
        board_snapshot_t faulted;
        board_snapshot_clear(&faulted);
        board_snapshot_place(&faulted, 0u, PIECE_COLOR_WHITE, PIECE_TYPE_KING, 1u);
        faulted.fault.fault = (board_fault_t)fault;
        (void)engine_apply_snapshot(&engine, &faulted);
        TEST_ASSERT_FALSE(engine.has_position);
    }
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_stub_reports_itself_unimplemented);
    RUN_TEST(test_init_leaves_no_position);
    RUN_TEST(test_clean_snapshot_is_recorded_but_never_accepted);
    RUN_TEST(test_faulted_snapshot_does_not_become_the_position);
    RUN_TEST(test_every_fault_is_refused);
    return UNITY_END();
}
