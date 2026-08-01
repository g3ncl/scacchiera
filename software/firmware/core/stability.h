#ifndef CHESSBOARD_CORE_STABILITY_H
#define CHESSBOARD_CORE_STABILITY_H

#include <stdbool.h>
#include <stdint.h>

#include "core/snapshot.h"

/* Deciding when a sweep has become a position.
 *
 * A single scan is never a position. Pieces are in flight, a hand is over the
 * board, and a tag at the edge of its read range drops in and out. The
 * gameplay spec only ever acts on a *stable* position, so this is where that
 * word is given a meaning.
 *
 * Two separate jobs, deliberately not conflated:
 *
 * Agreement. A position is emitted once it has read identically several scans
 * running. Anything less is still settling.
 *
 * Instability. A square that keeps changing inside a time window is not
 * settling at all, and that is the SQUARE_UNSTABLE fault: "a square repeatedly
 * changes between present, absent, or unreadable". That is a different thing
 * from a square this sweep could not locate, which the join already reports,
 * and it can only be seen across scans. */

#define STABILITY_REQUIRED_AGREEMENTS 3

/* Changes to one square inside the window before it is called unstable. Three
 * is a piece being placed, picked up and placed again, which is ordinary. */
#define STABILITY_UNSTABLE_CHANGES 4
#define STABILITY_WINDOW_MS 2000u

typedef struct {
    board_snapshot_t previous;
    board_snapshot_t candidate;
    bool has_previous;
    bool has_candidate;
    bool emitted;
    uint8_t agreements;
    uint8_t changes[BOARD_SQUARES];
    uint32_t window_start_ms;
} stability_t;

void stability_init(stability_t *state);

/* Feeds one raw sweep. Returns true, and fills `stable`, only on the scan
 * where a new position becomes settled: a position that stays put is reported
 * once, not on every sweep. */
bool stability_update(stability_t *state, const board_snapshot_t *raw,
                      uint32_t now_ms, board_snapshot_t *stable);

/* True when some square has changed too often inside the window, with the
 * first such square. Independent of agreement, because a board can be
 * unstable in one corner and settled everywhere else. */
bool stability_unstable_square(const stability_t *state, square_t *square);

#endif
