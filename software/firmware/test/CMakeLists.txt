# Unity is pinned by tag so the host gate is reproducible. CMock is not fetched
# yet: nothing here needs generated mocks, because the hardware boundary is a
# handful of free functions that the fakes implement directly.
include(FetchContent)
FetchContent_Declare(
  unity
  GIT_REPOSITORY https://github.com/ThrowTheSwitch/Unity.git
  GIT_TAG v2.6.1
  GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(unity)

# Unity's own sources do not survive this project's warning set, and they are
# not ours to fix.
target_compile_options(unity PRIVATE -w)

add_library(chessboard_fakes STATIC
  fake_clock.c
  fake_scan.c
  fake_output.c
  fake_storage.c
)
target_link_libraries(chessboard_fakes PUBLIC chessboard_core)
target_include_directories(chessboard_fakes PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

function(chessboard_test name)
  add_executable(${name} ${name}.c)
  target_link_libraries(${name} PRIVATE chessboard_core chessboard_fakes unity)
  # port/ itself needs ESP-IDF, but its pin map and mask headers are plain
  # macros, so the host gate can assert them.
  target_include_directories(${name} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/..)
  add_test(NAME ${name} COMMAND ${name})
endfunction()

chessboard_test(test_square)
chessboard_test(test_snapshot)
chessboard_test(test_fault)
chessboard_test(test_engine_stub)
chessboard_test(test_fakes)
chessboard_test(test_expander_config)
chessboard_test(test_matrix_encoding)
chessboard_test(test_lightbar_encoding)
