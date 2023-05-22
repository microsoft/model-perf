// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <thread>
#include <iostream>
#include "single_stream_load_gen.h"

SingleStreamLoadGen::SingleStreamLoadGen(PerfResult& result, int64_t min_query_count, int64_t min_duration_ms)
  : LoadGen(result, min_query_count, min_duration_ms){
}

SingleStreamLoadGen::SingleStreamLoadGen(std::shared_ptr<PerfResult> result, int64_t min_query_count, int64_t min_duration_ms)
  : LoadGen(result, min_query_count, min_duration_ms) {
}

std::list<std::shared_ptr<Query>> SingleStreamLoadGen::IssueQuery() {
    std::list<std::shared_ptr<Query>> res;

    // for the first query or pre query is completed.
    if (CountIssued() == 0 || pre_query_completed_.get()) {
        auto q = LoadGen::IssueQuery();
        q->completed = std::make_shared<std::promise<bool>>();
        res.push_back(q);
        pre_query_completed_ = q->completed->get_future();       
    }
    return res;
}
