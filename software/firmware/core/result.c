#include "core/result.h"

#include <string.h>

/* 150 plies is 75 full moves by each player. */
#define SEVENTY_FIVE_MOVE_PLIES 150
#define FIFTY_MOVE_PLIES 100

typedef struct {
    uint8_t pawns;
    uint8_t knights;
    uint8_t bishops;
    uint8_t rooks;
    uint8_t queens;
    /* True when at least one bishop stands on a light square, and likewise for
     * dark. Both can be true, which is already enough material to mate. */
    bool light_bishop;
    bool dark_bishop;
} material_t;

/* a1 is dark, and the colour alternates with file plus rank. */
static bool square_is_light(square_t square)
{
    const uint8_t file = (uint8_t)(square % BOARD_FILES);
    const uint8_t rank = (uint8_t)(square / BOARD_FILES);
    return ((file + rank) % 2) != 0;
}

static void count_material(const position_t *position, piece_color_t color,
                           material_t *material)
{
    memset(material, 0, sizeof(*material));

    for (square_t square = 0u; square < BOARD_SQUARES; square++) {
        const position_piece_t piece = position->board[square];
        if (piece == POSITION_PIECE_NONE || position_piece_color(piece) != color) {
            continue;
        }
        switch (position_piece_type(piece)) {
        case PIECE_TYPE_PAWN:
            material->pawns++;
            break;
        case PIECE_TYPE_KNIGHT:
            material->knights++;
            break;
        case PIECE_TYPE_BISHOP:
            material->bishops++;
            if (square_is_light(square)) {
                material->light_bishop = true;
            } else {
                material->dark_bishop = true;
            }
            break;
        case PIECE_TYPE_ROOK:
            material->rooks++;
            break;
        case PIECE_TYPE_QUEEN:
            material->queens++;
            break;
        case PIECE_TYPE_KING:
        case PIECE_TYPE_NONE:
        default:
            break;
        }
    }
}

static bool is_lone_king(const material_t *material)
{
    return material->pawns == 0u && material->knights == 0u && material->bishops == 0u &&
           material->rooks == 0u && material->queens == 0u;
}

static bool is_king_and_one_minor(const material_t *material)
{
    return material->pawns == 0u && material->rooks == 0u && material->queens == 0u &&
           ((material->knights + material->bishops) == 1);
}

bool result_can_mate(const position_t *position, piece_color_t side)
{
    material_t material;
    count_material(position, side, &material);

    if (material.pawns > 0u || material.rooks > 0u || material.queens > 0u) {
        return true;
    }
    /* Two minors can mate, even if only with help. One cannot, ever. */
    return (material.knights + material.bishops) >= 2;
}

bool result_dead_position(const position_t *position)
{
    material_t white;
    material_t black;
    count_material(position, PIECE_COLOR_WHITE, &white);
    count_material(position, PIECE_COLOR_BLACK, &black);

    if (is_lone_king(&white) && is_lone_king(&black)) {
        return true;
    }
    if (is_lone_king(&white) && is_king_and_one_minor(&black)) {
        return true;
    }
    if (is_lone_king(&black) && is_king_and_one_minor(&white)) {
        return true;
    }

    /* One bishop each, both on the same colour of square, so neither can ever
     * attack the other's squares and no mate exists. */
    const bool single_bishop_each =
        white.pawns == 0u && white.knights == 0u && white.rooks == 0u &&
        white.queens == 0u && white.bishops == 1u && black.pawns == 0u &&
        black.knights == 0u && black.rooks == 0u && black.queens == 0u &&
        black.bishops == 1u;
    if (single_bishop_each) {
        return (white.light_bishop == black.light_bishop);
    }
    return false;
}

game_result_t result_flag_fall(const position_t *position, piece_color_t flagged,
                               result_reason_t *reason)
{
    const piece_color_t winner =
        (flagged == PIECE_COLOR_WHITE) ? PIECE_COLOR_BLACK : PIECE_COLOR_WHITE;

    if (!result_can_mate(position, winner)) {
        if (reason != NULL) {
            *reason = RESULT_REASON_FLAG_FALL_INSUFFICIENT;
        }
        return GAME_RESULT_DRAW;
    }
    if (reason != NULL) {
        *reason = RESULT_REASON_FLAG_FALL;
    }
    return (winner == PIECE_COLOR_WHITE) ? GAME_RESULT_WHITE_WINS : GAME_RESULT_BLACK_WINS;
}

void result_evaluate(const position_t *position, const repetition_t *ledger,
                     move_list_t *scratch, result_report_t *report)
{
    memset(report, 0, sizeof(*report));

    if (!movegen_has_legal_move(position, scratch)) {
        if (movegen_in_check(position, position->side_to_move)) {
            report->reason = RESULT_REASON_CHECKMATE;
            /* The side to move is the one mated, so the other one won. */
            report->result = (position->side_to_move == PIECE_COLOR_WHITE)
                                 ? GAME_RESULT_BLACK_WINS
                                 : GAME_RESULT_WHITE_WINS;
        } else {
            report->reason = RESULT_REASON_STALEMATE;
            report->result = GAME_RESULT_DRAW;
        }
        return;
    }

    if (result_dead_position(position)) {
        report->result = GAME_RESULT_DRAW;
        report->reason = RESULT_REASON_DEAD_POSITION;
        return;
    }

    const uint8_t occurrences = repetition_count(ledger, position_key(position));
    if (occurrences >= 5) {
        report->result = GAME_RESULT_DRAW;
        report->reason = RESULT_REASON_FIVEFOLD;
        return;
    }
    if (position->halfmove_clock >= SEVENTY_FIVE_MOVE_PLIES) {
        report->result = GAME_RESULT_DRAW;
        report->reason = RESULT_REASON_SEVENTY_FIVE_MOVE;
        return;
    }

    /* Nothing has ended. What is left is what a player may claim. */
    report->hint_threefold = (occurrences >= 3);
    report->hint_fifty_move = (position->halfmove_clock >= FIFTY_MOVE_PLIES);
}
