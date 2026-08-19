#include "unity.h"

#include <string.h>

#include "core/result.h"

static position_t position;
static repetition_t ledger;
static move_list_t scratch;
static result_report_t report;

void setUp(void)
{
    position_init_standard(&position);
    repetition_reset(&ledger, position_key(&position));
    memset(&report, 0, sizeof(report));
}

void tearDown(void) {}

static void load(const char *fen)
{
    TEST_ASSERT_TRUE(position_from_fen(&position, fen));
    repetition_reset(&ledger, position_key(&position));
}

static void evaluate(void)
{
    result_evaluate(&position, &ledger, &scratch, &report);
}

static void test_the_opening_position_has_not_ended(void)
{
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_NONE, report.result);
    TEST_ASSERT_FALSE(report.hint_threefold);
    TEST_ASSERT_FALSE(report.hint_fifty_move);
}

static void test_checkmate_ends_the_game_for_the_side_that_delivered_it(void)
{
    /* Fool's mate: white is mated, so black won. */
    load("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3");
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_BLACK_WINS, report.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_CHECKMATE, report.reason);
}

static void test_stalemate_is_a_draw(void)
{
    load("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1");
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW, report.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_STALEMATE, report.reason);
}

static void test_the_decidable_dead_positions(void)
{
    load("8/8/8/4k3/8/4K3/8/8 w - - 0 1");
    TEST_ASSERT_TRUE(result_dead_position(&position));

    load("8/8/8/4k3/8/4K3/8/5B2 w - - 0 1");
    TEST_ASSERT_TRUE(result_dead_position(&position));

    load("8/8/8/4k3/8/4K3/8/5N2 w - - 0 1");
    TEST_ASSERT_TRUE(result_dead_position(&position));

    /* Bishops on the same colour of square can never meet, so no mate exists. */
    load("5b2/8/8/4k3/8/4K3/8/2B5 w - - 0 1");
    TEST_ASSERT_TRUE(result_dead_position(&position));
}

/* The pair that a single merged material test gets wrong, in opposite
 * directions. Opposite-coloured bishops can still mate; two knights cannot
 * force mate but can deliver one, so they win on time. */
static void test_the_positions_that_are_not_dead(void)
{
    load("2b5/8/8/4k3/8/4K3/8/2B5 w - - 0 1");
    TEST_ASSERT_FALSE(result_dead_position(&position));

    load("8/8/8/4k3/8/4K3/8/4NN2 w - - 0 1");
    TEST_ASSERT_FALSE(result_dead_position(&position));

    load("8/8/8/4k3/8/4K3/4P3/8 w - - 0 1");
    TEST_ASSERT_FALSE(result_dead_position(&position));
}

static void test_flag_fall_needs_a_winner_who_could_mate(void)
{
    result_reason_t reason = RESULT_REASON_NONE;

    /* Black has only a king, so white running out of time is a draw. */
    load("4k3/8/8/8/8/8/8/4K3 w - - 0 1");
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW,
                          result_flag_fall(&position, PIECE_COLOR_WHITE, &reason));
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_FLAG_FALL_INSUFFICIENT, reason);

    load("4k3/8/8/8/8/8/8/4KB2 w - - 0 1");
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW,
                          result_flag_fall(&position, PIECE_COLOR_BLACK, &reason));

    load("4k3/8/8/8/8/8/8/4KN2 w - - 0 1");
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW,
                          result_flag_fall(&position, PIECE_COLOR_BLACK, &reason));

    /* Two knights cannot force mate but can deliver one, so this is a win. */
    load("4k3/8/8/8/8/8/8/3NKN2 w - - 0 1");
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_WHITE_WINS,
                          result_flag_fall(&position, PIECE_COLOR_BLACK, &reason));
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_FLAG_FALL, reason);

    load("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1");
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_WHITE_WINS,
                          result_flag_fall(&position, PIECE_COLOR_BLACK, &reason));
}

/* Threefold is offered, fivefold ends it. Merging the two would end games
 * nobody asked to end. */
static void test_threefold_hints_and_fivefold_finishes(void)
{
    load("4k3/8/8/8/8/8/6P1/4K3 w - - 0 1");
    const uint64_t key = position_key(&position);

    repetition_push(&ledger, key);
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_NONE, report.result);
    TEST_ASSERT_FALSE(report.hint_threefold);

    repetition_push(&ledger, key);
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_NONE, report.result);
    TEST_ASSERT_TRUE(report.hint_threefold);

    repetition_push(&ledger, key);
    repetition_push(&ledger, key);
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW, report.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_FIVEFOLD, report.reason);
}

/* An irreversible move clears the window, because no earlier position can
 * ever come back. */
static void test_a_reset_window_forgets_earlier_occurrences(void)
{
    load("4k3/8/8/8/8/8/6P1/4K3 w - - 0 1");
    const uint64_t key = position_key(&position);
    repetition_push(&ledger, key);
    repetition_push(&ledger, key);
    TEST_ASSERT_EQUAL_UINT8(3u, repetition_count(&ledger, key));

    repetition_reset(&ledger, key);
    TEST_ASSERT_EQUAL_UINT8(1u, repetition_count(&ledger, key));
}

static void test_fifty_hints_and_seventy_five_finishes(void)
{
    load("4k3/8/8/8/8/8/6P1/4K3 w - - 0 1");

    position.halfmove_clock = 100u;
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_NONE, report.result);
    TEST_ASSERT_TRUE(report.hint_fifty_move);

    position.halfmove_clock = 150u;
    evaluate();
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW, report.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_SEVENTY_FIVE_MOVE, report.reason);
}

/* Mate on the last permitted ply is still mate: a game that ends both ways
 * ends the way that happened on the board. */
static void test_mate_beats_the_seventy_five_move_rule(void)
{
    load("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3");
    position.halfmove_clock = 150u;
    evaluate();
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_CHECKMATE, report.reason);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_the_opening_position_has_not_ended);
    RUN_TEST(test_checkmate_ends_the_game_for_the_side_that_delivered_it);
    RUN_TEST(test_stalemate_is_a_draw);
    RUN_TEST(test_the_decidable_dead_positions);
    RUN_TEST(test_the_positions_that_are_not_dead);
    RUN_TEST(test_flag_fall_needs_a_winner_who_could_mate);
    RUN_TEST(test_threefold_hints_and_fivefold_finishes);
    RUN_TEST(test_a_reset_window_forgets_earlier_occurrences);
    RUN_TEST(test_fifty_hints_and_seventy_five_finishes);
    RUN_TEST(test_mate_beats_the_seventy_five_move_rule);
    return UNITY_END();
}
