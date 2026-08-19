#ifndef CHESSBOARD_CORE_HW_STORAGE_H
#define CHESSBOARD_CORE_HW_STORAGE_H

#include <stdbool.h>

#include "core/game_record.h"
#include "core/registry.h"

/* What survives a power cut.
 *
 * Two things, and they have different lifetimes, which is why they are two
 * calls rather than one blob. The game is rewritten after every committed move
 * and is discarded when the game ends. The registry changes only when pieces
 * are provisioned and must outlive every game, so a board whose game record is
 * cleared still knows what its pieces are.
 *
 * V5 injects reset and write failure at every transaction boundary through
 * this interface, so each call reports success rather than assuming it. */

bool hw_storage_save_game(const game_record_t *record);
/* False when nothing is stored or what is stored does not verify. Both mean
 * the same thing to the caller: there is no game to resume. */
bool hw_storage_load_game(game_record_t *record);
bool hw_storage_clear_game(void);

bool hw_storage_save_registry(const piece_registry_t *registry);
bool hw_storage_load_registry(piece_registry_t *registry);

#endif
