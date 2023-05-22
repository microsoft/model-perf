// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "driver.h"

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Argument Error! It should have 3 arguments like following:" << std::endl;
        std::cerr << "test_app.exe test_config.json mode" << std::endl;
        return -1;
    }

    // Config file
    std::string config_path = argv[1];
    std::replace(config_path.begin(), config_path.end(), '\\', '/');

    // Mode
    std::string mode = argv[2];
    for (auto& c : mode) {
        c = tolower(c);
    }

    // model testing
    if (mode == "all") {
        model_perf::Driver driver(config_path);
        driver.RunModel();
        driver.RunPerfTest();
    } else if (mode == "predict") {
        model_perf::Driver driver(config_path);
        driver.RunModel();
    } else if (mode == "benchmark") {
        model_perf::Driver driver(config_path);
        driver.RunPerfTest();
    } else {
        std::cerr << "Argument Error! Mode should be one of the following: all, predict, benchmark." << std::endl;
        return -1;
    }

    return 0;
}
