#ifndef CHESSBOARD_CORE_GAME_RECORD_H
#define CHESSBOARD_CORE_GAME_RECORD_H

#include <stdbool.h>
#include <stdint.h>

#include "core/move.h"
#include "core/piece.h"

/* The in-progress game, as it survives a restart.
 *
 * A stored board_snapshot_t cannot do this job. It is 64 typed squares and a
 * fault, which says nothing about whose turn it is, what castling is still
 * available, which pawn may be taken en passant, or how much time each player
 * has left. Resuming from one is impossible, so the thing that is persisted is
 * the game rather than the reading.
 *
 * The position is not stored. It is rebuilt by replaying the moves from the
 * standard start, which is the same reason undo replays rather than unmakes:
 * two representations of one fact can drift apart, and one cannot. */

/* 300 moves. The longest recorded master game is 269. */
#define GAME_MAX_PLIES 600

#define GAME_RECORD_MAGIC 0x43424731u /* "CBG1" */
#define GAME_RECORD_VERSION 1u

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t ply_count;
    move_t moves[GAME_MAX_PLIES];

    uint32_t remaining_ms[2];
    uint32_t increment_ms[2];
    bool has_time_control;
    piece_color_t running;

    /* Over every byte above. NVS checks its own pages, but nothing else
     * notices a struct whose layout changed while its size did not, which is
     * exactly the failure that loads a plausible garbage board. */
    uint32_t crc32;
} game_record_t;

void game_record_clear(game_record_t *record);

/* Stamps magic, version and CRC. Call immediately before handing the record to
 * storage, so nothing can persist an unsealed one. */
void game_record_seal(game_record_t *record);

/* Checks magic, version and CRC. A rejected record is not an error to report
 * up: it is a board that must resynchronise, which is what BOARD_MISMATCH
 * means. */
bool game_record_valid(const game_record_t *record);

#endif
