// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.


#include "driver.h"
#include "ort/ort_data_conversion.h"
#include "single_stream_load_gen.h"
#include "str_utils.h"

#include <chrono>
#include <fstream>
#include <thread>

namespace model_perf {

std::string GetDirectoryFromPath(const std::string& filePath) {
    // Find the last occurrence of a path separator
    const auto lastSeparator = filePath.find_last_of("/\\");

    // If there is no separator, the directory is the current directory
    if (lastSeparator == std::string::npos) {
        return ".";
    }

    // Extract the directory path
    return filePath.substr(0, lastSeparator);
}

Driver::Driver(const std::string& config_path) {
    system_logger_ = Logger::CreateSystemLogger();
    system_logger_.Info("Get system logger with name model_perf");
    pid_ = PerformanceUtils::GetPid();

    // Load config
    std::ifstream f(config_path);
    config_ = json::parse(f);
    root_dir_ = GetDirectoryFromPath(config_path);
    config_["root_dir"] = root_dir_;

    // Create metrics logger
    metrics_logger_ = Logger("metrics", false, false, root_dir_ + "/metrics.json", false, spdlog::level::level_enum::info, "%v");
    metrics_logger_.Info("[");

    // Create metrics collector
    int interval = config_["metrics_collector"]["interval_ms"];
    metrics_collector_ptr_ = std::make_shared<MetricsCollector>(interval);
    metrics_collector_ptr_->Start();

    // Sleep 1000 milliseconds for monitoring thread to be ready
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    // Log start time
    metrics_logger_.AddInstantEvent("ModelTestingStart", "Event", pid_, {});

    // create ort inference session
    metrics_logger_.AddInstantEvent("CreateInferenceSessionStart", "Event", pid_, {});
    inference_session_ptr_ = std::make_unique<OrtSession>(config_);
    metrics_logger_.AddInstantEvent("CreateInferenceSessionEnd", "Event", pid_, {});

    // Sleep 200 milliseconds for monitoring thread to collect metric
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
}

Driver::~Driver() {
    metrics_logger_.AddInstantEvent("ModelTestingEnd", "Event", pid_, {});
    spdlog::drop_all();
}

void Driver::ReadInputs() {
    // read inputs from file
    std::string inputs_path = root_dir_ + "/" + config_["dataset"]["path"].get<std::string>();
    std::ifstream ifile;
    ifile.open(inputs_path.c_str(), std::ios::binary | std::ios::in | std::ios::ate);
    if (!ifile.good()) {
        std::cout << "Inputs file error" << std::endl;
    }

    long size;
    std::ifstream file(inputs_path.c_str(), std::ios::in | std::ios::binary | std::ios::ate);
    size = file.tellg();
    if (size < 0) {
        std::cout << "Binary file size < 0" << std::endl;
    }
    file.seekg(0, std::ios::beg);

    std::vector<char> inputs_buffer;
    inputs_buffer.resize(size);
    file.read(inputs_buffer.data(), size);
    file.close();

    // deserialize inputs, deserialized object is valid during the msgpack::object_handle instance is alive.
    inputs_handle_ = msgpack::unpack(inputs_buffer.data(), inputs_buffer.size());
    msgpack::object const& obj = inputs_handle_.get();

    inputs_ = obj.as<std::vector<std::vector<Ort::Value>>>();

    if (inputs_.size() == 0) {
        throw std::runtime_error("No model inputs found");
    }
}

void Driver::RunModel() {
    // reuse inputs if it's not empty to save time and memory
    if (inputs_.empty()) {
        ReadInputs();
    }

    metrics_logger_.AddInstantEvent("RunModelStart", "Event", pid_, {});

    // run model
    std::vector<std::vector<Ort::Value>> outputs;
    for (int k = 0; k < inputs_.size(); k++) {
        std::vector<Ort::Value>& input = inputs_[k];
        std::vector<Ort::Value> output_tensors = inference_session_ptr_->Run(input);
        outputs.emplace_back(std::move(output_tensors));
    }

    // Sleep 200 milliseconds waiting for monitoring thread to collect metric
    std::this_thread::sleep_for(std::chrono::milliseconds(200));
    metrics_logger_.AddInstantEvent("RunModelEnd", "Event", pid_, {});

    // serialize model outputs into file
    std::stringstream buffer;
    msgpack::pack(buffer, outputs);

    std::string outputs_path = root_dir_ + "/model_outputs.msgpack";
    std::ofstream out_file(outputs_path.c_str(), std::ios::out | std::ios::binary);

    out_file << buffer.rdbuf();
    out_file.close();
}

void Driver::RunPerfTest() {
    // reuse inputs if it's not empty to save time and memory
    if (inputs_.empty()) {
        ReadInputs();
    }

    PerfResult perf_result;
    min_query_count_ = config_["load_gen"]["min_query_count"].get<int>();
    min_duration_ms_ = config_["load_gen"]["min_duration_ms"].get<int>();
    SingleStreamLoadGen load_gen(perf_result, min_query_count_, min_duration_ms_);
    std::shared_ptr<Query> q;

    metrics_logger_.AddInstantEvent("RunPerfTestStart", "Event", pid_, {});

    // run perf test
    do {
        q = load_gen.IssueQuery().front();

        inference_session_ptr_->Run(inputs_[0]);

        perf_result.CompleteQuery(q->id, false);
    } while (q->id >= 0);

    metrics_logger_.AddInstantEvent("RunPerfTestEnd", "Event", pid_, {});

    // get perf result
    std::vector<double> percentiles = { 0.5, 0.7, 0.9, 0.95, 0.99 };
    std::vector<double> latecies = perf_result.GetLatencies(percentiles, false, false, false);

    // log latency
    metrics_logger_.AddInstantEvent("Latency", "Performance", pid_, { { "P50", latecies[0] }, { "P70", latecies[1] }, { "P90", latecies[2] }, { "P95", latecies[3] }, { "P99", latecies[4] } });
}
} // namespace model_perf