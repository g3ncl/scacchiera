#include "core/game.h"

#include <stdio.h>
#include <string.h>

#include "core/hw/output.h"
#include "core/hw/storage.h"

/* Display texts are terse because the band fits about seven glyphs at the
 * scale the rail uses; the renderer truncates at the right edge, so a longer
 * word would lose its ending, not its start. */

static void show_both(game_t *game, bool fault_active, const char *text)
{
    if (fault_active) {
        return;
    }
    if (strncmp(game->shown, text, sizeof(game->shown) - 1u) == 0) {
        return;
    }
    strncpy(game->shown, text, sizeof(game->shown) - 1u);
    game->shown[sizeof(game->shown) - 1u] = '\0';
    hw_output_display_text(PIECE_COLOR_WHITE, text);
    hw_output_display_text(PIECE_COLOR_BLACK, text);
}

static void show_clocks(game_t *game, bool fault_active, uint32_t now_ms)
{
    if (fault_active || !game->clock.has_time_control) {
        return;
    }
    chessclock_tick(&game->clock, now_ms);
    char white[10];
    char black[10];
    (void)chessclock_format(&game->clock, PIECE_COLOR_WHITE, white, sizeof(white));
    (void)chessclock_format(&game->clock, PIECE_COLOR_BLACK, black, sizeof(black));
    char combined[24];
    (void)snprintf(combined, sizeof(combined), "%s|%s", white, black);
    if (strncmp(game->shown, combined, sizeof(game->shown) - 1u) == 0) {
        return;
    }
    strncpy(game->shown, combined, sizeof(game->shown) - 1u);
    game->shown[sizeof(game->shown) - 1u] = '\0';
    hw_output_display_text(PIECE_COLOR_WHITE, white);
    hw_output_display_text(PIECE_COLOR_BLACK, black);
}

static void show_square(game_t *game, bool fault_active, const char *prefix,
                        square_t square)
{
    char text[24];
    if (square_is_valid(square)) {
        (void)snprintf(text, sizeof(text), "%s %c%u", prefix,
                       square_file_letter(square), (unsigned)square_rank(square));
    } else {
        (void)snprintf(text, sizeof(text), "%s", prefix);
    }
    show_both(game, fault_active, text);
}

static bool uid_on_board(const board_snapshot_t *snapshot, uint64_t uid)
{
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        if (snapshot->squares[square].state == SQUARE_STATE_OCCUPIED &&
            snapshot->squares[square].uid == uid) {
            return true;
        }
    }
    return false;
}

static square_t uid_square(const board_snapshot_t *snapshot, uint64_t uid)
{
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        if (snapshot->squares[square].state == SQUARE_STATE_OCCUPIED &&
            snapshot->squares[square].uid == uid) {
            return square;
        }
    }
    return SQUARE_INVALID;
}

/* The kings' tags, from an identity-resolved snapshot. Gesture detection is
 * UID presence afterwards, because a king in a hand is off the board wherever
 * the other pieces stand. */
static void capture_kings(game_t *game, const board_snapshot_t *snapshot,
                          uint32_t now_ms)
{
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const square_reading_t *reading = &snapshot->squares[square];
        if (reading->state == SQUARE_STATE_OCCUPIED &&
            reading->type == PIECE_TYPE_KING) {
            game->king_uid[(uint8_t)reading->color] = reading->uid;
        }
    }
    game->king_seen_ms[0] = now_ms;
    game->king_seen_ms[1] = now_ms;
    game->gesture_counting = false;
}

static void persist(game_t *game, bool fault_active)
{
    for (uint8_t side = 0u; side < 2u; side++) {
        game->record.remaining_ms[side] = game->clock.remaining_ms[side];
        game->record.increment_ms[side] = game->clock.increment_ms[side];
    }
    game->record.has_time_control = game->clock.has_time_control;
    game->record.running = game->clock.running;
    game_record_seal(&game->record);
    if (!hw_storage_save_game(&game->record)) {
        /* Persistence failing must not stop play; the cost is that a power
         * cut forgets this move. The next commit retries. */
        show_both(game, fault_active, "NOSAVE");
    }
}

static void finish(game_t *game, game_result_t result, result_reason_t reason,
                   bool fault_active)
{
    game->state = GAME_STATE_OVER;
    game->result = result;
    game->result_reason = reason;
    game->has_provisional = false;
    game->gesture_counting = false;
    if (game->clock.has_time_control) {
        chessclock_pause(&game->clock, game->clock.charged_to_ms);
    }
    /* The game is discarded when it ends; only the registry outlives it. */
    (void)hw_storage_clear_game();
    hw_output_light_cue(PIECE_COLOR_WHITE, LIGHT_CUE_RESULT);
    hw_output_light_cue(PIECE_COLOR_BLACK, LIGHT_CUE_RESULT);
    const char *text = (result == GAME_RESULT_WHITE_WINS)   ? "1-0"
                       : (result == GAME_RESULT_BLACK_WINS) ? "0-1"
                                                            : "DRAW";
    show_both(game, fault_active, text);
}

/* Repetition windows are cleared by irreversible moves: a capture, a pawn
 * move, or a lost castling right (core/repetition.h). */
static void track_repetition(game_t *game, const position_t *before,
                             const move_t *move)
{
    const bool irreversible =
        move_is_capture(move) ||
        position_piece_is(before->board[move->from], before->side_to_move,
                          PIECE_TYPE_PAWN) ||
        before->castling != game->position.castling;
    const uint64_t key = position_key(&game->position);
    if (irreversible) {
        repetition_reset(&game->ledger, key);
    } else {
        repetition_push(&game->ledger, key);
    }
}

static void commit_provisional(game_t *game, bool fault_active)
{
    const position_t before = game->position;
    game->position = game->provisional_position;
    const move_t move = game->provisional_move;
    game->has_provisional = false;

    if (game->record.ply_count < GAME_MAX_PLIES) {
        game->record.moves[game->record.ply_count] = move;
        game->record.ply_count = (uint16_t)(game->record.ply_count + 1u);
    }

    /* Credited at commitment, so a cancelled provisional needs no reversal. */
    chessclock_credit_increment(&game->clock, before.side_to_move);
    track_repetition(game, &before, &move);
    persist(game, fault_active);

    hw_output_light_cue(before.side_to_move, LIGHT_CUE_MOVE_ACCEPTED);

    result_report_t report;
    result_evaluate(&game->position, &game->ledger, &game->derive.legal, &report);
    if (report.result != GAME_RESULT_NONE) {
        finish(game, report.result, report.reason, fault_active);
        return;
    }
    if (report.hint_threefold) {
        show_both(game, fault_active, "3-FOLD");
    } else if (report.hint_fifty_move) {
        show_both(game, fault_active, "50 MOVE");
    }
}

static void begin_play(game_t *game, bool fault_active, uint32_t now_ms)
{
    game->state = GAME_STATE_PLAYING;
    position_init_standard(&game->position);
    game->has_provisional = false;
    repetition_reset(&game->ledger, position_key(&game->position));
    game_record_clear(&game->record);
    if (game->preset_selected) {
        chessclock_init_preset(&game->clock, game->selected_preset,
                               PIECE_COLOR_WHITE, now_ms);
    } else {
        chessclock_init_untimed(&game->clock);
    }
    persist(game, fault_active);
    /* An unclocked game keeps the displays dark until something needs saying;
     * a clocked one shows the clocks on the next step. */
    show_both(game, fault_active, game->clock.has_time_control ? "GO" : "");
}

static void start_check(game_t *game, const board_snapshot_t *stable,
                        bool fault_active, uint32_t now_ms)
{
    position_t standard;
    position_init_standard(&standard);
    square_t mismatch = SQUARE_INVALID;
    if (!position_matches_snapshot(&standard, stable, &mismatch)) {
        /* The exact mismatched square, never an inference (GAME-START-003). */
        show_square(game, fault_active, "SET", mismatch);
        return;
    }
    capture_kings(game, stable, now_ms);
    game->select_until_ms = now_ms + GAME_TIME_SELECT_WINDOW_MS;
    game->candidate_preset = TIME_PRESET_NONE;
    game->preset_selected = false;
    game->state = GAME_STATE_TIME_SELECT;
    show_both(game, fault_active, "TIME?");
}

/* The ten-second window: lift the white king from e1 onto d4, d5, e4 or e5,
 * hold it about three seconds, then return it to e1 to arm the preset. Raw
 * sweeps drive this because the hold is shorter than stability's agreement. */
static void time_select(game_t *game, const board_snapshot_t *raw,
                        bool fault_active, uint32_t now_ms)
{
    if ((int32_t)(now_ms - game->select_until_ms) >= 0) {
        begin_play(game, fault_active, now_ms);
        return;
    }
    if (raw == NULL) {
        return;
    }
    const square_t king_at = uid_square(raw, game->king_uid[PIECE_COLOR_WHITE]);
    const uint8_t preset = time_preset_for_square(king_at);

    if (preset != TIME_PRESET_NONE) {
        if (preset != game->candidate_preset) {
            game->candidate_preset = preset;
            game->candidate_since_ms = now_ms;
        } else if (!game->preset_selected &&
                   (uint32_t)(now_ms - game->candidate_since_ms) >=
                       GAME_PRESET_HOLD_MS) {
            game->preset_selected = true;
            game->selected_preset = preset;
            show_both(game, fault_active, TIME_PRESETS[preset].name);
        }
        /* Holding extends the window: a player mid-gesture is not idle. */
        game->select_until_ms = now_ms + GAME_TIME_SELECT_WINDOW_MS;
        return;
    }
    game->candidate_preset = TIME_PRESET_NONE;
    if (game->preset_selected &&
        king_at == square_from_file_rank('e', 1)) {
        begin_play(game, fault_active, now_ms);
    }
}

/* Resign and draw are king-absence gestures: one king out for five seconds
 * opens a fifteen-second countdown, both kings out means an agreed draw, and
 * a returned king cancels. */
static void gestures(game_t *game, const board_snapshot_t *raw, bool fault_active,
                     uint32_t now_ms)
{
    if (raw == NULL) {
        /* No clean sweep is no evidence: a gesture clock that ran while the
         * board was unreadable could resign a game nobody touched. */
        return;
    }
    for (uint8_t side = 0u; side < 2u; side++) {
        if (uid_on_board(raw, game->king_uid[side])) {
            game->king_seen_ms[side] = now_ms;
        }
    }
    const bool absent_white =
        (uint32_t)(now_ms - game->king_seen_ms[0]) >= GAME_KING_ABSENT_MS;
    const bool absent_black =
        (uint32_t)(now_ms - game->king_seen_ms[1]) >= GAME_KING_ABSENT_MS;

    if (!game->gesture_counting) {
        if (absent_white || absent_black) {
            game->gesture_counting = true;
            game->gesture_both_kings = absent_white && absent_black;
            game->gesture_side = absent_black ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE;
            game->gesture_deadline_ms = now_ms + GAME_GESTURE_COUNTDOWN_MS;
        }
        return;
    }

    /* Two kings gone is a stronger claim than one; upgrade but never
     * downgrade mid-count, because the first gesture's clock keeps running. */
    if (absent_white && absent_black) {
        game->gesture_both_kings = true;
    }
    if (!absent_white && !absent_black) {
        game->gesture_counting = false;
        show_both(game, fault_active, game->clock.has_time_control ? "GO" : "");
        return;
    }
    if ((int32_t)(now_ms - game->gesture_deadline_ms) >= 0) {
        if (game->gesture_both_kings) {
            finish(game, GAME_RESULT_DRAW, RESULT_REASON_AGREED_DRAW, fault_active);
        } else {
            finish(game,
                   (game->gesture_side == PIECE_COLOR_WHITE) ? GAME_RESULT_BLACK_WINS
                                                             : GAME_RESULT_WHITE_WINS,
                   RESULT_REASON_RESIGNATION, fault_active);
        }
        return;
    }
    const uint32_t left =
        (uint32_t)(game->gesture_deadline_ms - now_ms + 999u) / 1000u;
    char text[16];
    (void)snprintf(text, sizeof(text), "%s %u",
                   game->gesture_both_kings ? "DRW" : "RES", (unsigned)left);
    show_both(game, fault_active, text);
}

static void playing_stable(game_t *game, const board_snapshot_t *stable,
                           bool fault_active, uint32_t now_ms)
{
    if (game->resume_pending) {
        square_t mismatch = SQUARE_INVALID;
        if (position_matches_snapshot(&game->position, stable, &mismatch)) {
            game->resume_pending = false;
            capture_kings(game, stable, now_ms);
            if (game->clock.has_time_control) {
                game->clock.charged_to_ms = now_ms;
            }
            show_both(game, fault_active, "RESUME");
        } else {
            /* BOARD_MISMATCH: resynchronise (browser) or press for a new
             * game. Nothing is guessed from history. */
            show_square(game, fault_active, "RESYNC", mismatch);
        }
        return;
    }

    /* Returning to the committed position cancels the provisional move and
     * hands the clock back. Checked before deriving, because relative to the
     * provisional position the cancelled board just looks wrong. */
    if (game->has_provisional &&
        position_matches_snapshot(&game->position, stable, NULL)) {
        game->has_provisional = false;
        chessclock_switch(&game->clock, now_ms);
        return;
    }

    const position_t *base =
        game->has_provisional ? &game->provisional_position : &game->position;
    movederive_report_t report;
    movederive(&game->derive, base, stable, &report);

    switch (report.result) {
    case MOVEDERIVE_UNCHANGED:
        break;
    case MOVEDERIVE_MOVE:
        if (game->has_provisional) {
            /* A full move on top of the provisional one is the opponent
             * playing: acceptance and a new provisional in one step. */
            commit_provisional(game, fault_active);
            if (game->state != GAME_STATE_PLAYING) {
                break;
            }
        }
        game->provisional_move = report.move;
        game->provisional_position = game->position;
        position_make_move(&game->provisional_position, &report.move);
        game->has_provisional = true;
        chessclock_switch(&game->clock, now_ms);
        break;
    case MOVEDERIVE_INCOMPLETE:
        if (game->has_provisional &&
            movederive_lifted_by(&report, &game->provisional_position,
                                 game->provisional_position.side_to_move, NULL)) {
            /* The opponent touching their own piece commits the move. */
            commit_provisional(game, fault_active);
        }
        break;
    case MOVEDERIVE_PROMOTION_PENDING:
        show_both(game, fault_active, "PROM?");
        break;
    case MOVEDERIVE_ILLEGAL: {
        /* Replacing the provisional with a different legal move is allowed:
         * relative to the provisional position that board reads illegal, so
         * re-derive against the committed one before calling it wrong. */
        if (game->has_provisional) {
            movederive_report_t retry;
            movederive(&game->derive, &game->position, stable, &retry);
            if (retry.result == MOVEDERIVE_MOVE) {
                game->provisional_move = retry.move;
                game->provisional_position = game->position;
                position_make_move(&game->provisional_position, &retry.move);
                break;
            }
        }
        hw_output_light_cue(base->side_to_move, LIGHT_CUE_ILLEGAL);
        show_square(game, fault_active, "ILL", report.offender);
        break;
    }
    case MOVEDERIVE_AMBIGUOUS:
        show_square(game, fault_active, "AMBIG", report.offender);
        break;
    case MOVEDERIVE_UNREADABLE:
    default:
        break;
    }
}

static void replay_record(game_t *game)
{
    position_init_standard(&game->position);
    repetition_reset(&game->ledger, position_key(&game->position));
    for (uint16_t ply = 0u; ply < game->record.ply_count; ply++) {
        const position_t before = game->position;
        const move_t move = game->record.moves[ply];
        position_make_move(&game->position, &move);
        track_repetition(game, &before, &move);
    }
    chessclock_init_untimed(&game->clock);
    game->clock.has_time_control = game->record.has_time_control;
    game->clock.running = game->record.running;
    for (uint8_t side = 0u; side < 2u; side++) {
        game->clock.remaining_ms[side] = game->record.remaining_ms[side];
        game->clock.increment_ms[side] = game->record.increment_ms[side];
    }
}

void game_init(game_t *game)
{
    memset(game, 0, sizeof(*game));
    position_clear(&game->position);
    game_record_clear(&game->record);

    if (hw_storage_load_game(&game->record)) {
        /* A stored game resumes only against a matching physical board; the
         * comparison happens at the first stable position. */
        replay_record(game);
        game->resume_pending = true;
        game->state = GAME_STATE_PLAYING;
        return;
    }
    game_record_clear(&game->record);
    game->state = GAME_STATE_IDLE;
}

void game_step(game_t *game, const board_snapshot_t *raw_clean,
               const board_snapshot_t *stable, button_event_t button,
               bool fault_active, uint32_t now_ms)
{
    switch (game->state) {
    case GAME_STATE_IDLE:
        if (button == BUTTON_EVENT_SHORT) {
            game->state = GAME_STATE_START_CHECK;
            show_both(game, fault_active, "SETUP");
        }
        break;

    case GAME_STATE_START_CHECK:
        if (stable != NULL) {
            start_check(game, stable, fault_active, now_ms);
        }
        break;

    case GAME_STATE_TIME_SELECT:
        time_select(game, raw_clean, fault_active, now_ms);
        break;

    case GAME_STATE_PLAYING:
        if (button == BUTTON_EVENT_SHORT) {
            if (game->resume_pending) {
                /* Starting over instead of resynchronising. */
                game->resume_pending = false;
                game->state = GAME_STATE_IDLE;
                show_both(game, fault_active, "");
                break;
            }
            if (game->clock.has_time_control) {
                if (chessclock_is_paused(&game->clock)) {
                    chessclock_resume(&game->clock, now_ms);
                } else {
                    chessclock_pause(&game->clock, now_ms);
                    show_both(game, fault_active, "PAUSE");
                }
            }
        }
        if (stable != NULL) {
            playing_stable(game, stable, fault_active, now_ms);
        }
        if (game->state != GAME_STATE_PLAYING) {
            break;
        }
        if (!game->resume_pending) {
            gestures(game, raw_clean, fault_active, now_ms);
        }
        if (game->state != GAME_STATE_PLAYING) {
            break;
        }
        if (game->clock.has_time_control && !game->resume_pending) {
            chessclock_tick(&game->clock, now_ms);
            piece_color_t flagged = PIECE_COLOR_WHITE;
            if (chessclock_flagged(&game->clock, &flagged)) {
                result_reason_t reason = RESULT_REASON_NONE;
                const game_result_t result =
                    result_flag_fall(&game->position, flagged, &reason);
                finish(game, result, reason, fault_active);
                break;
            }
            if (!game->gesture_counting && !chessclock_is_paused(&game->clock)) {
                show_clocks(game, fault_active, now_ms);
            }
        }
        break;

    case GAME_STATE_OVER:
        if (button == BUTTON_EVENT_SHORT) {
            game->state = GAME_STATE_START_CHECK;
            show_both(game, fault_active, "SETUP");
        }
        break;

    default:
        break;
    }
}
