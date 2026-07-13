cmake_minimum_required(VERSION 3.20)
project(cpp_survival LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(score src/score.cpp)
target_include_directories(score PUBLIC include)

if(MSVC)
  target_compile_options(score PRIVATE /W4 /WX)
else()
  target_compile_options(score PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

add_executable(cpp_survival src/main.cpp)
target_link_libraries(cpp_survival PRIVATE score)

enable_testing()
add_executable(score_tests tests/score_tests.cpp)
target_link_libraries(score_tests PRIVATE score)
add_test(NAME score_contract COMMAND score_tests)
