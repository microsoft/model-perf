// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <list>
#include "load_gen.h"

class SingleStreamLoadGen:public LoadGen {
  public:
    SingleStreamLoadGen(
        std::shared_ptr<PerfResult> result,
        int64_t min_query_count = 100, 
        int64_t min_duration_ms = 10000);
    SingleStreamLoadGen(
      PerfResult& result,
      int64_t min_query_count = 100,
      int64_t min_duration_ms = 10000);
    virtual ~SingleStreamLoadGen() = default;
    std::list<std::shared_ptr<Query>> IssueQuery();

  private: 
    std::future<bool> pre_query_completed_;
};