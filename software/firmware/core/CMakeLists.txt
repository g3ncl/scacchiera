# core/ is the layer that must build unchanged on the host and on the ESP32-C6.
# It includes no ESP-IDF header and calls nothing in port/.
add_library(chessboard_core STATIC
  square.c
  snapshot.c
  fault.c
  engine.c
)
target_include_directories(chessboard_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/..)
