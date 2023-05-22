// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <iostream>

#include "logger.h"

#include "spdlog/sinks/android_sink.h"
#include "spdlog/sinks/basic_file_sink.h"
#include "spdlog/sinks/stdout_color_sinks.h"

namespace model_perf {

Logger logger;

Logger::Logger(const std::string& name,
               bool std_out,
               bool std_err,
               const std::string& file,
               bool android,
               const spdlog::level::level_enum& level,
               const std::string& format) {
    level_ = level;
    format_ = format;

    if (std_out) {
        AddStdoutSink();
    }

    if (std_err) {
        AddStderrSink();
    }

    if (file.size() > 0) {
        AddFileSink(file);
    }

    if (android) {
        AddAndroidSink();
    }

    inner_logger_ = std::make_shared<spdlog::logger>(name, sinks_.begin(), sinks_.end());
    inner_logger_->set_level(level_);
    inner_logger_->set_pattern(this->format_);
    spdlog::register_logger(inner_logger_);
}

void Logger::AddStdoutSink() {
    auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
    console_sink->set_level(level_);
    console_sink->set_pattern(this->format_);
    sinks_.push_back(console_sink);
}

void Logger::AddStderrSink() {
    auto console_sink = std::make_shared<spdlog::sinks::stderr_color_sink_mt>();
    console_sink->set_level(level_);
    console_sink->set_pattern(this->format_);
    sinks_.push_back(console_sink);
}

void Logger::AddFileSink(const std::string& file) {
    auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(file, true);
    file_sink->set_level(level_);
    file_sink->set_pattern(this->format_);
    sinks_.push_back(file_sink);
}

void Logger::AddAndroidSink() {
#ifdef __ANDROID__
    auto android_sink = std::make_shared<spdlog::sinks::android_sink_mt>();
    android_sink->set_level(level_);
    android_sink->set_pattern(this->format_);
    sinks_.push_back(android_sink);
#endif
}

void Logger::Debug(const char* msg) {
    inner_logger_->debug(msg);
}

void Logger::Info(const char* msg) {
    inner_logger_->info(msg);
}

void Logger::Warn(const char* msg) {
    inner_logger_->warn(msg);
}

void Logger::Error(const char* msg) {
    inner_logger_->error(msg);
}

void Logger::Flush() {
    inner_logger_->flush();
}

Logger Logger::GetLogger(const std::string& name) {
    auto inner_logger = spdlog::get(name);
    if (inner_logger) {
        return Logger(inner_logger);
    }
    std::cerr << "logger " + name + " is not found\n"
              << std::endl;
    throw std::runtime_error("logger " + name + " is not found\n");
}

Logger Logger::CreateSystemLogger(bool std_out,
                                  bool std_err,
                                  const std::string& file,
                                  bool android,
                                  const spdlog::level::level_enum& level,
                                  const std::string& format) {
    return Logger("model_perf", std_out, std_err, file, android, level, format);
}

void Logger::AddInstantEvent(const std::string& name, const std::string& cat, const uint64_t pid, const nlohmann::json args, bool is_last) {
    nlohmann::json event = {
        { "name", name },
        { "cat", cat },
        { "ts", std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count() },
        { "ph", "i" },
        { "pid", pid },
        { "args", args }
    };
    std::string output = event.dump();
    if (!is_last) {
        output = output + ",";
    } else {
        output = output + "]";
    }
    Info(output.c_str());
}

} // namespace model_perf
