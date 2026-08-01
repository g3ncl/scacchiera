#ifndef CHESSBOARD_CORE_SQUARE_H
#define CHESSBOARD_CORE_SQUARE_H

#include <stdbool.h>
#include <stdint.h>

#define BOARD_FILES 8
#define BOARD_RANKS 8
#define BOARD_SQUARES (BOARD_FILES * BOARD_RANKS)

/* Zero based so it lines up directly with the sensor array. */
typedef uint8_t square_t;

#define SQUARE_INVALID ((square_t)0xFFu)

square_t square_from_file_rank(char file_letter, uint8_t rank);
char square_file_letter(square_t square);
uint8_t square_rank(square_t square);
bool square_is_valid(square_t square);

#endif
