#include "core/registry.h"

#include <stddef.h>
#include <string.h>

#include "core/crc32.h"

#define RECORD_COLOR_SHIFT 4
#define RECORD_TYPE_MASK 0x0Fu

/* Everything up to the trailing checksum, which cannot cover itself. */
static size_t sealed_length(void)
{
    return offsetof(piece_registry_t, crc32);
}

/* A count above the array is a corrupt or reinterpreted blob, and it must
 * never become a loop bound: entries beyond the array do not exist. */
static uint8_t bounded_count(const piece_registry_t *registry)
{
    return (registry->count <= PIECE_REGISTRY_MAX) ? registry->count
                                                   : (uint8_t)PIECE_REGISTRY_MAX;
}

void registry_init(piece_registry_t *registry)
{
    memset(registry, 0, sizeof(*registry));
    registry->magic = PIECE_REGISTRY_MAGIC;
    registry->version = (uint16_t)PIECE_REGISTRY_VERSION;
}

void registry_seal(piece_registry_t *registry)
{
    registry->magic = PIECE_REGISTRY_MAGIC;
    registry->version = (uint16_t)PIECE_REGISTRY_VERSION;
    registry->crc32 = crc32_bytes((const uint8_t *)registry, sealed_length());
}

bool registry_valid(const piece_registry_t *registry)
{
    if (registry->magic != PIECE_REGISTRY_MAGIC) {
        return false;
    }
    if (registry->version != (uint16_t)PIECE_REGISTRY_VERSION) {
        return false;
    }
    if (registry->count > PIECE_REGISTRY_MAX) {
        return false;
    }
    return registry->crc32 == crc32_bytes((const uint8_t *)registry, sealed_length());
}

static piece_entry_t *find(piece_registry_t *registry, uint64_t uid)
{
    const uint8_t count = bounded_count(registry);
    for (uint8_t index = 0u; index < count; index++) {
        if (registry->entries[index].uid == uid) {
            return &registry->entries[index];
        }
    }
    return NULL;
}

bool registry_add(piece_registry_t *registry, uint64_t uid, piece_color_t color,
                  piece_type_t type, uint8_t index)
{
    if (type == PIECE_TYPE_NONE) {
        return false;
    }
    piece_entry_t *existing = find(registry, uid);
    if (existing != NULL) {
        /* Re-registering the same tag as the same piece is what a repeated
         * provisioning pass does, and it is harmless. Re-registering it as a
         * different piece is not, because the board would read differently
         * before and after with nothing to show for it. */
        return existing->color == color && existing->type == type &&
               existing->index == index;
    }
    if (registry->count >= PIECE_REGISTRY_MAX) {
        return false;
    }
    registry->entries[registry->count].uid = uid;
    registry->entries[registry->count].color = color;
    registry->entries[registry->count].type = type;
    registry->entries[registry->count].index = index;
    registry->count++;
    return true;
}

bool registry_lookup(const piece_registry_t *registry, uint64_t uid,
                     piece_color_t *color, piece_type_t *type)
{
    const uint8_t count = bounded_count(registry);
    for (uint8_t index = 0u; index < count; index++) {
        if (registry->entries[index].uid != uid) {
            continue;
        }
        if (color != NULL) {
            *color = registry->entries[index].color;
        }
        if (type != NULL) {
            *type = registry->entries[index].type;
        }
        return true;
    }
    return false;
}

bool registry_contains(const piece_registry_t *registry, uint64_t uid)
{
    return registry_lookup(registry, uid, NULL, NULL);
}

bool registry_remove(piece_registry_t *registry, uint64_t uid)
{
    const uint8_t count = bounded_count(registry);
    for (uint8_t index = 0u; index < count; index++) {
        if (registry->entries[index].uid != uid) {
            continue;
        }
        registry->entries[index] = registry->entries[count - 1u];
        registry->count = (uint8_t)(count - 1u);
        return true;
    }
    return false;
}

/* CRC-8 with polynomial 0x07. Small, and it only has to catch a half-written
 * block or a tag from another product, not an adversary. */
static uint8_t crc8(const uint8_t *data, uint8_t length)
{
    uint8_t crc = 0x00u;
    for (uint8_t index = 0u; index < length; index++) {
        crc = (uint8_t)(crc ^ data[index]);
        for (uint8_t bit = 0u; bit < 8u; bit++) {
            if ((crc & 0x80u) != 0u) {
                crc = (uint8_t)(((uint8_t)(crc << 1)) ^ 0x07u);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}

void registry_record_encode(piece_color_t color, piece_type_t type, uint8_t index,
                            uint8_t out[PIECE_RECORD_BYTES])
{
    out[0] = (uint8_t)PIECE_RECORD_VERSION;
    out[1] = (uint8_t)((((unsigned)color << RECORD_COLOR_SHIFT) |
                        ((unsigned)type & RECORD_TYPE_MASK)) & 0xFFu);
    out[2] = index;
    out[3] = crc8(out, 3u);
}

bool registry_record_decode(const uint8_t record[PIECE_RECORD_BYTES],
                            piece_color_t *color, piece_type_t *type, uint8_t *index)
{
    if (record[0] != (uint8_t)PIECE_RECORD_VERSION) {
        return false;
    }
    if (record[3] != crc8(record, 3u)) {
        return false;
    }
    const uint8_t code = record[1];
    const piece_type_t decoded = (piece_type_t)(code & RECORD_TYPE_MASK);
    if (decoded == PIECE_TYPE_NONE || decoded > PIECE_TYPE_KING) {
        return false;
    }
    if (color != NULL) {
        *color = ((code >> RECORD_COLOR_SHIFT) != 0u) ? PIECE_COLOR_BLACK
                                                      : PIECE_COLOR_WHITE;
    }
    if (type != NULL) {
        *type = decoded;
    }
    if (index != NULL) {
        *index = record[2];
    }
    return true;
}
