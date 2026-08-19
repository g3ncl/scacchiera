#ifndef CHESSBOARD_CORE_IDENTITY_H
#define CHESSBOARD_CORE_IDENTITY_H

#include <stdbool.h>

#include "core/registry.h"
#include "core/snapshot.h"

/* Turning UIDs into pieces.
 *
 * scan_join resolves geometry: which square a tag is on, and whether that
 * answer is trustworthy. It deliberately leaves colour and type unknown,
 * because identity is not a property of the copper and the registry lives in
 * core where the join does not reach.
 *
 * So identity is a separate pass, and it runs after stability rather than
 * inside the join. That ordering is deliberate three ways: the join keeps one
 * responsibility, port never needs the registry, and a lookup runs once per
 * settled position rather than three times per position while it settles. */

/* Resolves every occupied square through the registry, in place.
 *
 * Sets TAG_FAULT at the first square whose UID is not registered, which is the
 * "unknown code" of GAME-FAULT-002, and UID_DUPLICATE when one UID reached two
 * squares. Returns false when the snapshot carries a fault afterwards, so a
 * caller can stop without inspecting the report.
 *
 * A snapshot that already carries a fault is left exactly as it is: the first
 * fault is the one worth reporting, and overwriting it would hide the reason
 * the board is unhappy behind a consequence of it. */
bool identity_resolve(const piece_registry_t *registry, board_snapshot_t *snapshot);

#endif
