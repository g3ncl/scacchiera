#include "unity.h"

#include "core/stability.h"

static stability_t state;
static board_snapshot_t raw;
static board_snapshot_t stable;
static uint32_t clock_ms;

void setUp(void)
{
    stability_init(&state);
    board_snapshot_clear(&raw);
    board_snapshot_clear(&stable);
    clock_ms = 0;
}

void tearDown(void) {}

static bool feed(const board_snapshot_t *snapshot)
{
    clock_ms += 100u;
    return stability_update(&state, snapshot, clock_ms, &stable);
}

static void place(board_snapshot_t *snapshot, const char file, uint8_t rank, uint64_t uid)
{
    board_snapshot_place(snapshot, square_from_file_rank(file, rank),
                         PIECE_COLOR_WHITE, PIECE_TYPE_NONE, uid);
}

/* A single sweep is never a position: a hand may still be over the board. */
static void test_one_scan_is_not_a_position(void)
{
    TEST_ASSERT_FALSE(feed(&raw));
}

static void test_agreement_emits_once_and_only_once(void)
{
    place(&raw, 'e', 2, 0x10u);
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_TRUE(feed(&raw));
    TEST_ASSERT_EQUAL_UINT8(1u, board_snapshot_occupied_count(&stable));

    /* Still there, but already reported. A position that stays put must not
     * re-fire every sweep. */
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_FALSE(feed(&raw));
}

static void test_a_different_scan_restarts_agreement(void)
{
    place(&raw, 'e', 2, 0x10u);
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_FALSE(feed(&raw));

    board_snapshot_t moved;
    board_snapshot_clear(&moved);
    place(&moved, 'e', 4, 0x10u);
    TEST_ASSERT_FALSE(feed(&moved));  /* new claim, count restarts */
    TEST_ASSERT_FALSE(feed(&moved));
    TEST_ASSERT_TRUE(feed(&moved));
    TEST_ASSERT_EQUAL_INT(SQUARE_STATE_OCCUPIED,
                          stable.squares[square_from_file_rank('e', 4)].state);
}

static void test_a_new_position_after_one_settles_also_emits(void)
{
    place(&raw, 'e', 2, 0x10u);
    (void)feed(&raw); (void)feed(&raw);
    TEST_ASSERT_TRUE(feed(&raw));

    board_snapshot_t moved;
    board_snapshot_clear(&moved);
    place(&moved, 'e', 4, 0x10u);
    (void)feed(&moved); (void)feed(&moved);
    TEST_ASSERT_TRUE(feed(&moved));
}

/* The first principle: a fault is never converted into a position. A faulted
 * sweep must neither confirm the candidate nor replace it. */
static void test_a_faulted_scan_never_becomes_a_position(void)
{
    place(&raw, 'e', 2, 0x10u);
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_FALSE(feed(&raw));

    board_snapshot_t faulted = raw;
    faulted.fault.fault = BOARD_FAULT_RF_CROSSTALK;
    TEST_ASSERT_FALSE(feed(&faulted));

    /* Agreement was reset, so the same good position needs the full count
     * again rather than being waved through by the faulted sweep. */
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_FALSE(feed(&raw));
    TEST_ASSERT_TRUE(feed(&raw));
}

/* SQUARE_UNSTABLE is about repetition over time, which no single sweep can
 * see. This is the case the join cannot detect. */
static void test_a_flickering_square_is_reported_unstable(void)
{
    board_snapshot_t present;
    board_snapshot_clear(&present);
    place(&present, 'd', 4, 0x77u);
    board_snapshot_t absent;
    board_snapshot_clear(&absent);

    square_t offender = SQUARE_INVALID;
    TEST_ASSERT_FALSE(stability_unstable_square(&state, &offender));

    for (int cycle = 0; cycle < 3; cycle++) {
        (void)feed(&present);
        (void)feed(&absent);
    }

    TEST_ASSERT_TRUE(stability_unstable_square(&state, &offender));
    TEST_ASSERT_EQUAL_UINT8(square_from_file_rank('d', 4), offender);
}

static void test_a_settled_board_is_never_called_unstable(void)
{
    place(&raw, 'a', 1, 0x01u);
    for (int scan = 0; scan < 20; scan++) {
        (void)feed(&raw);
    }
    TEST_ASSERT_FALSE(stability_unstable_square(&state, NULL));
}

/* An ordinary move is a change, not instability: lift, place, adjust. The
 * threshold has to sit above normal handling or every move raises a fault. */
static void test_ordinary_handling_is_not_instability(void)
{
    board_snapshot_t from;
    board_snapshot_clear(&from);
    place(&from, 'g', 1, 0x55u);
    board_snapshot_t lifted;
    board_snapshot_clear(&lifted);
    board_snapshot_t to;
    board_snapshot_clear(&to);
    place(&to, 'f', 3, 0x55u);

    (void)feed(&from);
    (void)feed(&lifted);
    (void)feed(&to);
    TEST_ASSERT_FALSE(stability_unstable_square(&state, NULL));
}

/* A quiet board earns a clean slate, or a long game would eventually mark
 * every square unstable from accumulated ordinary moves. */
static void test_the_window_forgives_old_changes(void)
{
    board_snapshot_t present;
    board_snapshot_clear(&present);
    place(&present, 'd', 4, 0x77u);
    board_snapshot_t absent;
    board_snapshot_clear(&absent);

    for (int cycle = 0; cycle < 2; cycle++) {
        (void)feed(&present);
        (void)feed(&absent);
    }
    clock_ms += STABILITY_WINDOW_MS;
    (void)feed(&present);
    TEST_ASSERT_FALSE(stability_unstable_square(&state, NULL));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_one_scan_is_not_a_position);
    RUN_TEST(test_agreement_emits_once_and_only_once);
    RUN_TEST(test_a_different_scan_restarts_agreement);
    RUN_TEST(test_a_new_position_after_one_settles_also_emits);
    RUN_TEST(test_a_faulted_scan_never_becomes_a_position);
    RUN_TEST(test_a_flickering_square_is_reported_unstable);
    RUN_TEST(test_a_settled_board_is_never_called_unstable);
    RUN_TEST(test_ordinary_handling_is_not_instability);
    RUN_TEST(test_the_window_forgives_old_changes);
    return UNITY_END();
}
