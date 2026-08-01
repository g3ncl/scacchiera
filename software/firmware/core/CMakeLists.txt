# Built two ways from one source list: as an ESP-IDF component for the target
# image, and as a plain static library for the host gate. A file that will not
# compile both ways is in the wrong layer.
set(CHESSBOARD_CORE_SRCS square.c snapshot.c fault.c engine.c scan_join.c)

if(ESP_PLATFORM)
  idf_component_register(SRCS ${CHESSBOARD_CORE_SRCS} INCLUDE_DIRS "..")
else()
  add_library(chessboard_core STATIC ${CHESSBOARD_CORE_SRCS})
  target_include_directories(chessboard_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/..)
endif()
