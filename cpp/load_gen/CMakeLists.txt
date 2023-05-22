add_library(load_gen STATIC)
target_sources(
    load_gen
    PRIVATE "query.h"
            "load_gen.h"
            "load_gen.cpp"
            "server_load_gen.h"
            "server_load_gen.cpp"
            "single_stream_load_gen.h"
            "single_stream_load_gen.cpp"
            "perf_result.h"
            "perf_result.cpp")
target_include_directories(load_gen PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    target_link_libraries(load_gen stdc++fs)
endif()

if(PY_LOAD_GEN)
    # pybind11 use the variable PYTHON_EXECUTABLE(case sensitive) to detect python
    set(PYTHON_EXECUTABLE ${Python3_EXECUTABLE})
    pybind11_add_module(load_gen_c)
    target_sources(
        load_gen_c
        PRIVATE "python_exports.cpp")
    target_link_libraries(load_gen_c PRIVATE load_gen)
endif()
