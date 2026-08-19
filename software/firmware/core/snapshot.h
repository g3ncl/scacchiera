#ifndef CHESSBOARD_CORE_SNAPSHOT_H
#define CHESSBOARD_CORE_SNAPSHOT_H

#include <stdbool.h>
#include <stdint.h>

#include "core/fault.h"
#include "core/piece.h"
#include "core/square.h"

typedef enum {
    SQUARE_STATE_EMPTY = 0,
    SQUARE_STATE_OCCUPIED,
    /* Something is there but its tag did not read. Distinct from empty
     * because the spec forbids inferring a piece from move history. */
    SQUARE_STATE_UNREADABLE,
} square_state_t;

typedef struct {
    square_state_t state;
    piece_color_t color;
    piece_type_t type;
    /* ISO 15693 UIDs are 8 bytes; see the SL2S2602 datasheet summary. */
    uint64_t uid;
} square_reading_t;

typedef struct {
    square_reading_t squares[BOARD_SQUARES];
    board_fault_report_t fault;
} board_snapshot_t;

void board_snapshot_clear(board_snapshot_t *snapshot);
void board_snapshot_place(board_snapshot_t *snapshot, square_t square,
                          piece_color_t color, piece_type_t type, uint64_t uid);
bool board_snapshot_equal(const board_snapshot_t *a, const board_snapshot_t *b);
uint8_t board_snapshot_occupied_count(const board_snapshot_t *snapshot);
/* Reports the first UID appearing on two squares, which is UID_DUPLICATE.
 * Returns false and leaves the outputs untouched when every UID is unique. */
bool board_snapshot_find_duplicate_uid(const board_snapshot_t *snapshot,
                                       square_t *first, square_t *second);

#endif
