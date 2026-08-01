#include "unity.h"

#include <string.h>

#include "core/scan_join.h"

static line_reading_t rows[SCAN_ROWS];
static line_reading_t columns[SCAN_COLUMNS];
static board_snapshot_t snapshot;

void setUp(void)
{
    memset(rows, 0, sizeof(rows));
    memset(columns, 0, sizeof(columns));
    board_snapshot_clear(&snapshot);
}

void tearDown(void) {}

static void see(line_reading_t *lines, uint8_t line, uint64_t uid)
{
    lines[line].uids[lines[line].count++] = uid;
}

static void test_empty_board_is_empty_and_faultless(void)
{
    scan_join(rows, columns, &snapshot);
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&snapshot));
    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
}

static void test_one_tag_lands_on_the_intersection(void)
{
    /* Row 3, column 4 is e4 on a zero-based, rank-major index. */
    see(rows, 3, 0xAABBu);
    see(columns, 4, 0xAABBu);
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(1u, board_snapshot_occupied_count(&snapshot));
    const square_t e4 = square_from_file_rank('e', 4);
    TEST_ASSERT_EQUAL_INT(SQUARE_STATE_OCCUPIED, snapshot.squares[e4].state);
    TEST_ASSERT_EQUAL_HEX64(0xAABBu, snapshot.squares[e4].uid);
}

static void test_two_tags_resolve_independently(void)
{
    see(rows, 0, 0x11u);
    see(columns, 0, 0x11u);
    see(rows, 7, 0x22u);
    see(columns, 7, 0x22u);
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(2u, board_snapshot_occupied_count(&snapshot));
    TEST_ASSERT_EQUAL_HEX64(0x11u, snapshot.squares[square_from_file_rank('a', 1)].uid);
    TEST_ASSERT_EQUAL_HEX64(0x22u, snapshot.squares[square_from_file_rank('h', 8)].uid);
}

/* The coupling case in the fault table: one tag answering on two adjacent
 * lines. Its square is not knowable, so it must not become a piece. */
static void test_a_tag_on_two_rows_is_crosstalk_and_not_a_piece(void)
{
    see(rows, 3, 0xCAFEu);
    see(rows, 4, 0xCAFEu);
    see(columns, 2, 0xCAFEu);
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_RF_CROSSTALK, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&snapshot));
}

static void test_a_tag_on_two_columns_is_crosstalk(void)
{
    see(rows, 1, 0xBEEFu);
    see(columns, 5, 0xBEEFu);
    see(columns, 6, 0xBEEFu);
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_RF_CROSSTALK, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&snapshot));
}

/* A tag heard on one axis only is on the board but unlocatable. The rule that
 * matters is that it never becomes a guessed square. */
static void test_a_row_only_tag_is_not_placed(void)
{
    see(rows, 2, 0xD00Du);
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_SQUARE_UNSTABLE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&snapshot));
}

static void test_a_column_only_tag_is_not_placed(void)
{
    see(columns, 6, 0xF00Du);
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_SQUARE_UNSTABLE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(0u, board_snapshot_occupied_count(&snapshot));
}

/* A good tag alongside a broken one still reports the fault, and the good tag
 * is still placed: one bad read does not discard the whole sweep. */
static void test_a_fault_does_not_discard_the_valid_tags(void)
{
    see(rows, 0, 0x01u);
    see(columns, 0, 0x01u);
    see(rows, 5, 0x02u);   /* row only, unlocatable */
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_SQUARE_UNSTABLE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(1u, board_snapshot_occupied_count(&snapshot));
    TEST_ASSERT_EQUAL_HEX64(0x01u, snapshot.squares[square_from_file_rank('a', 1)].uid);
}

/* Identity is provisioning's job and provisioning does not exist, so a scanned
 * square carries its UID and no piece type. Pinned so nobody later "fixes"
 * this by inventing a default piece. */
/* The case single-slot inventory could not do: eight pieces on rank 1, which
 * is every real starting position. */
static void test_a_full_rank_resolves(void)
{
    for (uint8_t file = 0; file < 8u; file++) {
        const uint64_t uid = 0x100u + file;
        see(rows, 0, uid);
        see(columns, file, uid);
    }
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(8u, board_snapshot_occupied_count(&snapshot));
    for (uint8_t file = 0; file < 8u; file++) {
        const square_t square = square_from_file_rank((char)('a' + file), 1);
        TEST_ASSERT_EQUAL_HEX64(0x100u + file, snapshot.squares[square].uid);
    }
}

/* Two full ranks facing each other, which is the other half of a starting
 * position and the case where a column carries two tags. */
static void test_two_full_ranks_resolve(void)
{
    for (uint8_t file = 0; file < 8u; file++) {
        const uint64_t white = 0x100u + file;
        const uint64_t black = 0x200u + file;
        see(rows, 0, white);
        see(rows, 7, black);
        see(columns, file, white);
        see(columns, file, black);
    }
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_NONE, snapshot.fault.fault);
    TEST_ASSERT_EQUAL_UINT8(16u, board_snapshot_occupied_count(&snapshot));
    TEST_ASSERT_EQUAL_HEX64(0x100u, snapshot.squares[square_from_file_rank('a', 1)].uid);
    TEST_ASSERT_EQUAL_HEX64(0x207u, snapshot.squares[square_from_file_rank('h', 8)].uid);
}

/* A line anticollision could not fully resolve makes the sweep untrustworthy:
 * a piece missing from it looks identical to a piece that is not there. */
static void test_an_incomplete_line_is_reported(void)
{
    see(rows, 0, 0x55u);
    see(columns, 0, 0x55u);
    rows[3].incomplete = true;
    scan_join(rows, columns, &snapshot);

    TEST_ASSERT_EQUAL_INT(BOARD_FAULT_SQUARE_UNSTABLE, snapshot.fault.fault);
    /* The resolvable tag is still placed. */
    TEST_ASSERT_EQUAL_UINT8(1u, board_snapshot_occupied_count(&snapshot));
}

static void test_identity_is_left_unknown_rather_than_guessed(void)
{
    see(rows, 0, 0x99u);
    see(columns, 0, 0x99u);
    scan_join(rows, columns, &snapshot);

    const square_t a1 = square_from_file_rank('a', 1);
    TEST_ASSERT_EQUAL_INT(PIECE_TYPE_NONE, snapshot.squares[a1].type);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_empty_board_is_empty_and_faultless);
    RUN_TEST(test_one_tag_lands_on_the_intersection);
    RUN_TEST(test_two_tags_resolve_independently);
    RUN_TEST(test_a_tag_on_two_rows_is_crosstalk_and_not_a_piece);
    RUN_TEST(test_a_tag_on_two_columns_is_crosstalk);
    RUN_TEST(test_a_row_only_tag_is_not_placed);
    RUN_TEST(test_a_column_only_tag_is_not_placed);
    RUN_TEST(test_a_fault_does_not_discard_the_valid_tags);
    RUN_TEST(test_a_full_rank_resolves);
    RUN_TEST(test_two_full_ranks_resolve);
    RUN_TEST(test_an_incomplete_line_is_reported);
    RUN_TEST(test_identity_is_left_unknown_rather_than_guessed);
    return UNITY_END();
}
