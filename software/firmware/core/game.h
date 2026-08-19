#ifndef CHESSBOARD_CORE_GAME_H
#define CHESSBOARD_CORE_GAME_H

#include <stdbool.h>
#include <stdint.h>

#include "core/button.h"
#include "core/chessclock.h"
#include "core/game_record.h"
#include "core/movederive.h"
#include "core/position.h"
#include "core/repetition.h"
#include "core/result.h"
#include "core/snapshot.h"

/* The game state machine from docs/functional/gameplay.md: the thing the
 * engine stub stood in for. It consumes identity-resolved stable positions,
 * clean raw sweeps (for the gestures, which are faster than stability), the
 * button, and the clock; it drives the output surfaces and persistence
 * through the core/hw boundary.
 *
 * Two inputs rather than one because they answer different questions. A
 * stable position is the only thing that may change the game: moves derive
 * from it and nothing else. A raw clean sweep only ever answers "is this
 * king's tag still on the board", which drives the time-selection hold and
 * the resign and draw countdowns; those gestures are timed in seconds, and
 * waiting for stability's three agreements would stretch every one of them. */

/* The ten-second time-control window after a verified start. */
#define GAME_TIME_SELECT_WINDOW_MS 10000u
/* "Hold it for roughly three seconds." */
#define GAME_PRESET_HOLD_MS 3000u
/* "Remove one king for five seconds" starts the countdown... */
#define GAME_KING_ABSENT_MS 5000u
/* ...and the countdown itself is fifteen. Returning the king cancels. */
#define GAME_GESTURE_COUNTDOWN_MS 15000u

typedef enum {
    GAME_STATE_IDLE = 0,     /* no game; a button press starts the check */
    GAME_STATE_START_CHECK,  /* waiting for the standard starting position */
    GAME_STATE_TIME_SELECT,  /* the ten-second preset window */
    GAME_STATE_PLAYING,
    GAME_STATE_OVER,
} game_state_t;

typedef struct {
    game_state_t state;

    /* The committed position. Provisional moves live beside it, never in it,
     * so cancelling is a pointer's worth of work rather than an unmake. */
    position_t position;
    bool has_provisional;
    move_t provisional_move;
    position_t provisional_position;

    movederive_context_t derive;
    repetition_t ledger;
    chessclock_t clock;
    game_record_t record;

    /* The two kings' tags, captured from the verified start position. Gesture
     * detection is UID presence, not geometry: a king in a player's hand is
     * off the board wherever the other pieces stand. */
    uint64_t king_uid[2];

    /* Time selection. */
    uint32_t select_until_ms;
    uint8_t candidate_preset;
    uint32_t candidate_since_ms;
    bool preset_selected;
    uint8_t selected_preset;

    /* Resign and draw gestures: when each king's tag was last seen. */
    uint32_t king_seen_ms[2];
    bool gesture_counting;
    uint32_t gesture_deadline_ms;
    bool gesture_both_kings;
    piece_color_t gesture_side;

    /* Restart: a valid record was replayed and the physical board must match
     * it before play resumes (BOARD_MISMATCH otherwise). */
    bool resume_pending;

    game_result_t result;
    result_reason_t result_reason;

    /* What the displays currently show, so a state that has not changed is
     * not rewritten every step. */
    char shown[16];
} game_t;

/* Cold boot: resumes a stored game when one loads and verifies, else idles. */
void game_init(game_t *game);

/* One step of the machine. `raw_clean` is the latest fault-free sweep or NULL;
 * `stable` is a newly emitted, identity-resolved stable position or NULL (a
 * position that has not changed is reported once, so NULL is the common
 * case). `fault_active` means the caller is using the displays to show a
 * sensing fault, and the game must not paint over it. */
void game_step(game_t *game, const board_snapshot_t *raw_clean,
               const board_snapshot_t *stable, button_event_t button,
               bool fault_active, uint32_t now_ms);

#endif
