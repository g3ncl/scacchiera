#ifndef CHESSBOARD_CORE_CRC32_H
#define CHESSBOARD_CORE_CRC32_H

#include <stddef.h>
#include <stdint.h>

/* CRC-32, the ordinary reflected polynomial, computed without a table: it
 * runs once per storage transaction on records of a few kilobytes, so 8
 * shifts a byte is nothing against a kilobyte of lookup table in a 512 KB
 * part. One shared implementation, so a sealed record can never disagree
 * with its checker about the algorithm. */
static inline uint32_t crc32_bytes(const uint8_t *data, size_t length)
{
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t index = 0u; index < length; index++) {
        crc ^= (uint32_t)data[index];
        for (uint8_t bit = 0u; bit < 8u; bit++) {
            const uint32_t mask = (uint32_t)(0u - (crc & 1u));
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }
    return ~crc;
}

#endif
