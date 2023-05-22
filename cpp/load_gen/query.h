// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include <map>
#include <set>
#include <vector>
#include <chrono>
#include <memory>
#include <future>

struct Query {
    int64_t id;
    std::chrono::high_resolution_clock::time_point issued_at;
    std::chrono::nanoseconds latency;
    std::shared_ptr<std::promise<bool>> completed;
};
