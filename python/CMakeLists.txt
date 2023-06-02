if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    set(DIST_PLATFORM "win_amd64")
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(DIST_PLATFORM "manylinux1_x86_64")
endif()

add_custom_target(
    model_perf_whl ALL
    DEPENDS load_gen_c
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_SOURCE_DIR}/src/model_perf/lib/
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:load_gen_c> ${CMAKE_CURRENT_SOURCE_DIR}/src/model_perf/lib/

    # copy cpp and third_party folders to python/src/model_perf
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_SOURCE_DIR}/src/model_perf/cpp
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_SOURCE_DIR}/src/model_perf/third_party
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_ROOT_DIR}/cpp ${CMAKE_CURRENT_SOURCE_DIR}/src/model_perf/cpp
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_ROOT_DIR}/third_party ${CMAKE_CURRENT_SOURCE_DIR}/src/model_perf/third_party

    COMMAND "${Python3_EXECUTABLE}" -m pip install -e .
    COMMAND "stubgen" -p model_perf.lib.load_gen_c -o src
    COMMAND "${Python3_EXECUTABLE}" -m build . --wheel -C \"--build-option=--plat ${DIST_PLATFORM}\"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

# add_test(
#     NAME test_model_perf_whl
#     COMMAND "${Python3_EXECUTABLE}" -m unittest discover test/
#     WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

# set_tests_properties(test_pyis_python_whl PROPERTIES ENVIRONMENT CTEST_OUTPUT_ON_FAILURE=TRUE)