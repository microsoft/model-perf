
#spdlog
FetchContent_Declare(
    spdlog
    GIT_REPOSITORY https://github.com/gabime/spdlog.git
    GIT_TAG v1.11.0)
FetchContent_MakeAvailable(spdlog)

set(SPDLOG_INCLUDE_DIR
    ${spdlog_SOURCE_DIR}/include
    CACHE PATH "" FORCE)