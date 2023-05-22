option(PY_LOAD_GEN "build load gen python interface" OFF)
include(FetchContent)

add_library(test_app_common STATIC "")

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../load_gen ${CMAKE_CURRENT_BINARY_DIR}/load_gen)

target_sources(test_app_common PRIVATE 
               driver.h
               driver.cpp
               logger.h
               logger.cpp
               metrics_collector.h
               perf_utils.h
               str_utils.h
               str_utils.cpp)

include(${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/nlohmann_json.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/spdlog.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/msgpack.cmake)

target_include_directories(test_app_common PUBLIC 
    ${NLOHMANN_JSON_INCLUDE_DIR}
    ${SPDLOG_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(test_app_common PUBLIC load_gen spdlog::spdlog msgpack-cxx)

set(USE_ORT "" CACHE STRING "use ort as the inferance runtime")
if(NOT ${USE_ORT} STREQUAL "")
    target_sources(test_app_common PRIVATE 
                   ort/ort_data_conversion.h
                   ort/ort_session.h
                   ort/ort_session.cpp)
    set(ORT_VERSION ${USE_ORT})
    include(${CMAKE_CURRENT_SOURCE_DIR}/../../third_party/onnxruntime.cmake)
    # official prebuilt iOS version use xcframework
    # if(NOT ${CMAKE_SYSTEM_NAME} MATCHES "iOS")
    target_link_libraries(test_app_common PUBLIC onnxruntime)
    # endif()

    get_target_property(ORT_BINARY_DIR onnxruntime BINARY_DIRECTORY)
    set_target_properties(test_app_common PROPERTIES ORT_BINARY_DIR ${ORT_BINARY_DIR})
endif()
