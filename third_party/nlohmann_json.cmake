# nlohmann/json
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2)
FetchContent_MakeAvailable(nlohmann_json)

set(NLOHMANN_JSON_INCLUDE_DIR
    ${nlohmann_json_SOURCE_DIR}/include
    CACHE PATH "" FORCE)