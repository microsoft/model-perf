// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "load_gen.h"

std::atomic_int64_t LoadGen::next_query_id_{ 0 };

LoadGen::LoadGen(PerfResult& result, int64_t min_query_count, int64_t min_duration_ms)
  : seed_(std::chrono::system_clock::now().time_since_epoch().count())
  , rng_(seed_)
  , result_(&result)
  , min_query_count_(min_query_count)
  , min_duration_ms_(min_duration_ms)
  , issued_query_count_(0) {
    start_time_ = std::chrono::high_resolution_clock::now();
}

LoadGen::LoadGen(std::shared_ptr<PerfResult> result, int64_t min_query_count, int64_t min_duration_ms)
  :LoadGen(*result, min_query_count, min_duration_ms) {}

std::shared_ptr<Query> LoadGen::IssueQuery() {
    auto now = std::chrono::high_resolution_clock::now();
    // use the issued time of the first query a start time.
    if (issued_query_count_ == 0) {
        start_time_ = now;
    }

    std::shared_ptr<Query> q = std::make_shared<Query>();
    q->issued_at = now;
    int64_t span = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time_).count();
    if (span >= min_duration_ms_ && issued_query_count_ >= min_query_count_) {
        q->id = -1;
        return q;
    }

    issued_query_count_++;
    q->id = (next_query_id_++);
    if (result_) {
        result_->AddQuery(q);
    }
    return q;
}

int64_t LoadGen::CountIssued() {
    return issued_query_count_;
}

double LoadGen::GetIssuedQPS() {
    auto now = std::chrono::high_resolution_clock::now();
    double lat_ms = std::chrono::duration<double, std::milli>(now - start_time_).count();
    return CountIssued() / lat_ms * 1e3;
}