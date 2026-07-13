cmake_minimum_required(VERSION 3.20)
project(course_hello_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(hello_cpp MODULE src/bindings.cpp)
if(MSVC)
  target_compile_options(hello_cpp PRIVATE /W4 /WX)
else()
  target_compile_options(hello_cpp PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

install(TARGETS hello_cpp LIBRARY DESTINATION . RUNTIME DESTINATION .)
