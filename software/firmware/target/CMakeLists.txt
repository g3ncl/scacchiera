# ESP-IDF project root for the ESP32-C6 image. Kept in its own directory
# because the host gate owns ../CMakeLists.txt, and the two build systems
# cannot share a project root. Both compile the same core/ sources.
cmake_minimum_required(VERSION 3.16)

# main/ lives beside core/ and port/ rather than at this project root, so it
# has to be named here like any other component directory.
set(EXTRA_COMPONENT_DIRS
  ${CMAKE_CURRENT_LIST_DIR}/../core
  ${CMAKE_CURRENT_LIST_DIR}/../port
  ${CMAKE_CURRENT_LIST_DIR}/../main
)
set(COMPONENTS main core port)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(chessboard)
