#ifndef CHESSBOARD_CORE_REGISTRY_H
#define CHESSBOARD_CORE_REGISTRY_H

#include <stdbool.h>
#include <stdint.h>

#include "core/piece.h"

/* Which physical tag is which piece.
 *
 * A scan performs an ISO 15693 inventory, which returns UIDs and nothing else,
 * so identity at scan time can only come from a table. That is this.
 *
 * The four-byte record written into the tag answers a different question and
 * both are needed. The registry says "this UID is the white king"; the record
 * makes the piece self-describing, so a board whose registry is lost can
 * rebuild it, and reading it back after a write is what proves the tag was
 * actually programmed rather than merely addressed. */

/* Thirty-two standard pieces plus spare promotion pieces. The spare count is a
 * product decision rather than a rule, so it lives here as one number. */
#define PIECE_REGISTRY_MAX 48

/* Exactly one ISO 15693 block. */
#define PIECE_RECORD_BYTES 4
#define PIECE_RECORD_VERSION 1u

#define PIECE_REGISTRY_MAGIC 0x43425031u /* "CBP1" */
#define PIECE_REGISTRY_VERSION 1u

typedef struct {
    uint64_t uid;
    piece_color_t color;
    piece_type_t type;
    /* Distinguishes the two rooks, and a spare queen from the original. */
    uint8_t index;
} piece_entry_t;

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint8_t count;
    piece_entry_t entries[PIECE_REGISTRY_MAX];

    /* Over every byte above, exactly as game_record_t and for a stronger
     * reason: the registry outlives every game, so it is the blob most likely
     * to be read back by a firmware whose struct layout has moved while its
     * size has not. */
    uint32_t crc32;
} piece_registry_t;

void registry_init(piece_registry_t *registry);

/* Stamps magic, version and CRC. Call immediately before handing the registry
 * to storage, so nothing can persist an unsealed one. */
void registry_seal(piece_registry_t *registry);

/* Checks magic, version, count and CRC. A rejected registry is treated as no
 * registry at all: re-provisioning is recoverable, trusting garbage
 * identities is not. */
bool registry_valid(const piece_registry_t *registry);

/* False when the registry is full, or when the UID is already present under a
 * different identity: a tag is one piece, and silently rewriting which one
 * would make a board that reads differently after provisioning than before. */
bool registry_add(piece_registry_t *registry, uint64_t uid, piece_color_t color,
                  piece_type_t type, uint8_t index);

bool registry_lookup(const piece_registry_t *registry, uint64_t uid,
                     piece_color_t *color, piece_type_t *type);
bool registry_remove(piece_registry_t *registry, uint64_t uid);
bool registry_contains(const piece_registry_t *registry, uint64_t uid);

/* The bytes written to block 0: version, code, index, and a CRC over the first
 * three. A wrong version, an unknown code or a failed CRC is the TAG_FAULT of
 * GAME-FAULT-002, which is why decode reports failure rather than guessing. */
void registry_record_encode(piece_color_t color, piece_type_t type, uint8_t index,
                            uint8_t out[PIECE_RECORD_BYTES]);
bool registry_record_decode(const uint8_t record[PIECE_RECORD_BYTES],
                            piece_color_t *color, piece_type_t *type, uint8_t *index);

#endif
