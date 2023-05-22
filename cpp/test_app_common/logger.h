// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#include "nlohmann/json.hpp"
#include "spdlog/spdlog.h"
#include <vector>

namespace model_perf {

class Logger {
  public:
    explicit Logger(
      const std::string& name,
      bool std_out = false,
      bool std_err = false,
      const std::string& file = "",
      bool android = false,
      const spdlog::level::level_enum& level = spdlog::level::level_enum::info,
      const std::string& format = "[%Y-%m-%d %H:%M:%S.%e] [%n] [%^%l%$] [%t] %v");

    Logger() {}
    Logger(std::shared_ptr<spdlog::logger> inner_logger)
      : inner_logger_(inner_logger) {}

    template<typename... Rest>
    void Debug(const char* fmt, const Rest&... rest) {
        inner_logger_->debug(fmt, rest...);
    }

    template<typename... Rest>
    void Info(const char* fmt, const Rest&... rest) {
        inner_logger_->info(fmt, rest...);
    }

    template<typename... Rest>
    void Warn(const char* fmt, const Rest&... rest) {
        inner_logger_->warn(fmt, rest...);
    }

    template<typename... Rest>
    void Error(const char* fmt, const Rest&... rest) {
        inner_logger_->error(fmt, rest...);
    }

    void Debug(const char* msg);
    void Info(const char* msg);
    void Warn(const char* msg);
    void Error(const char* msg);
    void Flush();

    static Logger GetLogger(const std::string& name = "model_perf");

    void AddInstantEvent(const std::string& name, const std::string& cat, const uint64_t pid, const nlohmann::json args, bool is_last = false);
    static Logger CreateSystemLogger(
      bool std_out = false,
      bool std_err = false,
      const std::string& file = "",
      bool android = false,
      const spdlog::level::level_enum& level = spdlog::level::level_enum::info,
      const std::string& format = "[%Y-%m-%d %H:%M:%S.%e] [%n] [%^%l%$] [%t] %v");

    void AddAndroidSink();
    void AddStdoutSink();
    void AddStderrSink();
    void AddFileSink(const std::string& file);

  private:
    std::string format_;
    std::vector<std::shared_ptr<spdlog::sinks::sink>> sinks_;
    std::shared_ptr<spdlog::logger> inner_logger_;
    spdlog::level::level_enum level_;
};

} // namespace model_perf