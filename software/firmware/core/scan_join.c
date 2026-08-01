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

static bool line_has(const line_reading_t *line, uint64_t uid)
{
    for (uint8_t index = 0; index < line->count; index++) {
        if (line->uids[index] == uid) {
            return true;
        }
    }
    return false;
}

/* Counts the lines carrying this UID and reports the first. */
static uint8_t count_lines(const line_reading_t *lines, uint8_t line_count,
                           uint64_t uid, uint8_t *first)
{
    uint8_t seen = 0;
    for (uint8_t line = 0; line < line_count; line++) {
        if (line_has(&lines[line], uid)) {
            if (seen == 0u) {
                *first = line;
            }
            seen++;
        }
    }
    return seen;
}

static bool already_handled(const line_reading_t *rows, uint8_t row, uint8_t index)
{
    /* Each UID is resolved once, from its first appearance. */
    const uint64_t uid = rows[row].uids[index];
    for (uint8_t earlier = 0; earlier < index; earlier++) {
        if (rows[row].uids[earlier] == uid) {
            return true;
        }
    }
    for (uint8_t earlier_row = 0; earlier_row < row; earlier_row++) {
        if (line_has(&rows[earlier_row], uid)) {
            return true;
        }
    }
    return false;
}

void scan_join(const line_reading_t rows[SCAN_ROWS],
               const line_reading_t columns[SCAN_COLUMNS],
               board_snapshot_t *snapshot)
{
    board_snapshot_clear(snapshot);

    /* An unresolved line makes the whole sweep untrustworthy: a piece missing
     * from it is indistinguishable from a piece that is not there. Reported
     * before anything else so it is not masked by a later fault. */
    for (uint8_t row = 0; row < SCAN_ROWS; row++) {
        if (rows[row].incomplete) {
            set_fault(snapshot, BOARD_FAULT_SQUARE_UNSTABLE,
                      square_from_file_rank('a', (uint8_t)(row + 1u)));
        }
    }
    for (uint8_t column = 0; column < SCAN_COLUMNS; column++) {
        if (columns[column].incomplete) {
            set_fault(snapshot, BOARD_FAULT_SQUARE_UNSTABLE,
                      square_from_file_rank((char)('a' + column), 1));
        }
    }

    for (uint8_t row = 0; row < SCAN_ROWS; row++) {
        for (uint8_t index = 0; index < rows[row].count; index++) {
            if (already_handled(rows, row, index)) {
                continue;
            }
            const uint64_t uid = rows[row].uids[index];

            uint8_t first_row = 0;
            const uint8_t row_hits = count_lines(rows, SCAN_ROWS, uid, &first_row);
            uint8_t first_column = 0;
            const uint8_t column_hits = count_lines(columns, SCAN_COLUMNS, uid, &first_column);

            if (row_hits > 1u || column_hits > 1u) {
                /* One tag answering on two lines is the coupling case the
                 * fault table calls RF_CROSSTALK. Its square is not knowable. */
                set_fault(snapshot, BOARD_FAULT_RF_CROSSTALK,
                          square_from_file_rank('a', (uint8_t)(row + 1u)));
                continue;
            }
            if (column_hits == 0u) {
                /* Heard on a row and on no column: on the board, not
                 * locatable. Never a guess. */
                set_fault(snapshot, BOARD_FAULT_SQUARE_UNSTABLE, SQUARE_INVALID);
                continue;
            }

            const square_t square = (square_t)((row * SCAN_COLUMNS) + first_column);
            /* Colour and type come from the piece record, which provisioning
             * owns and which does not exist yet. PIECE_TYPE_NONE says the
             * identity is unknown rather than inventing a pawn. */
            board_snapshot_place(snapshot, square, PIECE_COLOR_WHITE, PIECE_TYPE_NONE, uid);
        }
    }

    /* A UID on a column but on no row is the mirror case and equally
     * unlocatable. */
    for (uint8_t column = 0; column < SCAN_COLUMNS; column++) {
        for (uint8_t index = 0; index < columns[column].count; index++) {
            uint8_t unused = 0;
            if (count_lines(rows, SCAN_ROWS, columns[column].uids[index], &unused) == 0u) {
                set_fault(snapshot, BOARD_FAULT_SQUARE_UNSTABLE, SQUARE_INVALID);
            }
        }
    }
}
