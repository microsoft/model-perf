cmake_minimum_required(VERSION 3.16 FATAL_ERROR)

project(model-perf-toolkit VERSION 0.1)

include(CMakeDependentOption)

# c/c++ common compliation options
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(PYTHON
    ""
    CACHE STRING "set which version of python to use, default to auto detect")
set(CMAKE_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR})
option(PY_LOAD_GEN "build load gen python interface" ON)

include(cmake/policy.cmake)
include(cmake/detect_python.cmake)
add_subdirectory(third_party)
add_subdirectory(cpp/load_gen)
add_subdirectory(python)
#set(ENV{CTEST_OUTPUT_ON_FAILURE} "TRUE")
enable_testing()