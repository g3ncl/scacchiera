# Host build only. The ESP-IDF target build lives under main/ and is driven by
# idf.py, not from here; see docs/software/architecture.md for why the two
# builds share core/ and why a file that will not compile in both is misplaced.
cmake_minimum_required(VERSION 3.25)
project(chessboard_firmware C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# V5 asks for strict warnings, static analysis and available sanitizers. gcc's
# -fanalyzer stands in for clang-tidy, which is not installed on this machine.
add_compile_options(
  -Wall -Wextra -Werror -Wpedantic
  -Wconversion -Wsign-conversion -Wshadow -Wcast-qual -Wstrict-prototypes
  -Wmissing-prototypes -Wdouble-promotion -Wformat=2 -Wundef
)

option(FIRMWARE_ANALYZER "Enable gcc static analysis" ON)
option(FIRMWARE_SANITIZE "Enable address and undefined-behaviour sanitizers" ON)

# V5 asks for "available sanitizers". gcc accepts the flag whether or not the
# runtime libraries are installed and only fails at link, so this probes a real
# link rather than trusting the compiler, and reports loudly when it has to
# fall back. On Fedora the missing pieces are libasan and libubsan.
if(FIRMWARE_SANITIZE)
  include(CheckCSourceCompiles)
  set(CMAKE_REQUIRED_FLAGS "-fsanitize=address,undefined")
  set(CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=address,undefined")
  check_c_source_compiles("int main(void){return 0;}" FIRMWARE_SANITIZERS_LINK)
  unset(CMAKE_REQUIRED_FLAGS)
  unset(CMAKE_REQUIRED_LINK_OPTIONS)

  if(NOT FIRMWARE_SANITIZERS_LINK)
    message(WARNING
      "Sanitizer runtimes are missing, so the host gate runs without them. "
      "Install libasan and libubsan to close this part of V5.")
  endif()
endif()

# The analyzer and the sanitizers are both V5 obligations, and they cannot
# share a build: gcc's analyzer runs on the instrumented code when both are
# enabled and reports uninitialized values that exist only in the sanitizer's
# own temporaries, with no source location to inspect. So each gets a clean
# configuration: sanitizers whenever they link, the analyzer otherwise, and a
# second configure with -DFIRMWARE_SANITIZE=OFF is the analyzer pass.
if(FIRMWARE_SANITIZE AND FIRMWARE_SANITIZERS_LINK)
  add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
  add_link_options(-fsanitize=address,undefined)
  if(FIRMWARE_ANALYZER)
    message(STATUS
      "Sanitizers active; the gcc analyzer is skipped in this configuration. "
      "Configure with -DFIRMWARE_SANITIZE=OFF to run the analyzer pass.")
  endif()
elseif(FIRMWARE_ANALYZER AND CMAKE_C_COMPILER_ID STREQUAL "GNU")
  add_compile_options(-fanalyzer)
endif()

add_subdirectory(core)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(test)
endif()
