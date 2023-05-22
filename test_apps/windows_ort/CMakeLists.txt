# cmake -S . -B build -DUSE_ORT="1.14.1"
# cmake --build build --config Release
cmake_minimum_required(VERSION 3.24)

project(windows_test_app)

# specify C++ standard
include(${CMAKE_CURRENT_SOURCE_DIR}/../../cmake/policy.cmake)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
include(CheckCXXCompilerFlag)
include(CheckLanguage)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../cpp/test_app_common ${CMAKE_CURRENT_BINARY_DIR}/test_app_common)

add_executable(test_app
               "test_app.cpp"
               )

target_link_libraries(test_app test_app_common)

if(NOT ${USE_ORT} STREQUAL "")
    # copy onnxruntime dlls to output directory
    get_target_property(ORT_BINARY_DIR test_app_common ORT_BINARY_DIR)
    add_custom_command(TARGET test_app POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy_directory "${ORT_BINARY_DIR}" $<TARGET_FILE_DIR:test_app>)
endif()
