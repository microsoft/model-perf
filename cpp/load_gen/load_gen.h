// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <cstdint>
#include <chrono>
#include <memory>
#include <atomic>
#include <random>
#include "query.h"
#include "perf_result.h"

class LoadGen {
  public:
    LoadGen(std::shared_ptr<PerfResult> result, int64_t min_query_count=100, int64_t min_duration_ms=10000);
    LoadGen(PerfResult& result, int64_t min_query_count = 100, int64_t min_duration_ms = 10000);
    virtual ~LoadGen() = default;
    std::shared_ptr<Query> IssueQuery();
    int64_t CountIssued();
    double GetIssuedQPS();

  protected:
    unsigned seed_;
    std::mt19937 rng_; // Pseudo-random number generation

  private:
    PerfResult* result_;    // non-owning pointer
    int64_t min_query_count_;
    int64_t min_duration_ms_;
    static std::atomic_int64_t next_query_id_;

    std::chrono::high_resolution_clock::time_point start_time_;
    std::atomic<int64_t> issued_query_count_;
};