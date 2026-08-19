#include "unity.h"

#include <string.h>

#include "core/identity.h"

static piece_registry_t registry;
static board_snapshot_t snapshot;

void setUp(void)
{
    registry_init(&registry);
    board_snapshot_clear(&snapshot);
}

void tearDown(void) {}

static square_t sq(char file, uint8_t rank)
{
    return square_from_file_rank(file, rank);
}

/* What scan_join produces: a UID at a square, with identity left unknown
 * rather than guessed. */
static void sensed(square_t square, uint64_t uid)
{
    board_snapshot_place(&snapshot, square, PIECE_COLOR_WHITE, PIECE_TYPE_NONE, uid);
}

static void test_a_registered_tag_becomes_its_piece(void)
{
    TEST_ASSERT_TRUE(registry_add(&registry, 0xA1u, PIECE_COLOR_BLACK, PIECE_TYPE_QUEEN, 0u));
    sensed(sq('d', 8), 0xA1u);

    TEST_ASSERT_TRUE(identity_resolve(&registry, &snapshot));
    TEST_ASSERT_EQUAL_INT(PIECE_COLOR_BLACK, snapshot.squares[sq('d', 8)].color);
    TEST_ASSERT_EQUAL_INT(PIECE_TYPE_QUEEN, snapshot.squares[sq('d', 8)].type);
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
}

/* An unprovisioned or foreign tag is the "unknown code" of GAME-FAULT-002, and
 * it has to name the square so the recovery text can indicate a piece. */
static void test_an_unknown_tag_is_a_tag_fault_at_its_square(void)
{
    sensed(sq('e', 4), 0xDEADu);

    TEST_ASSERT_FALSE(identity_resolve(&registry, &snapshot));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_TAG_FAULT, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 4), snapshot.fault.square);
}

/* Two squares carrying one UID is a cloned tag, which the join cannot see
 * because each square resolved to exactly one row and one column. */
static void test_one_uid_in_two_places_is_a_duplicate(void)
{
    TEST_ASSERT_TRUE(registry_add(&registry, 0xB2u, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK, 0u));
    sensed(sq('a', 1), 0xB2u);
    sensed(sq('h', 1), 0xB2u);

    TEST_ASSERT_FALSE(identity_resolve(&registry, &snapshot));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_UID_DUPLICATE, snapshot.fault.fault);
}

/* The first fault is the one worth reporting. Overwriting it would hide the
 * reason the board is unhappy behind a consequence of it. */
static void test_an_existing_fault_is_left_alone(void)
{
    snapshot.fault.fault = BOARD_FAULT_RF_CROSSTALK;
    snapshot.fault.square = sq('c', 3);
    sensed(sq('e', 4), 0xDEADu);

    TEST_ASSERT_FALSE(identity_resolve(&registry, &snapshot));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_RF_CROSSTALK, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(sq('c', 3), snapshot.fault.square);
}

static void test_an_empty_board_resolves_cleanly(void)
{
    TEST_ASSERT_TRUE(identity_resolve(&registry, &snapshot));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
}

static void test_a_whole_starting_row_resolves(void)
{
    for (uint8_t file = 0u; file < 8u; file++) {
        TEST_ASSERT_TRUE(registry_add(&registry, 0x200u + file, PIECE_COLOR_WHITE,
                                      PIECE_TYPE_PAWN, file));
        sensed(square_from_file_rank((char)('a' + file), 2), 0x200u + file);
    }
    TEST_ASSERT_TRUE(identity_resolve(&registry, &snapshot));
    for (uint8_t file = 0u; file < 8u; file++) {
        const square_t square = square_from_file_rank((char)('a' + file), 2);
        TEST_ASSERT_EQUAL_INT(PIECE_TYPE_PAWN, snapshot.squares[square].type);
    }
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_a_registered_tag_becomes_its_piece);
    RUN_TEST(test_an_unknown_tag_is_a_tag_fault_at_its_square);
    RUN_TEST(test_one_uid_in_two_places_is_a_duplicate);
    RUN_TEST(test_an_existing_fault_is_left_alone);
    RUN_TEST(test_an_empty_board_resolves_cleanly);
    RUN_TEST(test_a_whole_starting_row_resolves);
    return UNITY_END();
}
