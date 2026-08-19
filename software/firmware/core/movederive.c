#include "core/movederive.h"

#include <string.h>

static void report_clear(movederive_report_t *report, movederive_result_t result)
{
    memset(report, 0, sizeof(*report));
    report->result = result;
    report->move = move_null();
    report->offender = SQUARE_INVALID;
}

/* The first square the sensing could not resolve, or SQUARE_INVALID. */
static square_t first_unreadable(const board_snapshot_t *snapshot)
{
    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        if (snapshot->squares[square].state == SQUARE_STATE_UNREADABLE) {
            return square;
        }
    }
    return SQUARE_INVALID;
}

/* Squares that held a piece and now read empty, and whether anything at all
 * appeared. Those two facts separate a board mid-move from a board that has
 * been changed into something. */
static void survey(const position_t *before, const board_snapshot_t *snapshot,
                   movederive_report_t *report, bool *has_addition)
{
    *has_addition = false;

    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const square_reading_t *reading = &snapshot->squares[square];
        const position_piece_t expected = before->board[square];

        if (reading->state == SQUARE_STATE_EMPTY) {
            if (expected != POSITION_PIECE_NONE) {
                if (report->lifted_count < MOVEDERIVE_MAX_LIFTED) {
                    report->lifted[report->lifted_count] = square;
                }
                report->lifted_count++;
            }
            continue;
        }
        if (reading->state != SQUARE_STATE_OCCUPIED) {
            continue;
        }
        if (!position_piece_is(expected, reading->color, reading->type)) {
            *has_addition = true;
        }
    }
}

static bool snapshot_equals(const position_t *position, const board_snapshot_t *snapshot)
{
    return position_snapshot_diff(position, snapshot, NULL, 0u) == 0u;
}

/* The board as it would look if this move had been played. */
static void apply(const position_t *before, const move_t *move, position_t *out)
{
    *out = *before;
    position_make_move(out, move);
}

/* The board as it looks between placing the pawn on the last rank and
 * replacing it, which GAME-PROMOTION-002 requires to be neither a completed
 * move nor a fault. */
static void apply_promotion_pending(const position_t *before, const move_t *move,
                                    position_t *out)
{
    move_t as_pawn = *move;
    as_pawn.promotion = (uint8_t)PIECE_TYPE_NONE;
    apply(before, &as_pawn, out);
}

/* Castling moves two pieces, so the board necessarily passes through a state
 * that is neither the position before nor the position after. Only the four
 * squares the castle touches may be in either state, and only for a castle
 * that is actually legal right now; everything else on the board must be
 * settled. That is what keeps this from being a wildcard. */
static bool is_castle_in_progress(const position_t *before, const move_t *move,
                                  const position_t *after,
                                  const board_snapshot_t *snapshot)
{
    const square_t rank_base = (square_t)(move->from - (move->from % BOARD_FILES));
    const bool kingside = (move->flags & MOVE_FLAG_CASTLE_KING) != 0u;
    const square_t touched[4] = {
        move->from,
        move->to,
        kingside ? (square_t)(rank_base + 7u) : rank_base,
        kingside ? (square_t)(move->to - 1u) : (square_t)(move->to + 1u),
    };

    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        bool is_touched = false;
        for (uint8_t index = 0u; index < 4u; index++) {
            if (touched[index] == square) {
                is_touched = true;
                break;
            }
        }

        const square_reading_t *reading = &snapshot->squares[square];
        const position_piece_t was = before->board[square];
        const position_piece_t will_be = after->board[square];

        bool matches_before;
        bool matches_after;
        if (reading->state == SQUARE_STATE_EMPTY) {
            matches_before = (was == POSITION_PIECE_NONE);
            matches_after = (will_be == POSITION_PIECE_NONE);
        } else if (reading->state == SQUARE_STATE_OCCUPIED) {
            matches_before = position_piece_is(was, reading->color, reading->type);
            matches_after = position_piece_is(will_be, reading->color, reading->type);
        } else {
            return false;
        }

        if (is_touched) {
            /* A touched square may also be empty while the piece is in the
             * player's hand, which is neither of the two settled states. */
            if (!matches_before && !matches_after &&
                reading->state != SQUARE_STATE_EMPTY) {
                return false;
            }
        } else if (!matches_before || !matches_after) {
            return false;
        }
    }
    return true;
}

/* En passant also moves two pieces: the captured pawn stands beside the
 * destination, not under it. Played pawn-first, the board shows the mover
 * already on the target square while the victim still stands, a state no
 * completed legal move can produce. Only the victim square may lag behind at
 * its before state; everything else must already match the position after
 * the move, which is what keeps this from being a wildcard. */
static bool is_en_passant_in_progress(const position_t *before, const move_t *move,
                                      const position_t *after,
                                      const board_snapshot_t *snapshot)
{
    const piece_color_t mover = before->side_to_move;
    const square_t victim = (mover == PIECE_COLOR_WHITE)
                                ? (square_t)(move->to - BOARD_FILES)
                                : (square_t)(move->to + BOARD_FILES);

    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const square_reading_t *reading = &snapshot->squares[square];
        const position_piece_t expected =
            (square == victim) ? before->board[square] : after->board[square];

        bool matches;
        if (reading->state == SQUARE_STATE_EMPTY) {
            matches = (expected == POSITION_PIECE_NONE);
        } else if (reading->state == SQUARE_STATE_OCCUPIED) {
            matches = position_piece_is(expected, reading->color, reading->type);
        } else {
            return false;
        }
        if (!matches) {
            return false;
        }
    }
    return true;
}

void movederive(movederive_context_t *context, const position_t *before,
                const board_snapshot_t *snapshot, movederive_report_t *report)
{
    report_clear(report, MOVEDERIVE_ILLEGAL);

    const square_t unreadable = first_unreadable(snapshot);
    if (unreadable != SQUARE_INVALID) {
        report->result = MOVEDERIVE_UNREADABLE;
        report->offender = unreadable;
        return;
    }

    if (snapshot_equals(before, snapshot)) {
        report->result = MOVEDERIVE_UNCHANGED;
        return;
    }

    bool has_addition = false;
    survey(before, snapshot, report, &has_addition);

    /* Nothing has arrived anywhere, so whatever is happening is still
     * happening. Deliberately unbounded: a board being tidied should wait
     * rather than flash red, and no move can be derived from a board with
     * pieces missing in any case. */
    if (!has_addition) {
        report->result = MOVEDERIVE_INCOMPLETE;
        return;
    }

    movegen_legal(before, &context->legal);

    uint8_t matches = 0u;
    for (uint8_t index = 0u; index < context->legal.count; index++) {
        apply(before, &context->legal.moves[index], &context->scratch);
        if (!snapshot_equals(&context->scratch, snapshot)) {
            continue;
        }
        matches++;
        if (matches == 1u) {
            report->result = MOVEDERIVE_MOVE;
            report->move = context->legal.moves[index];
        } else {
            report->result = MOVEDERIVE_AMBIGUOUS;
            report->offender = context->legal.moves[index].to;
            return;
        }
    }
    if (matches == 1u) {
        return;
    }

    /* A pawn sitting on the last rank matches the pawn-shaped variant of every
     * promotion move from that square, so the first one names the squares. */
    for (uint8_t index = 0u; index < context->legal.count; index++) {
        const move_t *candidate = &context->legal.moves[index];
        if (move_promotion(candidate) == PIECE_TYPE_NONE) {
            continue;
        }
        apply_promotion_pending(before, candidate, &context->scratch);
        if (snapshot_equals(&context->scratch, snapshot)) {
            report->result = MOVEDERIVE_PROMOTION_PENDING;
            report->move = move_make(candidate->from, candidate->to, PIECE_TYPE_NONE,
                                     candidate->flags);
            return;
        }
    }

    for (uint8_t index = 0u; index < context->legal.count; index++) {
        const move_t *candidate = &context->legal.moves[index];
        if (!move_is_castle(candidate)) {
            continue;
        }
        apply(before, candidate, &context->scratch);
        if (is_castle_in_progress(before, candidate, &context->scratch, snapshot)) {
            report->result = MOVEDERIVE_INCOMPLETE;
            return;
        }
    }

    for (uint8_t index = 0u; index < context->legal.count; index++) {
        const move_t *candidate = &context->legal.moves[index];
        if ((candidate->flags & MOVE_FLAG_EN_PASSANT) == 0u) {
            continue;
        }
        apply(before, candidate, &context->scratch);
        if (is_en_passant_in_progress(before, candidate, &context->scratch, snapshot)) {
            report->result = MOVEDERIVE_INCOMPLETE;
            return;
        }
    }

    report->result = MOVEDERIVE_ILLEGAL;
    /* Name the first square that disagrees, which is the one to point a player
     * at even when several are wrong. */
    square_t offender = SQUARE_INVALID;
    (void)position_snapshot_diff(before, snapshot, &offender, 1u);
    report->offender = offender;
}

bool movederive_lifted_by(const movederive_report_t *report, const position_t *before,
                          piece_color_t color, square_t *square)
{
    const uint8_t recorded =
        (uint8_t)((report->lifted_count < MOVEDERIVE_MAX_LIFTED) ? report->lifted_count
                                                                 : MOVEDERIVE_MAX_LIFTED);
    for (uint8_t index = 0u; index < recorded; index++) {
        const square_t candidate = report->lifted[index];
        const position_piece_t piece = before->board[candidate];
        if (piece != POSITION_PIECE_NONE && position_piece_color(piece) == color) {
            if (square != NULL) {
                *square = candidate;
            }
            return true;
        }
    }
    return false;
}
