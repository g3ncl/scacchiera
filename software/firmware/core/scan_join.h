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
 * A line carries several tags, not one. Sixteen antennas cover sixty-four
 * squares, so each line is shared by eight of them and a starting position
 * puts eight pieces on rank 1. Anticollision returns all of them.
 *
 * The join is deliberately unforgiving. A UID that does not resolve to exactly
 * one row and exactly one column never becomes a piece, because the first
 * principle in docs/functional/overview.md is that a sensing fault is never
 * converted into a guessed position. */

/* A line covers eight squares, so it cannot legitimately hold more tags than
 * that. More than eight answering on one line is coupling from a neighbour,
 * not a fuller line. */
#define SCAN_MAX_TAGS_PER_LINE 8
#define SCAN_ROWS 8
#define SCAN_COLUMNS 8

typedef struct {
    uint8_t count;
    uint64_t uids[SCAN_MAX_TAGS_PER_LINE];
    /* Anticollision could not resolve every responder on this line: more tags
     * than slots, or a slot that stayed collided. The line is known to be
     * incomplete, which is different from being empty. */
    bool incomplete;
} line_reading_t;

void scan_join(const line_reading_t rows[SCAN_ROWS],
               const line_reading_t columns[SCAN_COLUMNS],
               board_snapshot_t *snapshot);

#endif
