// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT license.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include "server_load_gen.h"
#include "single_stream_load_gen.h"
#include "perf_result.h"

namespace py = pybind11;

PYBIND11_MODULE(load_gen_c, m) {

    py::class_<Query, std::shared_ptr<Query>>(m, "Query")
      .def(py::init<>())
      .def_readwrite("id", &Query::id)
      .def_readwrite("issued_at", &Query::issued_at)
      .def_readwrite("latency", &Query::latency);

    struct ServerLoadGenIterator {
        ServerLoadGenIterator(ServerLoadGen& lg)
          : lg(lg) {}

        std::shared_ptr<Query> next() {
            if (cached.size() == 0) {
                cached = lg.IssueQuery();
            }

            auto it = cached.begin();
            auto q = *it;
            cached.erase(it);

            if (q->id < 0) {
                throw py::stop_iteration();
            }
            return q;
        }

        std::list<std::shared_ptr<Query>> cached;
        ServerLoadGen& lg;
    };

    py::class_<ServerLoadGenIterator>(m, "ServerLoadGenIterator")
      .def(
        "__iter__", [](ServerLoadGenIterator& it) -> ServerLoadGenIterator& { return it; }, py::call_guard<py::gil_scoped_release>())
      .def("__next__", &ServerLoadGenIterator::next, py::call_guard<py::gil_scoped_release>());

    py::class_<ServerLoadGen, std::shared_ptr<ServerLoadGen>>(m, "ServerLoadGen")
      .def(py::init<std::shared_ptr<PerfResult> /* result */, float /* target_qps */, int64_t /* min_query_cnt = 100 */, int64_t /* min_duration_ms = 10000 */>(),
           py::arg("result"),
           py::arg("target_qps"),
           py::arg("min_query_count") = 100,
           py::arg("min_duration_ms") = 10000)
      .def(
        "issue_query",
        &ServerLoadGen::IssueQuery,
        py::return_value_policy::reference,
        py::call_guard<py::gil_scoped_release>())
      .def(
        "queries",
        [](ServerLoadGen& s) { return ServerLoadGenIterator(s); },
        py::keep_alive<0, 1>() /* Essential: keep object alive while iterator exists */)
      .def("count_issued", &ServerLoadGen::CountIssued)
      .def("get_issued_qps", &ServerLoadGen::GetIssuedQPS)
      .def(
        "test_qps",
        &ServerLoadGen::TestQPS);

    struct SingleStreamLoadGenIterator {
        SingleStreamLoadGenIterator(SingleStreamLoadGen& lg)
          : lg(lg) {}

        std::shared_ptr<Query> next() {
            std::list<std::shared_ptr<Query>> qs = lg.IssueQuery();
            std::shared_ptr<Query> q = qs.front();

            if (q->id < 0) {
                throw py::stop_iteration();
            }
            return q;
        }

        SingleStreamLoadGen& lg;
    };

    py::class_<SingleStreamLoadGenIterator>(m, "SingleStreamLoadGenIterator")
      .def(
        "__iter__", [](SingleStreamLoadGenIterator& it) -> SingleStreamLoadGenIterator& { return it; }, py::call_guard<py::gil_scoped_release>())
      .def("__next__", &SingleStreamLoadGenIterator::next, py::call_guard<py::gil_scoped_release>());

    py::class_<SingleStreamLoadGen, std::shared_ptr<SingleStreamLoadGen>>(m, "SingleStreamLoadGen")
      .def(py::init<std::shared_ptr<PerfResult> /* result */, int64_t /* min_query_cnt = 100 */, int64_t /* min_duration_ms = 10000 */>(),
           py::arg("result"),
           py::arg("min_query_count") = 100,
           py::arg("min_duration_ms") = 10000)
      .def(
        "issue_query",
        &SingleStreamLoadGen::IssueQuery,
        py::return_value_policy::reference,
        py::call_guard<py::gil_scoped_release>())
      .def(
        "queries",
        [](SingleStreamLoadGen& s) { return SingleStreamLoadGenIterator(s); },
        py::keep_alive<0, 1>() /* Essential: keep object alive while iterator exists */)
      .def("count_issued", &SingleStreamLoadGen::CountIssued)
      .def("get_issued_qps", &SingleStreamLoadGen::GetIssuedQPS);

    py::class_<PerfResult, std::shared_ptr<PerfResult>>(m, "PerfResult")
      .def(py::init<>())
      .def("add_query",
           static_cast<void (PerfResult::*)(std::shared_ptr<Query>)>(&PerfResult::AddQuery),
           py::arg("query"),
           py::call_guard<py::gil_scoped_release>())
      .def(
        "complete_query",
        static_cast<void (PerfResult::*)(int64_t, bool, float)>(&PerfResult::CompleteQuery),
        py::arg("id"),
        py::arg("error")=false,
        py::arg("latency_ms") = -1.0,
        py::call_guard<py::gil_scoped_release>())
      .def_static(
        "complete_query_args",
        []() -> std::vector<std::string> { return { "id", "error", "latency_ms" }; })
      .def(
        "get_actual_qps",
        &PerfResult::GetActualQPS)
      .def("count_succeeded", &PerfResult::CountSucceeded)
      .def("count_failed", &PerfResult::CountFailed)
      .def(
        "get_latencies",
        &PerfResult::GetLatencies,
        py::arg("percentiles"),
        py::arg("min") = true,
        py::arg("avg") = true,
        py::arg("max") = true,
        py::call_guard<py::gil_scoped_release>());
}
