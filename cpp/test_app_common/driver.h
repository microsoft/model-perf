// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <stddef.h>
#include <stdint.h>

#include <algorithm>
#include <iomanip>
#include <memory>
#include <msgpack.hpp>
#include <sstream>
#include <string>
#include <vector>

#include "logger.h"
#include "metrics_collector.h"
#include "nlohmann/json.hpp"
#ifdef USE_ORT
#include "ort/ort_session.h"
#endif

namespace model_perf {

using json = nlohmann::json;

class Driver {
  public:
    Driver(const std::string& config_path);
    ~Driver();

    void RunModel();
    void RunPerfTest();

  private:
    json config_;
    std::string root_dir_;
    msgpack::object_handle inputs_handle_;
#ifdef USE_ORT
    std::unique_ptr<OrtSession> inference_session_ptr_;
    std::vector<std::vector<Ort::Value>> inputs_;
#else
    // TODO: add support for other inference sessions
    std::vector<std::vector<float>> inputs_;
#endif

    // SingleStream for perf test
    std::string test_scenario_;
    int min_query_count_;
    int min_duration_ms_;

    // logger
    Logger system_logger_;
    Logger metrics_logger_;
    std::shared_ptr<MetricsCollector> metrics_collector_ptr_;
    uint64_t pid_;

    void ReadInputs();
};
} // namespace model_perf