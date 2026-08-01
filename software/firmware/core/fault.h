#ifndef CHESSBOARD_CORE_FAULT_H
#define CHESSBOARD_CORE_FAULT_H

#include "core/square.h"

/* The fault table in docs/functional/gameplay.md. A fault never changes the
 * stored position and is never converted into a guessed legal move, so these
 * are reported alongside a snapshot rather than folded into it. */
typedef enum {
    BOARD_FAULT_NONE = 0,
    BOARD_FAULT_TAG_FAULT,
    BOARD_FAULT_UID_DUPLICATE,
    BOARD_FAULT_RF_CROSSTALK,
    BOARD_FAULT_SQUARE_UNSTABLE,
    BOARD_FAULT_BOARD_MISMATCH,
    BOARD_FAULT_COUNT,
} board_fault_t;

typedef struct {
    board_fault_t fault;
    /* The offending square, or SQUARE_INVALID where the fault is board-wide.
     * The spec requires reporting the exact square rather than a general
     * failure, so this is not optional detail. */
    square_t square;
} board_fault_report_t;

const char *board_fault_name(board_fault_t fault);

#endif
