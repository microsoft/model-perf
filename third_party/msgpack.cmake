# nlohmann/json
FetchContent_Declare(
    msgpack
    GIT_REPOSITORY https://github.com/msgpack/msgpack-c.git
    GIT_TAG cpp_master)

set(MSGPACK_USE_BOOST
    OFF
    CACHE BOOL "" FORCE)

set(MSGPACK_BUILD_TESTS
    OFF
    CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(msgpack)