#include "core/snapshot.h"

#include <string.h>

void board_snapshot_clear(board_snapshot_t *snapshot)
{
    memset(snapshot, 0, sizeof(*snapshot));
    snapshot->fault.fault = BOARD_FAULT_NONE;
    snapshot->fault.square = SQUARE_INVALID;
}

void board_snapshot_place(board_snapshot_t *snapshot, square_t square,
                          piece_color_t color, piece_type_t type, uint64_t uid)
{
    if (!square_is_valid(square)) {
        return;
    }
    snapshot->squares[square] = (square_reading_t){
        .state = SQUARE_STATE_OCCUPIED,
        .color = color,
        .type = type,
        .uid = uid,
    };
}

bool board_snapshot_equal(const board_snapshot_t *a, const board_snapshot_t *b)
{
    for (square_t square = 0; square < BOARD_SQUARES; square++) {
        const square_reading_t *left = &a->squares[square];
        const square_reading_t *right = &b->squares[square];
        if (left->state != right->state) {
            return false;
        }
        /* Colour, type and UID are only meaningful where a tag actually read,
         * so comparing them on an empty or unreadable square would make two
         * equivalent positions differ over stale bytes. */
        if (left->state != SQUARE_STATE_OCCUPIED) {
            continue;
        }
        if (left->color != right->color || left->type != right->type ||
            left->uid != right->uid) {
            return false;
        }
    }
    return true;
}

uint8_t board_snapshot_occupied_count(const board_snapshot_t *snapshot)
{
    uint8_t count = 0;
    for (square_t square = 0; square < BOARD_SQUARES; square++) {
        if (snapshot->squares[square].state == SQUARE_STATE_OCCUPIED) {
            count++;
        }
    }
    return count;
}

bool board_snapshot_find_duplicate_uid(const board_snapshot_t *snapshot,
                                       square_t *first, square_t *second)
{
    for (square_t a = 0; a < BOARD_SQUARES; a++) {
        if (snapshot->squares[a].state != SQUARE_STATE_OCCUPIED) {
            continue;
        }
        for (square_t b = (square_t)(a + 1u); b < BOARD_SQUARES; b++) {
            if (snapshot->squares[b].state != SQUARE_STATE_OCCUPIED) {
                continue;
            }
            if (snapshot->squares[a].uid == snapshot->squares[b].uid) {
                *first = a;
                *second = b;
                return true;
            }
        }
    }
    return false;
}
