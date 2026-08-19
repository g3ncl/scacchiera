#include "core/game_record.h"

#include <stddef.h>
#include <string.h>

#include "core/crc32.h"

/* Everything up to the trailing checksum, which cannot cover itself. */
static size_t sealed_length(void)
{
    return offsetof(game_record_t, crc32);
}

void game_record_clear(game_record_t *record)
{
    memset(record, 0, sizeof(*record));
    record->magic = GAME_RECORD_MAGIC;
    record->version = (uint16_t)GAME_RECORD_VERSION;
    record->running = PIECE_COLOR_WHITE;
}

void game_record_seal(game_record_t *record)
{
    record->magic = GAME_RECORD_MAGIC;
    record->version = (uint16_t)GAME_RECORD_VERSION;
    record->crc32 = crc32_bytes((const uint8_t *)record, sealed_length());
}

bool game_record_valid(const game_record_t *record)
{
    if (record->magic != GAME_RECORD_MAGIC) {
        return false;
    }
    if (record->version != (uint16_t)GAME_RECORD_VERSION) {
        return false;
    }
    if (record->ply_count > GAME_MAX_PLIES) {
        return false;
    }
    return record->crc32 == crc32_bytes((const uint8_t *)record, sealed_length());
}
