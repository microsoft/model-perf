// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <map>
#include <set>
#include <vector>
#include <chrono>
#include <memory>
#include <mutex>
#include <unordered_map>
#include <list>
#include "query.h"

class PerfResult {
  public:
    PerfResult();
    virtual ~PerfResult() = default;
    void AddQuery(int64_t id);
    void AddQuery(std::shared_ptr<Query> q);

    void CompleteQuery(int64_t id, bool error=false, float latency_ms=-1.0);

    double GetActualQPS();
    int64_t CountSucceeded();
    int64_t CountFailed();

    std::vector<double> GetLatencies(std::vector<double> percentiles, bool min = true, bool avg = true, bool max = true);

  private:
    static bool set_cmp(const std::shared_ptr<Query>& a, const std::shared_ptr<Query>& b) {
        return a->latency < b->latency;
    }

    std::atomic<int64_t> num_queries_;
    std::atomic<int64_t> num_succeeded_queries_;
    std::atomic<int64_t> num_failed_queries_;

    std::mutex lock_;
    std::unordered_map<int64_t, std::shared_ptr<Query>> pending_queries_;
    std::list<std::shared_ptr<Query>> succeeded_queries_buffer_;
    std::list<std::shared_ptr<Query>> failed_queries_;

    std::set<std::shared_ptr<Query>, decltype(set_cmp)*> succeeded_queries_sorted_;

    std::chrono::high_resolution_clock::time_point start_time_;
    std::chrono::nanoseconds total_latency_ns_;
};