// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <iostream>
#include "perf_result.h"

bool set_cmp(const Query& a, const Query& b) {
    return a.latency < b.latency;
}

PerfResult::PerfResult()
  : num_queries_(0)
  , num_succeeded_queries_(0)
  , num_failed_queries_(0)
  , succeeded_queries_sorted_(PerfResult::set_cmp)
  , total_latency_ns_(0) {
    start_time_ = std::chrono::high_resolution_clock::now();
}

void PerfResult::AddQuery(int64_t id) {
    std::shared_ptr<Query> q = std::make_shared<Query>();
    q->id = id;
    q->issued_at = std::chrono::high_resolution_clock::now();
    AddQuery(q);
}

void PerfResult::AddQuery(std::shared_ptr<Query> q) {
    std::lock_guard<std::mutex> guard(lock_);

    pending_queries_[q->id] = q;
    if (num_queries_ == 0) {
        start_time_ = q->issued_at;
    } else if (q->issued_at < start_time_){
        start_time_ = q->issued_at;
    }

    num_queries_ += 1;
}

void PerfResult::CompleteQuery(int64_t id, bool error, float latency_ms) {
    std::lock_guard<std::mutex> guard(lock_);

    // if id not found, then the query might be issued by previous runs.
    // we choose to ignore it instead of reporting an error.
    auto ite = pending_queries_.find(id);
    if (ite == pending_queries_.end()) {
        // throw std::runtime_error("PerfResult::CompleteQuery: query not found");
        return;
    }

    std::shared_ptr<Query> q = ite->second;
    if (latency_ms >= 0) {
        q->latency = std::chrono::nanoseconds(int64_t(latency_ms * 1e6));
    } else {
        q->latency = std::chrono::high_resolution_clock::now() - q->issued_at;
    }

    if (error) {
        failed_queries_.push_back(q);
        num_failed_queries_ += 1;
    } else {
        succeeded_queries_buffer_.push_back(q);
        num_succeeded_queries_ += 1;
        total_latency_ns_ += q->latency;
    }

    pending_queries_.erase(id);

    // If someone created the promise and wait for the completion, we should set its value and notify.
    if (q->completed) {
        q->completed->set_value(true);
    }
}

double PerfResult::GetActualQPS() {
    std::chrono::duration<double, std::milli> fp_ms = std::chrono::high_resolution_clock::now() - start_time_;
    int64_t total_completed = CountSucceeded();
    return total_completed / fp_ms.count() * 1e3;
}

int64_t PerfResult::CountSucceeded() {
    return num_succeeded_queries_;
}

int64_t PerfResult::CountFailed() {
    return num_failed_queries_;
}

std::vector<double> PerfResult::GetLatencies(std::vector<double> percentiles, bool min, bool avg, bool max) {
    std::list<std::shared_ptr<Query>> succeeded_queries_buffer1;
    {
        std::lock_guard<std::mutex> guard(lock_);
        succeeded_queries_buffer1.swap(succeeded_queries_buffer_);
    }

    for (auto& q : succeeded_queries_buffer1) {
        succeeded_queries_sorted_.insert(q);
    }

    std::vector<double> res;
    int64_t size = static_cast<int64_t>(succeeded_queries_sorted_.size());
    // std::cout << "num_completed_queries: " << size << " total: " << num_queries_ << std::endl;
    if (size == 0) {
        return res;
    }

    for (double p : percentiles) {
        int64_t idx = int64_t(size * p);
        if (idx >= size) {
            idx = size - 1;
        }
        if (idx < 0) {
            idx = 0;
        }

        auto it = succeeded_queries_sorted_.begin();
        std::advance(it, idx);

        const std::shared_ptr<Query>& q = *it;
        double latency_ms = std::chrono::duration<double, std::milli>(q->latency).count();
        res.push_back(latency_ms);
    }

    if (min) {
        const auto& q = *succeeded_queries_sorted_.begin();
        res.push_back(std::chrono::duration<double, std::milli>(q->latency).count());
    }

    if (avg) {
        double latency_ms = std::chrono::duration<double, std::milli>(total_latency_ns_).count();
        res.push_back(latency_ms / size);
    }

    if (max) {
        const auto& q = *succeeded_queries_sorted_.rbegin();
        res.push_back(std::chrono::duration<double, std::milli>(q->latency).count());
    }

    return res;
}
