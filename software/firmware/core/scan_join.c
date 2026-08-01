#include "core/scan_join.h"

static void set_fault(board_snapshot_t *snapshot, board_fault_t fault, square_t square)
{
    /* First fault wins. Reporting the earliest keeps the message stable across
     * repeated scans of the same broken position, which matters because the
     * user is being told which square to go and look at. */
    if (snapshot->fault.fault == BOARD_FAULT_NONE) {
        snapshot->fault.fault = fault;
        snapshot->fault.square = square;
    }
}

/* Counts how many lines carry this UID, and reports the first. */
static uint8_t count_lines(const line_reading_t *lines, uint8_t line_count,
                           uint64_t uid, uint8_t *first)
{
    uint8_t seen = 0;
    for (uint8_t line = 0; line < line_count; line++) {
        if (lines[line].present && lines[line].uid == uid) {
            if (seen == 0u) {
                *first = line;
            }
            seen++;
        }
    }
    return seen;
}

void scan_join(const line_reading_t rows[SCAN_ROWS],
               const line_reading_t columns[SCAN_COLUMNS],
               board_snapshot_t *snapshot)
{
    board_snapshot_clear(snapshot);

    for (uint8_t row = 0; row < SCAN_ROWS; row++) {
        if (!rows[row].present) {
            continue;
        }
        const uint64_t uid = rows[row].uid;

        uint8_t first_row = 0;
        const uint8_t row_hits = count_lines(rows, SCAN_ROWS, uid, &first_row);
        uint8_t first_column = 0;
        const uint8_t column_hits = count_lines(columns, SCAN_COLUMNS, uid, &first_column);

        /* Only process each UID once, from its lowest row. */
        if (first_row != row) {
            continue;
        }

        if (row_hits > 1u || column_hits > 1u) {
            /* One tag answering on two lines is the coupling case the fault
             * table calls RF_CROSSTALK. The square is not knowable, so the
             * report names the row that saw it. */
            set_fault(snapshot, BOARD_FAULT_RF_CROSSTALK,
                      square_from_file_rank('a', (uint8_t)(row + 1u)));
            continue;
        }

        if (column_hits == 0u) {
            /* The tag answered on a row and on no column, so it is on the
             * board but not locatable. Never a guess: the position stays
             * unresolved and the caller retries or reports. */
            set_fault(snapshot, BOARD_FAULT_SQUARE_UNSTABLE, SQUARE_INVALID);
            continue;
        }

        const square_t square =
            (square_t)((row * SCAN_COLUMNS) + first_column);
        /* Colour and type come from the piece record, which provisioning
         * owns and which does not exist yet. Until it does, the square is
         * occupied by a known UID of unknown identity, and PIECE_TYPE_NONE
         * says so honestly rather than inventing a pawn. */
        board_snapshot_place(snapshot, square, PIECE_COLOR_WHITE, PIECE_TYPE_NONE, uid);
    }

    /* A UID seen on a column but on no row is the mirror of the case above and
     * is equally unlocatable. */
    for (uint8_t column = 0; column < SCAN_COLUMNS; column++) {
        if (!columns[column].present) {
            continue;
        }
        uint8_t unused = 0;
        if (count_lines(rows, SCAN_ROWS, columns[column].uid, &unused) == 0u) {
            set_fault(snapshot, BOARD_FAULT_SQUARE_UNSTABLE, SQUARE_INVALID);
        }
    }
}
