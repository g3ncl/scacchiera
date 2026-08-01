#ifndef CHESSBOARD_CORE_SCAN_JOIN_H
#define CHESSBOARD_CORE_SCAN_JOIN_H

#include <stdbool.h>
#include <stdint.h>

#include "core/snapshot.h"

/* Turning sixteen line reads into sixty-four squares.
 *
 * The matrix reads lines, not squares: eight rows then eight columns, and a
 * piece sits where the row and the column that both saw its UID cross. This
 * join is where the ghost-piece and crosstalk faults live, so it is pure logic
 * in core/ and tested on the host rather than buried in a driver.
 *
 * It is deliberately unforgiving. A UID that does not resolve to exactly one
 * row and exactly one column never becomes a piece, because the first
 * principle in docs/functional/overview.md is that a sensing fault is never
 * converted into a guessed position. */

typedef struct {
    bool present;
    uint64_t uid;
} line_reading_t;

#define SCAN_ROWS 8
#define SCAN_COLUMNS 8

/* Fills the snapshot from one sweep. Squares with no tag are left empty, and
 * any inconsistency sets the snapshot's fault rather than being smoothed
 * over. */
void scan_join(const line_reading_t rows[SCAN_ROWS],
               const line_reading_t columns[SCAN_COLUMNS],
               board_snapshot_t *snapshot);

#endif
