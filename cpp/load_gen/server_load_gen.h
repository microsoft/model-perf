// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <list>
#include "load_gen.h"

class ServerLoadGen:public LoadGen {
  public:
    ServerLoadGen(std::shared_ptr<PerfResult> result, float target_qps, int64_t min_query_count = 100, int64_t min_duration_ms = 10000);
    virtual ~ServerLoadGen() = default;
    std::list<std::shared_ptr<Query>> IssueQuery();
    double TestQPS();

  private:
    float target_qps_;  
    std::exponential_distribution<double> exp_;
    std::chrono::high_resolution_clock::time_point next_schedule_time_;
};