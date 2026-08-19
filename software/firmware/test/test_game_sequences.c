#include "unity.h"

#include <string.h>

#include "core/game.h"
#include "core/movegen.h"
#include "fake_output.h"
#include "fake_storage.h"

/* V5's generated-sequence gate: whole games played through the same interface
 * main/ drives, one stable position at a time. Four scripted games pin the
 * behaviours random play cannot be trusted to reach (checkmate, castling,
 * promotion, en passant); a deterministic random walk then covers breadth,
 * with every commit cross-checked against an independently maintained
 * repetition ledger and result evaluation. */

#define RANDOM_GAMES 24
#define MAX_PLIES 120

static game_t game;
static position_t mirror;
static uint64_t uids[BOARD_SQUARES];
static board_snapshot_t snap;
static move_list_t legal;
static move_list_t scratch;
static repetition_t own_ledger;
static uint32_t now;
static uint64_t rng;

static uint32_t captures, castles, promotions, en_passants, checkmates, endings;

static uint64_t next_rand(void)
{
    rng ^= rng << 13;
    rng ^= rng >> 7;
    rng ^= rng << 17;
    return rng;
}

static square_t sq(char file, uint8_t rank)
{
    return square_from_file_rank(file, rank);
}

static void seed_uids(void)
{
    for (square_t s = 0u; s < BOARD_SQUARES; s++) {
        uids[s] = (mirror.board[s] != POSITION_PIECE_NONE) ? (0x1000u + s) : 0u;
    }
}

static const board_snapshot_t *snapshot_now(void)
{
    board_snapshot_clear(&snap);
    for (square_t s = 0u; s < BOARD_SQUARES; s++) {
        const position_piece_t piece = mirror.board[s];
        if (piece != POSITION_PIECE_NONE) {
            board_snapshot_place(&snap, s, position_piece_color(piece),
                                 position_piece_type(piece), uids[s]);
        }
    }
    return &snap;
}

static void mirror_move(const move_t *move)
{
    if ((move->flags & MOVE_FLAG_EN_PASSANT) != 0u) {
        const square_t victim = (mirror.side_to_move == PIECE_COLOR_WHITE)
                                    ? (square_t)(move->to - BOARD_FILES)
                                    : (square_t)(move->to + BOARD_FILES);
        uids[victim] = 0u;
    }
    if (move_is_castle(move)) {
        const square_t base = (square_t)(move->from - (move->from % BOARD_FILES));
        const bool kingside = (move->flags & MOVE_FLAG_CASTLE_KING) != 0u;
        const square_t rook_from = kingside ? (square_t)(base + 7u) : base;
        const square_t rook_to =
            kingside ? (square_t)(move->to - 1u) : (square_t)(move->to + 1u);
        uids[rook_to] = uids[rook_from];
        uids[rook_from] = 0u;
    }
    uids[move->to] = uids[move->from];
    uids[move->from] = 0u;
    position_make_move(&mirror, move);
}

static void step(const board_snapshot_t *raw, const board_snapshot_t *stable,
                 button_event_t button)
{
    now += 250u;
    game_step(&game, raw, stable, button, false, now);
}

static void begin_untimed_game(void)
{
    fake_storage_reset();
    fake_output_reset();
    position_init_standard(&mirror);
    seed_uids();
    game_init(&game);
    step(NULL, NULL, BUTTON_EVENT_SHORT);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    now += GAME_TIME_SELECT_WINDOW_MS;
    step(NULL, NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, game.state);
    repetition_reset(&own_ledger, position_key(&mirror));
}

/* The mirror-side twin of the game's own bookkeeping, so an ending is checked
 * against an independent evaluation rather than the machine's word. */
static void own_track(const position_t *before, const move_t *move)
{
    const bool irreversible =
        move_is_capture(move) ||
        position_piece_is(before->board[move->from], before->side_to_move,
                          PIECE_TYPE_PAWN) ||
        before->castling != mirror.castling;
    const uint64_t key = position_key(&mirror);
    if (irreversible) {
        repetition_reset(&own_ledger, key);
    } else {
        repetition_push(&own_ledger, key);
    }
}

static void count_flags(const move_t *move)
{
    if (move_is_capture(move)) {
        captures++;
    }
    if (move_is_castle(move)) {
        castles++;
    }
    if (move_promotion(move) != PIECE_TYPE_NONE) {
        promotions++;
    }
    if ((move->flags & MOVE_FLAG_EN_PASSANT) != 0u) {
        en_passants++;
    }
}

/* Plays one ply through the stable-position interface and commits it with an
 * opponent lift. Returns false when the commit ended the game. */
static bool play_ply(const move_t *move)
{
    const position_t before = mirror;
    mirror_move(move);
    own_track(&before, move);
    count_flags(move);

    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_TRUE_MESSAGE(game.has_provisional, "move not derived");

    /* The opponent lifts one of their pieces: pick any, the king included,
     * because one sweep is far inside the resign threshold. */
    square_t lifted = SQUARE_INVALID;
    for (square_t s = 0u; s < BOARD_SQUARES; s++) {
        const position_piece_t piece = mirror.board[s];
        if (piece != POSITION_PIECE_NONE &&
            position_piece_color(piece) == mirror.side_to_move) {
            lifted = s;
            break;
        }
    }
    (void)snapshot_now();
    snap.squares[lifted].state = SQUARE_STATE_EMPTY;
    step(NULL, &snap, BUTTON_EVENT_NONE);
    TEST_ASSERT_FALSE_MESSAGE(game.has_provisional, "move not committed");

    /* The independent verdict, against the machine's. */
    result_report_t expect;
    result_evaluate(&mirror, &own_ledger, &scratch, &expect);
    if (expect.result != GAME_RESULT_NONE) {
        endings++;
        if (expect.reason == RESULT_REASON_CHECKMATE) {
            checkmates++;
        }
        TEST_ASSERT_EQUAL_INT(GAME_STATE_OVER, game.state);
        TEST_ASSERT_EQUAL_INT(expect.result, game.result);
        TEST_ASSERT_EQUAL_INT(expect.reason, game.result_reason);
        return false;
    }
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, game.state);
    TEST_ASSERT_EQUAL_UINT64(position_key(&mirror), position_key(&game.position));
    return true;
}

static bool play_named(char ff, uint8_t fr, char tf, uint8_t tr)
{
    movegen_legal(&mirror, &legal);
    for (uint8_t i = 0u; i < legal.count; i++) {
        if (legal.moves[i].from == sq(ff, fr) && legal.moves[i].to == sq(tf, tr)) {
            return play_ply(&legal.moves[i]);
        }
    }
    TEST_FAIL_MESSAGE("scripted move is not legal here");
    return false;
}

void setUp(void)
{
    now = 1000u;
    rng = 0x9E3779B97F4A7C15ull;
}

void tearDown(void) {}

/* The fastest mate there is, end to end through the machine. */
static void test_a_scripted_checkmate_finishes_the_game(void)
{
    begin_untimed_game();
    TEST_ASSERT_TRUE(play_named('f', 2, 'f', 3));
    TEST_ASSERT_TRUE(play_named('e', 7, 'e', 5));
    TEST_ASSERT_TRUE(play_named('g', 2, 'g', 4));
    TEST_ASSERT_FALSE(play_named('d', 8, 'h', 4));
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_BLACK_WINS, game.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_CHECKMATE, game.result_reason);
    TEST_ASSERT_EQUAL_UINT32(1u, checkmates);
}

static void test_a_scripted_castle_commits(void)
{
    begin_untimed_game();
    TEST_ASSERT_TRUE(play_named('g', 1, 'f', 3));
    TEST_ASSERT_TRUE(play_named('g', 8, 'f', 6));
    TEST_ASSERT_TRUE(play_named('e', 2, 'e', 3));
    TEST_ASSERT_TRUE(play_named('e', 7, 'e', 6));
    TEST_ASSERT_TRUE(play_named('f', 1, 'e', 2));
    TEST_ASSERT_TRUE(play_named('f', 8, 'e', 7));
    TEST_ASSERT_TRUE(play_named('e', 1, 'g', 1));
    TEST_ASSERT_TRUE(castles >= 1u);
}

static void test_a_scripted_en_passant_commits(void)
{
    begin_untimed_game();
    TEST_ASSERT_TRUE(play_named('a', 2, 'a', 4));
    TEST_ASSERT_TRUE(play_named('h', 7, 'h', 6));
    TEST_ASSERT_TRUE(play_named('a', 4, 'a', 5));
    TEST_ASSERT_TRUE(play_named('b', 7, 'b', 5));
    TEST_ASSERT_TRUE(play_named('a', 5, 'b', 6));
    TEST_ASSERT_TRUE(en_passants >= 1u);
}

static void test_a_scripted_promotion_commits(void)
{
    begin_untimed_game();
    TEST_ASSERT_TRUE(play_named('a', 2, 'a', 4));
    TEST_ASSERT_TRUE(play_named('b', 7, 'b', 5));
    TEST_ASSERT_TRUE(play_named('a', 4, 'b', 5));
    TEST_ASSERT_TRUE(play_named('a', 7, 'a', 6));
    TEST_ASSERT_TRUE(play_named('b', 5, 'a', 6));
    TEST_ASSERT_TRUE(play_named('c', 8, 'b', 7));
    TEST_ASSERT_TRUE(play_named('a', 6, 'b', 7));
    TEST_ASSERT_TRUE(play_named('h', 7, 'h', 6));

    /* The promotion square holds the rook; take it and choose a queen. The
     * derivation reads the choice from the replacement tag's type. */
    movegen_legal(&mirror, &legal);
    const move_t *promo = NULL;
    for (uint8_t i = 0u; i < legal.count; i++) {
        if (legal.moves[i].from == sq('b', 7) && legal.moves[i].to == sq('a', 8) &&
            move_promotion(&legal.moves[i]) == PIECE_TYPE_QUEEN) {
            promo = &legal.moves[i];
        }
    }
    TEST_ASSERT_NOT_NULL(promo);
    TEST_ASSERT_TRUE(play_ply(promo));
    TEST_ASSERT_EQUAL_UINT32(1u, promotions);
}

/* Deterministic random games: every commit cross-checked, every ending
 * matched against the independent evaluation, and a resume round trip at the
 * cap so persistence is exercised at an arbitrary mid-game point. */
static void test_random_games_stay_consistent(void)
{
    for (uint32_t g = 0u; g < RANDOM_GAMES; g++) {
        begin_untimed_game();
        uint32_t plies = 0u;
        while (plies < MAX_PLIES) {
            movegen_legal(&mirror, &legal);
            TEST_ASSERT_GREATER_THAN_UINT8(0u, legal.count);

            /* Prefer the rare shapes when they are available, so random play
             * keeps meeting them; otherwise lean toward captures a third of
             * the time to keep games moving. */
            const move_t *choice = NULL;
            for (uint8_t i = 0u; i < legal.count; i++) {
                if ((legal.moves[i].flags & MOVE_FLAG_EN_PASSANT) != 0u ||
                    move_is_castle(&legal.moves[i]) ||
                    move_promotion(&legal.moves[i]) == PIECE_TYPE_QUEEN) {
                    choice = &legal.moves[i];
                    break;
                }
            }
            if (choice == NULL && (next_rand() % 3u) == 0u) {
                for (uint8_t i = 0u; i < legal.count; i++) {
                    if (move_is_capture(&legal.moves[i])) {
                        choice = &legal.moves[i];
                        break;
                    }
                }
            }
            if (choice == NULL) {
                choice = &legal.moves[next_rand() % legal.count];
            }

            plies++;
            if (!play_ply(choice)) {
                break;
            }
        }

        if (game.state == GAME_STATE_PLAYING) {
            /* Cap reached: the stored record must rebuild this exact game. */
            game_t resumed;
            game_init(&resumed);
            TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, resumed.state);
            TEST_ASSERT_TRUE(resumed.resume_pending);
            TEST_ASSERT_EQUAL_UINT16((uint16_t)plies, resumed.record.ply_count);
            TEST_ASSERT_EQUAL_UINT64(position_key(&mirror),
                                     position_key(&resumed.position));
        }
    }

    TEST_ASSERT_GREATER_THAN_UINT32(0u, captures);
    TEST_ASSERT_GREATER_THAN_UINT32(0u, castles);
    TEST_ASSERT_GREATER_THAN_UINT32(0u, endings);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_a_scripted_checkmate_finishes_the_game);
    RUN_TEST(test_a_scripted_castle_commits);
    RUN_TEST(test_a_scripted_en_passant_commits);
    RUN_TEST(test_a_scripted_promotion_commits);
    RUN_TEST(test_random_games_stay_consistent);
    return UNITY_END();
}
