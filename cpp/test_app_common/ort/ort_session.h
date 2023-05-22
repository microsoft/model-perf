// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <map>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

#include "nlohmann/json.hpp"
#include <onnxruntime_cxx_api.h>

namespace model_perf {

using json = nlohmann::json;

class OrtSession {
  public:
    OrtSession(const json& config);
    ~OrtSession() {}

    std::vector<Ort::Value> Run(const std::vector<Ort::Value>& inputs);

  private:
    static void InitializeOrt();

    json config_;
    std::shared_ptr<Ort::SessionOptions> session_options_;
    std::shared_ptr<Ort::Session> session_;
    std::vector<const char*> input_names_;
    std::vector<const char*> output_names_;
    std::vector<std::string> input_names_str_repr_;
    std::vector<std::string> output_names_str_repr_;

    static std::shared_ptr<Ort::Env> ort_env;
    static std::shared_ptr<Ort::AllocatorWithDefaultOptions> ort_allocator;
};

} // namespace model_perf
