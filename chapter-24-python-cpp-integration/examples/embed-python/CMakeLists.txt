cmake_minimum_required(VERSION 3.20)
project(embed_python_course LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Embed)
find_package(pybind11 CONFIG REQUIRED)

add_executable(embed_strategy src/main.cpp)
target_link_libraries(embed_strategy PRIVATE pybind11::embed)
if(MSVC)
  target_compile_options(embed_strategy PRIVATE /W4 /WX /permissive-)
else()
  target_compile_options(embed_strategy PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
