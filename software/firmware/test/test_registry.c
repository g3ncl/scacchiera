#include "unity.h"

#include <stddef.h>
#include <string.h>

#include "core/crc32.h"
#include "core/registry.h"

static piece_registry_t registry;

void setUp(void)
{
    registry_init(&registry);
}

void tearDown(void) {}

static void test_a_new_registry_knows_nothing(void)
{
    TEST_ASSERT_EQUAL_UINT8(0u, registry.count);
    TEST_ASSERT_FALSE(registry_contains(&registry, 0x1234u));
}

static void test_a_registered_tag_resolves_to_its_piece(void)
{
    TEST_ASSERT_TRUE(
        registry_add(&registry, 0xAAu, PIECE_COLOR_BLACK, PIECE_TYPE_KNIGHT, 1u));

    piece_color_t color = PIECE_COLOR_WHITE;
    piece_type_t type = PIECE_TYPE_NONE;
    TEST_ASSERT_TRUE(registry_lookup(&registry, 0xAAu, &color, &type));
    TEST_ASSERT_EQUAL_INT(PIECE_COLOR_BLACK, color);
    TEST_ASSERT_EQUAL_INT(PIECE_TYPE_KNIGHT, type);
}

/* Re-running provisioning over the same set is harmless; quietly changing what
 * a tag means is not, because the board would read differently before and
 * after with nothing to show for it. */
static void test_a_tag_cannot_quietly_become_a_different_piece(void)
{
    TEST_ASSERT_TRUE(registry_add(&registry, 0xAAu, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK, 0u));
    TEST_ASSERT_TRUE(registry_add(&registry, 0xAAu, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK, 0u));
    TEST_ASSERT_FALSE(registry_add(&registry, 0xAAu, PIECE_COLOR_WHITE, PIECE_TYPE_QUEEN, 0u));
    TEST_ASSERT_EQUAL_UINT8(1u, registry.count);
}

static void test_an_untyped_piece_is_refused(void)
{
    TEST_ASSERT_FALSE(registry_add(&registry, 0xAAu, PIECE_COLOR_WHITE, PIECE_TYPE_NONE, 0u));
}

static void test_the_registry_fills_and_stops(void)
{
    for (uint8_t index = 0u; index < PIECE_REGISTRY_MAX; index++) {
        TEST_ASSERT_TRUE(registry_add(&registry, 0x100u + index, PIECE_COLOR_WHITE,
                                      PIECE_TYPE_PAWN, index));
    }
    TEST_ASSERT_FALSE(
        registry_add(&registry, 0x9999u, PIECE_COLOR_WHITE, PIECE_TYPE_PAWN, 0u));
}

static void test_removal(void)
{
    TEST_ASSERT_TRUE(registry_add(&registry, 0xAAu, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK, 0u));
    TEST_ASSERT_TRUE(registry_add(&registry, 0xBBu, PIECE_COLOR_BLACK, PIECE_TYPE_KING, 0u));
    TEST_ASSERT_TRUE(registry_remove(&registry, 0xAAu));
    TEST_ASSERT_FALSE(registry_contains(&registry, 0xAAu));
    TEST_ASSERT_TRUE(registry_contains(&registry, 0xBBu));
    TEST_ASSERT_FALSE(registry_remove(&registry, 0xAAu));
}

static void test_the_tag_record_round_trips_for_every_piece(void)
{
    static const piece_type_t types[6] = {PIECE_TYPE_PAWN,  PIECE_TYPE_KNIGHT,
                                          PIECE_TYPE_BISHOP, PIECE_TYPE_ROOK,
                                          PIECE_TYPE_QUEEN, PIECE_TYPE_KING};
    for (uint8_t index = 0u; index < 6u; index++) {
        for (uint8_t color = 0u; color < 2u; color++) {
            uint8_t record[PIECE_RECORD_BYTES];
            registry_record_encode((piece_color_t)color, types[index], index, record);

            piece_color_t out_color = PIECE_COLOR_WHITE;
            piece_type_t out_type = PIECE_TYPE_NONE;
            uint8_t out_index = 0xFFu;
            TEST_ASSERT_TRUE(registry_record_decode(record, &out_color, &out_type, &out_index));
            TEST_ASSERT_EQUAL_INT(color, out_color);
            TEST_ASSERT_EQUAL_INT(types[index], out_type);
            TEST_ASSERT_EQUAL_UINT8(index, out_index);
        }
    }
}

/* Each of these is a TAG_FAULT rather than a piece, and they are refused
 * separately so a log can say which one. */
static void test_a_damaged_record_is_refused(void)
{
    uint8_t record[PIECE_RECORD_BYTES];
    registry_record_encode(PIECE_COLOR_WHITE, PIECE_TYPE_QUEEN, 0u, record);
    TEST_ASSERT_TRUE(registry_record_decode(record, NULL, NULL, NULL));

    /* A tag written by a future version. */
    uint8_t wrong_version[PIECE_RECORD_BYTES];
    memcpy(wrong_version, record, sizeof(record));
    wrong_version[0] = (uint8_t)(PIECE_RECORD_VERSION + 1u);
    TEST_ASSERT_FALSE(registry_record_decode(wrong_version, NULL, NULL, NULL));

    /* A single flipped bit anywhere in the payload. */
    uint8_t corrupt[PIECE_RECORD_BYTES];
    memcpy(corrupt, record, sizeof(record));
    corrupt[2] = (uint8_t)(corrupt[2] ^ 0x01u);
    TEST_ASSERT_FALSE(registry_record_decode(corrupt, NULL, NULL, NULL));

    /* A code that names no piece. */
    uint8_t bad_code[PIECE_RECORD_BYTES];
    bad_code[0] = (uint8_t)PIECE_RECORD_VERSION;
    bad_code[1] = 0x0Fu;
    bad_code[2] = 0u;
    bad_code[3] = 0u;
    TEST_ASSERT_FALSE(registry_record_decode(bad_code, NULL, NULL, NULL));
}

/* The registry is persisted, so it carries the same seal as the game record:
 * a blob whose layout moved while its size did not must be refused rather
 * than reinterpreted as confident identities. */
static void test_a_sealed_registry_validates_and_a_tampered_one_does_not(void)
{
    TEST_ASSERT_TRUE(registry_add(&registry, 0xAAu, PIECE_COLOR_WHITE, PIECE_TYPE_ROOK, 0u));
    registry_seal(&registry);
    TEST_ASSERT_TRUE(registry_valid(&registry));

    registry.entries[0].uid ^= 1u;
    TEST_ASSERT_FALSE(registry_valid(&registry));
}

static void test_a_version_from_the_future_is_refused(void)
{
    registry_seal(&registry);
    registry.version = (uint16_t)(PIECE_REGISTRY_VERSION + 1u);
    /* Re-checksummed, so the version check is what fails rather than the CRC. */
    registry.crc32 =
        crc32_bytes((const uint8_t *)&registry, offsetof(piece_registry_t, crc32));
    TEST_ASSERT_FALSE(registry_valid(&registry));
}

/* A corrupt count fails validation, and even before validation it must never
 * become a loop bound: under the host sanitizers these lookups would fault on
 * an out-of-bounds read if count were trusted. */
static void test_an_oversized_count_is_refused_and_never_indexed(void)
{
    registry_seal(&registry);
    registry.count = 0xFFu;
    registry.crc32 =
        crc32_bytes((const uint8_t *)&registry, offsetof(piece_registry_t, crc32));
    TEST_ASSERT_FALSE(registry_valid(&registry));
    TEST_ASSERT_FALSE(registry_contains(&registry, 0x123456u));
    TEST_ASSERT_FALSE(registry_remove(&registry, 0x123456u));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_a_new_registry_knows_nothing);
    RUN_TEST(test_a_registered_tag_resolves_to_its_piece);
    RUN_TEST(test_a_tag_cannot_quietly_become_a_different_piece);
    RUN_TEST(test_an_untyped_piece_is_refused);
    RUN_TEST(test_the_registry_fills_and_stops);
    RUN_TEST(test_removal);
    RUN_TEST(test_the_tag_record_round_trips_for_every_piece);
    RUN_TEST(test_a_damaged_record_is_refused);
    RUN_TEST(test_a_sealed_registry_validates_and_a_tampered_one_does_not);
    RUN_TEST(test_a_version_from_the_future_is_refused);
    RUN_TEST(test_an_oversized_count_is_refused_and_never_indexed);
    return UNITY_END();
}
