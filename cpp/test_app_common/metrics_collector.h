// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once
#include <atomic>
#include <chrono>
#include <ctime>
#include <fstream>
#include <functional>
#include <iostream>
#include <thread>

#include "logger.h"
#include "nlohmann/json.hpp"
#include "perf_utils.h"

namespace model_perf {
class MetricsCollector {
  public:
    MetricsCollector(int& interval)
      : execute_(false)
      , interval_(interval) {
        logger_ = Logger::GetLogger("metrics");
        pid_ = PerformanceUtils::GetPid();
        perf_ptr_ = std::make_shared<PerformanceUtils>();
    }

    ~MetricsCollector() {
        if (execute_) {
            Stop();
        };
    }

    void Start() {
        if (execute_) {
            Stop();
        };

        // Log start time
        logger_.AddInstantEvent("MonitoringStart", "Event", pid_, { { "Interval_Milliseconds", interval_ } });

        // Start thread
        execute_ = true;

        thd_ = std::thread([this]() {
            while (execute_) {
                auto cpu_usage = perf_ptr_->GetCPUUsage();
                auto mem_usage = perf_ptr_->GetMemoryUsage();

                // log cpu
                logger_.AddInstantEvent("CPU", "Performance", pid_, { { "CPU_Percentage", cpu_usage.process_usage } });

                // log memory
                logger_.AddInstantEvent("Memory", "Performance", pid_, { { "Virtual_Memory_KB", mem_usage.virtual_process_usage }, { "Physical_Memory_KB", mem_usage.physical_process_usage } });

                // sleep for interval
                std::this_thread::sleep_for(std::chrono::milliseconds(interval_));
            }
        });
    }

    bool IsRunning() const noexcept {
        return (execute_ && thd_.joinable());
    }

    void Stop() {
        execute_ = false;
        if (thd_.joinable())
            thd_.join();

        // Log end time
        logger_.AddInstantEvent("MonitoringEnd", "Event", pid_, {}, true);
    }

  private:
    std::atomic_bool execute_;
    std::thread thd_;
    int interval_;
    Logger logger_;
    uint64_t pid_;
    std::shared_ptr<PerformanceUtils> perf_ptr_;
};
} // namespace model_perf
