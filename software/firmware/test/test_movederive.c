#include "unity.h"

#include <string.h>

#include "core/movederive.h"

static movederive_context_t context;
static position_t before;
static board_snapshot_t snapshot;
static movederive_report_t report;

static square_t sq(char file, uint8_t rank)
{
    return square_from_file_rank(file, rank);
}

/* The physical board as it would read with the position exactly set up. UIDs
 * are synthetic and deliberately arbitrary: derivation must never depend on
 * them, because two identical rooks are the same piece to chess. */
static void snapshot_from(const position_t *position, board_snapshot_t *out)
{
    board_snapshot_clear(out);
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const position_piece_t piece = position->board[square];
        if (piece != POSITION_PIECE_NONE) {
            board_snapshot_place(out, square, position_piece_color(piece),
                                 position_piece_type(piece), 0x1000u + square);
        }
    }
}

static void lift(square_t square)
{
    snapshot.squares[square].state = SQUARE_STATE_EMPTY;
    snapshot.squares[square].uid = 0u;
}

static void put(square_t square, piece_color_t color, piece_type_t type)
{
    board_snapshot_place(&snapshot, square, color, type, 0x2000u + square);
}

static void load(const char *fen)
{
    TEST_ASSERT_TRUE(position_from_fen(&before, fen));
    snapshot_from(&before, &snapshot);
}

static void derive(void)
{
    movederive(&context, &before, &snapshot, &report);
}

void setUp(void)
{
    memset(&context, 0, sizeof(context));
    position_init_standard(&before);
    snapshot_from(&before, &snapshot);
    memset(&report, 0, sizeof(report));
}

void tearDown(void) {}

static void test_an_untouched_board_is_unchanged(void)
{
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_UNCHANGED, report.result);
}

/* The rule that makes the product usable. A capture passes through this state
 * every single time, and flashing red at it would make the board unplayable. */
static void test_a_lifted_piece_is_never_an_error(void)
{
    lift(sq('e', 2));
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);
    TEST_ASSERT_EQUAL_UINT8(1u, report.lifted_count);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 2), report.lifted[0]);
}

/* Deliberately unbounded: a board being tidied should wait, not complain. */
static void test_many_lifted_pieces_are_still_only_incomplete(void)
{
    for (char file = 'a'; file <= 'h'; file++) {
        lift(sq(file, 2));
        lift(sq(file, 7));
    }
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);
}

static void test_a_quiet_move_is_derived(void)
{
    lift(sq('e', 2));
    put(sq('e', 4), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();

    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 2), report.move.from);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 4), report.move.to);
    TEST_ASSERT_NOT_EQUAL_UINT8(0u, report.move.flags & MOVE_FLAG_DOUBLE_PAWN);
}

static void test_a_capture_is_derived_however_the_hands_move(void)
{
    load("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2");

    /* Victim lifted first, which is how most people capture. */
    lift(sq('d', 5));
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);

    /* Then the capturing pawn is lifted too. */
    lift(sq('e', 4));
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);

    /* And placed. */
    put(sq('d', 5), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 4), report.move.from);
    TEST_ASSERT_EQUAL_UINT8(sq('d', 5), report.move.to);
    TEST_ASSERT_TRUE(move_is_capture(&report.move));
}

static void test_en_passant_is_derived_without_any_special_case(void)
{
    load("rnbqkbnr/pp1ppppp/8/2pP4/8/8/PPP1PPPP/RNBQKBNR w KQkq c6 0 3");

    lift(sq('d', 5));
    lift(sq('c', 5));
    put(sq('c', 6), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();

    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_NOT_EQUAL_UINT8(0u, report.move.flags & MOVE_FLAG_EN_PASSANT);
}

/* The mirror of the castle-in-progress cases: en passant also touches a
 * square that is neither from nor to, so a pawn-first hand order passes
 * through a state no completed move can produce. It must wait, not flash. */
static void test_en_passant_pawn_first_waits(void)
{
    load("rnbqkbnr/pp1ppppp/8/2pP4/8/8/PPP1PPPP/RNBQKBNR w KQkq c6 0 3");

    lift(sq('d', 5));
    put(sq('c', 6), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);

    /* Removing the captured pawn completes the move. */
    lift(sq('c', 5));
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_EQUAL_UINT8(sq('d', 5), report.move.from);
    TEST_ASSERT_EQUAL_UINT8(sq('c', 6), report.move.to);
    TEST_ASSERT_NOT_EQUAL_UINT8(0u, report.move.flags & MOVE_FLAG_EN_PASSANT);
}

/* The same hand order for black, whose victim square is on the other side of
 * the destination. */
static void test_en_passant_pawn_first_waits_for_black(void)
{
    load("rnbqkbnr/pppp1ppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 3");

    lift(sq('e', 4));
    put(sq('d', 3), PIECE_COLOR_BLACK, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);

    lift(sq('d', 4));
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_NOT_EQUAL_UINT8(0u, report.move.flags & MOVE_FLAG_EN_PASSANT);
}

static void test_a_completed_castle_is_derived(void)
{
    load("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");

    lift(sq('e', 1));
    lift(sq('h', 1));
    put(sq('g', 1), PIECE_COLOR_WHITE, PIECE_TYPE_KING);
    put(sq('f', 1), PIECE_COLOR_WHITE, PIECE_TYPE_ROOK);
    derive();

    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_NOT_EQUAL_UINT8(0u, report.move.flags & MOVE_FLAG_CASTLE_KING);
}

/* Castling moves two pieces, so the board must pass through a state that is
 * neither position. Without this the board flashes red halfway through every
 * castle. */
static void test_a_castle_in_progress_waits_king_first(void)
{
    load("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");

    lift(sq('e', 1));
    put(sq('g', 1), PIECE_COLOR_WHITE, PIECE_TYPE_KING);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);
}

/* Moving the rook first is indistinguishable from the legal move Rf1, so this
 * layer must report exactly that: the physical board shows Rf1 and nothing
 * else. The castle still works, one layer up: Rf1 becomes provisional, and
 * when the king lands on g1 the derivation against the pre-Rf1 base matches
 * O-O and replaces it, which is GAME-MOVE-004 doing its ordinary job. */
static void test_a_rook_moved_first_is_the_rook_move(void)
{
    load("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");

    lift(sq('h', 1));
    put(sq('f', 1), PIECE_COLOR_WHITE, PIECE_TYPE_ROOK);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_EQUAL_UINT8(sq('h', 1), report.move.from);
    TEST_ASSERT_EQUAL_UINT8(sq('f', 1), report.move.to);
    TEST_ASSERT_FALSE(move_is_castle(&report.move));
}

/* The rook placed with the king still in hand matches no legal move at all,
 * and that is the state the castle-in-progress rule exists for. */
static void test_a_castle_in_progress_waits_rook_first(void)
{
    load("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");

    lift(sq('h', 1));
    lift(sq('e', 1));
    put(sq('f', 1), PIECE_COLOR_WHITE, PIECE_TYPE_ROOK);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);
}

static void test_a_queenside_castle_in_progress_waits(void)
{
    load("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1");

    lift(sq('e', 8));
    put(sq('c', 8), PIECE_COLOR_BLACK, PIECE_TYPE_KING);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);
}

static void test_a_pawn_on_the_last_rank_is_not_yet_a_move(void)
{
    load("7k/4P3/8/8/8/8/8/4K3 w - - 0 1");

    lift(sq('e', 7));
    put(sq('e', 8), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();

    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_PROMOTION_PENDING, report.result);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 7), report.move.from);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 8), report.move.to);
}

static void test_the_replacement_piece_chooses_the_promotion(void)
{
    static const piece_type_t choices[4] = {PIECE_TYPE_QUEEN, PIECE_TYPE_ROOK,
                                            PIECE_TYPE_BISHOP, PIECE_TYPE_KNIGHT};
    for (uint8_t index = 0u; index < 4u; index++) {
        load("7k/4P3/8/8/8/8/8/4K3 w - - 0 1");
        lift(sq('e', 7));
        put(sq('e', 8), PIECE_COLOR_WHITE, choices[index]);
        derive();

        TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
        TEST_ASSERT_EQUAL_INT(choices[index], move_promotion(&report.move));
    }
}

/* The spec describes placing the pawn then replacing it, but a player who does
 * it in one motion has played exactly the same legal move, and refusing it
 * would flash red at a legal move. */
static void test_promotion_in_one_motion_is_accepted(void)
{
    load("7k/4P3/8/8/8/8/8/4K3 w - - 0 1");
    lift(sq('e', 7));
    put(sq('e', 8), PIECE_COLOR_WHITE, PIECE_TYPE_QUEEN);
    derive();

    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_MOVE, report.result);
    TEST_ASSERT_EQUAL_INT(PIECE_TYPE_QUEEN, move_promotion(&report.move));
}

static void test_withdrawing_the_pawn_returns_to_unchanged(void)
{
    load("7k/4P3/8/8/8/8/8/4K3 w - - 0 1");
    lift(sq('e', 7));
    put(sq('e', 8), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_PROMOTION_PENDING, report.result);

    lift(sq('e', 8));
    put(sq('e', 7), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_UNCHANGED, report.result);
}

static void test_a_wrong_colour_promotion_piece_is_illegal(void)
{
    load("7k/4P3/8/8/8/8/8/4K3 w - - 0 1");
    lift(sq('e', 7));
    put(sq('e', 8), PIECE_COLOR_BLACK, PIECE_TYPE_QUEEN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_ILLEGAL, report.result);
}

static void test_a_king_on_the_promotion_square_is_illegal(void)
{
    load("7k/4P3/8/8/8/8/8/4K3 w - - 0 1");
    lift(sq('e', 7));
    put(sq('e', 8), PIECE_COLOR_WHITE, PIECE_TYPE_KING);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_ILLEGAL, report.result);
}

static void test_moving_into_check_is_illegal_and_names_a_square(void)
{
    load("4k3/8/8/8/8/8/8/4K2r w - - 0 1");
    lift(sq('e', 1));
    put(sq('f', 1), PIECE_COLOR_WHITE, PIECE_TYPE_KING);
    derive();

    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_ILLEGAL, report.result);
    TEST_ASSERT_NOT_EQUAL_UINT8(SQUARE_INVALID, report.offender);
}

static void test_moving_the_opponents_piece_is_illegal(void)
{
    lift(sq('e', 7));
    put(sq('e', 5), PIECE_COLOR_BLACK, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_ILLEGAL, report.result);
}

static void test_a_pawn_moved_three_squares_is_illegal(void)
{
    lift(sq('e', 2));
    put(sq('e', 5), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_ILLEGAL, report.result);
}

static void test_a_piece_arriving_from_nowhere_is_illegal(void)
{
    put(sq('e', 4), PIECE_COLOR_WHITE, PIECE_TYPE_QUEEN);
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_ILLEGAL, report.result);
}

/* Two pieces of the same colour and type are interchangeable in chess, so
 * swapping them has changed nothing that a rule can see. */
static void test_swapping_two_identical_rooks_is_not_a_move(void)
{
    load("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
    const uint64_t left = snapshot.squares[sq('a', 1)].uid;
    snapshot.squares[sq('a', 1)].uid = snapshot.squares[sq('h', 1)].uid;
    snapshot.squares[sq('h', 1)].uid = left;
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_UNCHANGED, report.result);
}

/* Not knowing and knowing something wrong are different, and only one of them
 * is the player's fault. */
static void test_an_unreadable_square_is_reported_as_such(void)
{
    snapshot.squares[sq('d', 4)].state = SQUARE_STATE_UNREADABLE;
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_UNREADABLE, report.result);
    TEST_ASSERT_EQUAL_UINT8(sq('d', 4), report.offender);
}

/* The lift that commits a provisional move has to be the opponent's own piece,
 * not the mover fiddling with their own. */
static void test_a_lift_is_attributed_to_its_owner(void)
{
    lift(sq('e', 7));
    derive();
    TEST_ASSERT_EQUAL_INT(MOVEDERIVE_INCOMPLETE, report.result);

    square_t lifted = SQUARE_INVALID;
    TEST_ASSERT_TRUE(movederive_lifted_by(&report, &before, PIECE_COLOR_BLACK, &lifted));
    TEST_ASSERT_EQUAL_UINT8(sq('e', 7), lifted);
    TEST_ASSERT_FALSE(movederive_lifted_by(&report, &before, PIECE_COLOR_WHITE, &lifted));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_an_untouched_board_is_unchanged);
    RUN_TEST(test_a_lifted_piece_is_never_an_error);
    RUN_TEST(test_many_lifted_pieces_are_still_only_incomplete);
    RUN_TEST(test_a_quiet_move_is_derived);
    RUN_TEST(test_a_capture_is_derived_however_the_hands_move);
    RUN_TEST(test_en_passant_is_derived_without_any_special_case);
    RUN_TEST(test_en_passant_pawn_first_waits);
    RUN_TEST(test_en_passant_pawn_first_waits_for_black);
    RUN_TEST(test_a_completed_castle_is_derived);
    RUN_TEST(test_a_castle_in_progress_waits_king_first);
    RUN_TEST(test_a_rook_moved_first_is_the_rook_move);
    RUN_TEST(test_a_castle_in_progress_waits_rook_first);
    RUN_TEST(test_a_queenside_castle_in_progress_waits);
    RUN_TEST(test_a_pawn_on_the_last_rank_is_not_yet_a_move);
    RUN_TEST(test_the_replacement_piece_chooses_the_promotion);
    RUN_TEST(test_promotion_in_one_motion_is_accepted);
    RUN_TEST(test_withdrawing_the_pawn_returns_to_unchanged);
    RUN_TEST(test_a_wrong_colour_promotion_piece_is_illegal);
    RUN_TEST(test_a_king_on_the_promotion_square_is_illegal);
    RUN_TEST(test_moving_into_check_is_illegal_and_names_a_square);
    RUN_TEST(test_moving_the_opponents_piece_is_illegal);
    RUN_TEST(test_a_pawn_moved_three_squares_is_illegal);
    RUN_TEST(test_a_piece_arriving_from_nowhere_is_illegal);
    RUN_TEST(test_swapping_two_identical_rooks_is_not_a_move);
    RUN_TEST(test_an_unreadable_square_is_reported_as_such);
    RUN_TEST(test_a_lift_is_attributed_to_its_owner);
    return UNITY_END();
}
