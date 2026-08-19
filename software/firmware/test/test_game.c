#include "unity.h"

#include <string.h>

#include "core/game.h"
#include "core/hw/storage.h"
#include "core/movegen.h"
#include "fake_output.h"
#include "fake_storage.h"

/* The game state machine against the gameplay spec, driven the way main/
 * drives it: identity-resolved stable positions, clean raw sweeps, button
 * events, and a clock that only ever arrives as a parameter.
 *
 * The test keeps a mirror position and a UID per square, because the game
 * tracks kings by tag rather than by geometry and a mirror is what keeps
 * those tags stable as pieces move. */

static game_t game;
static position_t mirror;
static uint64_t uids[BOARD_SQUARES];
static board_snapshot_t snap;
static move_list_t legal;
static uint32_t now;

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

static const board_snapshot_t *snapshot_without(square_t lifted)
{
    (void)snapshot_now();
    snap.squares[lifted].state = SQUARE_STATE_EMPTY;
    return &snap;
}

/* Applies a move to the mirror, moving its tag with it: captures lose the
 * victim's tag, castling carries the rook's, en passant clears the bystander. */
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

static move_t legal_move(char ff, uint8_t fr, char tf, uint8_t tr)
{
    movegen_legal(&mirror, &legal);
    for (uint8_t i = 0u; i < legal.count; i++) {
        if (legal.moves[i].from == sq(ff, fr) && legal.moves[i].to == sq(tf, tr)) {
            return legal.moves[i];
        }
    }
    TEST_FAIL_MESSAGE("expected move is not legal here");
    return move_null();
}

static void step(const board_snapshot_t *raw, const board_snapshot_t *stable,
                 button_event_t button)
{
    now += 250u;
    game_step(&game, raw, stable, button, false, now);
}

/* Button, standard position, let the ten-second window lapse: an untimed
 * game, which is the spec's default. */
static void start_untimed(void)
{
    step(NULL, NULL, BUTTON_EVENT_SHORT);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_START_CHECK, game.state);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_TIME_SELECT, game.state);
    now += GAME_TIME_SELECT_WINDOW_MS;
    step(NULL, NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, game.state);
    TEST_ASSERT_FALSE(game.clock.has_time_control);
}

/* One full committed ply: place the move, then the other player lifts one of
 * their pieces, which is the acceptance the spec defines. */
static void play_and_commit(char ff, uint8_t fr, char tf, uint8_t tr,
                            char lift_file, uint8_t lift_rank)
{
    const move_t move = legal_move(ff, fr, tf, tr);
    mirror_move(&move);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_TRUE(game.has_provisional);
    step(NULL, snapshot_without(sq(lift_file, lift_rank)), BUTTON_EVENT_NONE);
    TEST_ASSERT_FALSE(game.has_provisional);
}

void setUp(void)
{
    fake_storage_reset();
    fake_output_reset();
    position_init_standard(&mirror);
    seed_uids();
    now = 1000u;
    game_init(&game);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_IDLE, game.state);
}

void tearDown(void) {}

static void test_moves_commit_on_the_opponents_first_lift(void)
{
    start_untimed();
    play_and_commit('e', 2, 'e', 4, 'd', 7);
    TEST_ASSERT_EQUAL_UINT16(1u, game.record.ply_count);

    /* The committed move is durable: it survives into storage. */
    game_record_t stored;
    TEST_ASSERT_TRUE(hw_storage_load_game(&stored));
    TEST_ASSERT_EQUAL_UINT16(1u, stored.ply_count);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 4), stored.moves[0].to);

    play_and_commit('d', 7, 'd', 5, 'g', 1);
    TEST_ASSERT_EQUAL_UINT16(2u, game.record.ply_count);
}

static void test_returning_to_the_previous_position_cancels(void)
{
    start_untimed();
    const move_t move = legal_move('e', 2, 'e', 4);
    const position_t before = mirror;
    const uint64_t before_uids_e2 = uids[sq('e', 2)];
    mirror_move(&move);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_TRUE(game.has_provisional);

    /* Take it back. */
    mirror = before;
    uids[sq('e', 2)] = before_uids_e2;
    uids[sq('e', 4)] = 0u;
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_FALSE(game.has_provisional);
    TEST_ASSERT_EQUAL_UINT16(0u, game.record.ply_count);

    /* A different move replaces it and commits normally. */
    play_and_commit('e', 2, 'e', 3, 'd', 7);
    TEST_ASSERT_EQUAL_UINT8(sq('e', 3), game.record.moves[0].to);
}

static void test_the_opponents_own_move_commits_and_replaces(void)
{
    start_untimed();
    const move_t white = legal_move('e', 2, 'e', 4);
    mirror_move(&white);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);

    /* Black answers without a separate lift being observed: acceptance and a
     * new provisional in one stable position. */
    const move_t black = legal_move('d', 7, 'd', 5);
    mirror_move(&black);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_UINT16(1u, game.record.ply_count);
    TEST_ASSERT_TRUE(game.has_provisional);
    TEST_ASSERT_EQUAL_UINT8(sq('d', 5), game.provisional_move.to);
}

static void test_time_selection_arms_a_preset(void)
{
    step(NULL, NULL, BUTTON_EVENT_SHORT);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_TIME_SELECT, game.state);

    /* White king from e1 to e4, held past the three-second mark. */
    const uint64_t king = uids[sq('e', 1)];
    (void)snapshot_now();
    snap.squares[sq('e', 1)].state = SQUARE_STATE_EMPTY;
    board_snapshot_place(&snap, sq('e', 4), PIECE_COLOR_WHITE, PIECE_TYPE_KING, king);
    step(&snap, NULL, BUTTON_EVENT_NONE);
    now += GAME_PRESET_HOLD_MS;
    step(&snap, NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_TRUE(game.preset_selected);

    /* Back to e1 arms it: e4 is the third preset square. */
    (void)snapshot_now();
    step(&snap, NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, game.state);
    TEST_ASSERT_TRUE(game.clock.has_time_control);
    TEST_ASSERT_EQUAL_UINT32(TIME_PRESETS[2].initial_ms,
                             chessclock_remaining_ms(&game.clock, PIECE_COLOR_WHITE));
}

static void test_flag_fall_ends_a_timed_game(void)
{
    test_time_selection_arms_a_preset();
    now += TIME_PRESETS[2].initial_ms + 1000u;
    step(NULL, NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_OVER, game.state);
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_BLACK_WINS, game.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_FLAG_FALL, game.result_reason);

    /* A finished game is discarded from storage. */
    game_record_t stored;
    TEST_ASSERT_FALSE(hw_storage_load_game(&stored));
}

static void test_removing_a_king_resigns_after_the_countdown(void)
{
    start_untimed();
    const square_t e1 = sq('e', 1);
    for (uint32_t elapsed = 0u; elapsed <= GAME_KING_ABSENT_MS; elapsed += 250u) {
        step(snapshot_without(e1), NULL, BUTTON_EVENT_NONE);
    }
    TEST_ASSERT_TRUE(game.gesture_counting);
    now += GAME_GESTURE_COUNTDOWN_MS;
    step(snapshot_without(e1), NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_OVER, game.state);
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_BLACK_WINS, game.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_RESIGNATION, game.result_reason);
}

static void test_returning_the_king_cancels_the_gesture(void)
{
    start_untimed();
    const square_t e1 = sq('e', 1);
    for (uint32_t elapsed = 0u; elapsed <= GAME_KING_ABSENT_MS; elapsed += 250u) {
        step(snapshot_without(e1), NULL, BUTTON_EVENT_NONE);
    }
    TEST_ASSERT_TRUE(game.gesture_counting);
    step(snapshot_now(), NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_FALSE(game.gesture_counting);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, game.state);
}

static void test_removing_both_kings_agrees_a_draw(void)
{
    start_untimed();
    for (uint32_t elapsed = 0u; elapsed <= GAME_KING_ABSENT_MS; elapsed += 250u) {
        (void)snapshot_without(sq('e', 1));
        snap.squares[sq('e', 8)].state = SQUARE_STATE_EMPTY;
        step(&snap, NULL, BUTTON_EVENT_NONE);
    }
    now += GAME_GESTURE_COUNTDOWN_MS;
    (void)snapshot_without(sq('e', 1));
    snap.squares[sq('e', 8)].state = SQUARE_STATE_EMPTY;
    step(&snap, NULL, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_OVER, game.state);
    TEST_ASSERT_EQUAL_INT(GAME_RESULT_DRAW, game.result);
    TEST_ASSERT_EQUAL_INT(RESULT_REASON_AGREED_DRAW, game.result_reason);
}

static void test_an_illegal_position_flashes_the_offender(void)
{
    start_untimed();
    (void)snapshot_now();
    /* A pawn teleported from a2 to a5 matches no legal move. */
    const uint64_t pawn = uids[sq('a', 2)];
    snap.squares[sq('a', 2)].state = SQUARE_STATE_EMPTY;
    board_snapshot_place(&snap, sq('a', 5), PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, pawn);
    step(NULL, &snap, BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(LIGHT_CUE_ILLEGAL, fake_output_last_cue(PIECE_COLOR_WHITE));
    TEST_ASSERT_EQUAL_UINT16(0u, game.record.ply_count);
}

static void test_a_stored_game_resumes_against_a_matching_board(void)
{
    start_untimed();
    play_and_commit('e', 2, 'e', 4, 'd', 7);

    /* Restart. */
    game_t restarted;
    game_init(&restarted);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, restarted.state);
    TEST_ASSERT_TRUE(restarted.resume_pending);

    game_step(&restarted, NULL, snapshot_now(), BUTTON_EVENT_NONE, false, now);
    TEST_ASSERT_FALSE(restarted.resume_pending);
    TEST_ASSERT_EQUAL_UINT64(position_key(&mirror), position_key(&restarted.position));
}

static void test_a_mismatched_board_blocks_resume_until_a_new_game(void)
{
    start_untimed();
    play_and_commit('e', 2, 'e', 4, 'd', 7);

    game_t restarted;
    game_init(&restarted);

    /* The physical board shows the standard start, not the stored game. */
    position_init_standard(&mirror);
    seed_uids();
    game_step(&restarted, NULL, snapshot_now(), BUTTON_EVENT_NONE, false, now);
    TEST_ASSERT_TRUE(restarted.resume_pending);

    game_step(&restarted, NULL, NULL, BUTTON_EVENT_SHORT, false, now);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_IDLE, restarted.state);
}

static void test_a_failed_save_does_not_stop_play(void)
{
    start_untimed();
    const move_t move = legal_move('e', 2, 'e', 4);
    mirror_move(&move);
    step(NULL, snapshot_now(), BUTTON_EVENT_NONE);

    fake_storage_fail_writes(1u);
    step(NULL, snapshot_without(sq('d', 7)), BUTTON_EVENT_NONE);
    TEST_ASSERT_EQUAL_INT(GAME_STATE_PLAYING, game.state);
    TEST_ASSERT_EQUAL_UINT16(1u, game.record.ply_count);

    /* The next committed move persists both. */
    play_and_commit('d', 7, 'd', 5, 'g', 1);
    game_record_t stored;
    TEST_ASSERT_TRUE(hw_storage_load_game(&stored));
    TEST_ASSERT_EQUAL_UINT16(2u, stored.ply_count);
}

static void test_short_press_pauses_and_resumes_a_timed_clock(void)
{
    test_time_selection_arms_a_preset();
    step(NULL, NULL, BUTTON_EVENT_SHORT);
    TEST_ASSERT_TRUE(chessclock_is_paused(&game.clock));
    step(NULL, NULL, BUTTON_EVENT_SHORT);
    TEST_ASSERT_FALSE(chessclock_is_paused(&game.clock));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_moves_commit_on_the_opponents_first_lift);
    RUN_TEST(test_returning_to_the_previous_position_cancels);
    RUN_TEST(test_the_opponents_own_move_commits_and_replaces);
    RUN_TEST(test_time_selection_arms_a_preset);
    RUN_TEST(test_flag_fall_ends_a_timed_game);
    RUN_TEST(test_removing_a_king_resigns_after_the_countdown);
    RUN_TEST(test_returning_the_king_cancels_the_gesture);
    RUN_TEST(test_removing_both_kings_agrees_a_draw);
    RUN_TEST(test_an_illegal_position_flashes_the_offender);
    RUN_TEST(test_a_stored_game_resumes_against_a_matching_board);
    RUN_TEST(test_a_mismatched_board_blocks_resume_until_a_new_game);
    RUN_TEST(test_a_failed_save_does_not_stop_play);
    RUN_TEST(test_short_press_pauses_and_resumes_a_timed_clock);
    return UNITY_END();
}
