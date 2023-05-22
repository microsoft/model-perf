// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "driver.h"

namespace model_perf{

void RunModelTest(std::string config_path) {
    Driver* driver_ptr = new Driver(config_path);
    driver_ptr->RunModel();
    driver_ptr->RunPerfTest();
    delete(driver_ptr);
}
}
