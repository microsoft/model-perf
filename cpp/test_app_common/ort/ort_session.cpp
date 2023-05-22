// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include "ort_session.h"
#include "str_utils.h"
#include <fstream>
#include <iostream>

namespace model_perf {

std::shared_ptr<Ort::Env> OrtSession::ort_env;
std::shared_ptr<Ort::AllocatorWithDefaultOptions> OrtSession::ort_allocator;
std::once_flag once_flag;

void OrtSession::InitializeOrt() {
    OrtSession::ort_env = std::make_shared<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "ort");
    OrtSession::ort_allocator = std::make_shared<Ort::AllocatorWithDefaultOptions>();
}

OrtSession::OrtSession(const json& config)
  : config_(config) {
    std::call_once(once_flag, InitializeOrt);

    // get model path
    std::string model_path = config["root_dir"].get<std::string>() + "/" + config["model"]["path"].get<std::string>();

    // get input/output names of model
    input_names_str_repr_ = config["model"]["input_names"].get<std::vector<std::string>>();
    output_names_str_repr_ = config["model"]["output_names"].get<std::vector<std::string>>();
    input_names_.resize(input_names_str_repr_.size());
    output_names_.resize(output_names_str_repr_.size());
    std::transform(input_names_str_repr_.begin(), input_names_str_repr_.end(), input_names_.begin(), [](std::string& name) { return name.c_str(); });
    std::transform(output_names_str_repr_.begin(), output_names_str_repr_.end(), output_names_.begin(), [](std::string& name) { return name.c_str(); });

    session_options_ = std::make_shared<Ort::SessionOptions>();
    // Memory arena on CPU may pre-allocate memory for future usage. Set this option to false if you don't want it. Default is True.
    // session_options_->DisableCpuMemArena();
    // int intra_op_thread_num = config["intra_op_thread_num"].get<int>();
    // int inter_op_thread_num = config["inter_op_thread_num"].get<int>();
    // session_options_->SetIntraOpNumThreads(intra_op_thread_num);
    // session_options_->SetInterOpNumThreads(intra_op_thread_num);

    // load model from memory buffer. https://github.com/microsoft/onnxruntime/issues/6475
    std::shared_ptr<std::ifstream> ifs(new std::ifstream(), [](std::ifstream* s) {
        s->close();
        delete s;
    });
    std::ios_base::openmode mode = std::ios_base::in | std::ios_base::binary;
#if defined(_WIN32)
    ifs->open(str_to_wstr(model_path), mode);
#else
    ifs->open(model_path, mode);
#endif

    std::vector<char> model_buffer((std::istreambuf_iterator<char>(*ifs)), std::istreambuf_iterator<char>());
    session_.reset(new Ort::Session(*OrtSession::ort_env, model_buffer.data(), model_buffer.size(), *session_options_));
}

std::vector<Ort::Value> OrtSession::Run(const std::vector<Ort::Value>& inputs) {
    std::vector<Ort::Value> outputs = session_->Run(Ort::RunOptions(), input_names_.data(), inputs.data(), inputs.size(), output_names_.data(), output_names_.size());
    return outputs;
}

} // namespace model_perf