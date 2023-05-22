// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <thread>
#include <iostream>
#include "server_load_gen.h"

ServerLoadGen::ServerLoadGen(std::shared_ptr<PerfResult> result, float target_qps, int64_t min_query_count, int64_t min_duration_ms)
  : LoadGen(result, min_query_count, min_duration_ms)
  , target_qps_(target_qps)
  , exp_(target_qps_) {
    auto now = std::chrono::high_resolution_clock::now();
    next_schedule_time_ = now + std::chrono::duration_cast<std::chrono::nanoseconds>(
                                  std::chrono::duration<double>(exp_(rng_)));
}

std::list<std::shared_ptr<Query>> ServerLoadGen::IssueQuery() {
    auto now = std::chrono::high_resolution_clock::now();

    // for the first query
    if (CountIssued() == 0) {
        next_schedule_time_ = now + std::chrono::duration_cast<std::chrono::nanoseconds>(
                                      std::chrono::duration<double>(exp_(rng_)));
    }
    std::list<std::shared_ptr<Query>> res;

    while (next_schedule_time_ <= now) {
        res.push_back(LoadGen::IssueQuery());
        next_schedule_time_ += std::chrono::duration_cast<std::chrono::nanoseconds>(
          std::chrono::duration<double>(exp_(rng_)));
    }

    if (res.size() != 0) {
        return res;
    }

    if (now < next_schedule_time_) {
        std::this_thread::sleep_until(next_schedule_time_);
        res.push_back(LoadGen::IssueQuery());
        next_schedule_time_ += std::chrono::duration_cast<std::chrono::nanoseconds>(
          std::chrono::duration<double>(exp_(rng_)));
    }
    
    return res;
}

double ServerLoadGen::TestQPS() {
    std::list<std::shared_ptr<Query>> qs;
    do {
        qs = IssueQuery();
    } while ((*qs.rbegin())->id >= 0);
    return GetIssuedQPS();
}