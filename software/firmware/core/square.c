#include "core/square.h"

square_t square_from_file_rank(char file_letter, uint8_t rank)
{
    if (file_letter < 'a' || file_letter > 'h' || rank < 1u || rank > BOARD_RANKS) {
        return SQUARE_INVALID;
    }
    const uint8_t file_index = (uint8_t)(file_letter - 'a');
    return (square_t)(((rank - 1u) * BOARD_FILES) + file_index);
}

char square_file_letter(square_t square)
{
    if (!square_is_valid(square)) {
        return '?';
    }
    return (char)('a' + (square % BOARD_FILES));
}

uint8_t square_rank(square_t square)
{
    if (!square_is_valid(square)) {
        return 0u;
    }
    return (uint8_t)((square / BOARD_FILES) + 1u);
}

bool square_is_valid(square_t square)
{
    return square < BOARD_SQUARES;
}
