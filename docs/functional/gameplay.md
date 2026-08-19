# Gameplay

How a player uses the connected chessboard. The physical typed position is authoritative and the
board works without a connected browser. This behavior does not depend on the sensing architecture:
it only assumes that each square's occupant, and each piece's color and type, can be read.

## Starting and recording

Press the single button to start a new game. The board reads the color and type on all 64 squares
and accepts only the standard starting position. It reports the exact mismatched square or tag fault
instead of inferring a piece from move history.

During a game, a stable legal move becomes provisional. It is committed when the opponent first
lifts one of their pieces. Until that point, returning to the previous position cancels the move,
and a different legal move replaces it. The owner UI also provides an explicit undo for honest
corrections.

Captures, castling, and en passant come from typed position changes. For promotion, first place the
pawn on the final rank, then replace it with a same-color queen, rook, bishop, or knight. The
replacement tag specifies the promotion. A pawn left on the final rank is not a completed move.

An illegal stable position flashes red on the offending side and is not recorded. Checkmate,
stalemate, dead positions, fivefold repetition, and the 75-move rule finish automatically. Claimable
threefold repetition and 50-move draws are displayed as hints.

## Clock and results

Immediately after a verified start position, a ten-second window allows time-control selection: move
the white king from e1 to d4, d5, e4, or e5 and hold it for roughly three seconds. Return the king
to e1 to arm the selected preset. Otherwise the game is untimed.

The board switches the running clock when a move is placed. A provisional take-back switches it back.
A short button press pauses or resumes it. Flag fall ends the game, except that insufficient mating
material produces a draw.

To resign, remove one king for five seconds, then leave it absent through the displayed 15-second
countdown. Removing both kings follows the same countdown to agree a draw. Returning a king cancels
the gesture.

## Sleep and battery

The board sleeps after about 20 idle minutes when no game or clients are active. A game in progress
never auto-sleeps. At critically low battery voltage, it saves the current game and shuts down after
five minutes unless USB power is connected.

## Faults

Faults never change the stored chess position, and the board never converts a sensing fault into a
guessed legal move.

| Fault | Meaning | Recovery |
| --- | --- | --- |
| `TAG_FAULT` | Unknown version, code, CRC, or unreadable changed piece | Remove or re-provision the indicated piece. |
| `UID_DUPLICATE` | One physical UID appears in two logical places | Remove the duplicate or inspect for a cloned tag. |
| `RF_CROSSTALK` | One tag is read in more than one place in the same scan (for example a piece coupling to two adjacent sensing lines) | Recenter the piece, then run RF diagnostics. |
| `SQUARE_UNSTABLE` | A square repeatedly changes between present, absent, or unreadable | Hold the position still and inspect that square. |
| `BOARD_MISMATCH` | Saved game and complete physical snapshot differ after restart | Use guided resynchronization or start a new game. |
| `SQUARE_CONFLICT` | Two different tags resolve to the same square (for example two pieces standing within one square's footprint) | Inspect that square and remove the extra piece. |

## Piece provisioning

Provisioning is a maintenance operation protected by a long button hold and owner confirmation. For a
new set, place the normal 32 pieces in their standard starting position. The board writes the
expected code to each tag, reads it back, and records its UID. It then prompts for each spare
promotion piece.

A replacement tag can be written for one selected piece class. Provisioning refuses to overwrite a
tag already detected elsewhere on the board.

## Browser client

Any browser client mirrors board state. The first client after a new game becomes the owner; later
clients are spectators. The owner can edit PGN metadata, manage time presets and brightness, run
diagnostics, provision pieces, resync, export or manage games, and adjust WiFi settings. The client
may load Stockfish in a Web Worker for optional analysis.

Completed games are stored as PGN with standard tags and SAN. The board persists an in-progress
snapshot after every committed move, compares it with a complete physical typed position after
restart, and requires resynchronization if they differ.
