cmake_minimum_required(VERSION 3.16)

project(android_test_app_jni VERSION 0.1)

set(ROOT_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../../../../../../../)
include(${ROOT_PATH}/cmake/policy.cmake)
set(CMAKE_CXX_STANDARD 17)
#set(CMAKE_POSITION_INDEPENDENT_CODE ON)
#set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
include(CheckCXXCompilerFlag)
include(CheckLanguage)

add_subdirectory(${ROOT_PATH}/cpp/test_app_common ${CMAKE_CURRENT_BINARY_DIR}/test_app_common)

add_library(android_test_app_jni SHARED 
            jni_bindings.cpp)
set_property(TARGET android_test_app_jni PROPERTY CXX_STANDARD 17)

find_library(log-lib log)

target_link_libraries(android_test_app_jni
                      test_app_common
                      ${log-lib}
                      android)