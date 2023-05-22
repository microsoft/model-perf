# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import threading
import time
import onnxruntime as ort
from perftools.server.ort_runtime import OrtRuntime
from perftools.server.ort_config import OrtSession
from perftools.server.onnx_model_factory import ONNXModelFactory


if __name__ == '__main__':
    time.sleep(3)
    
    sess_options = ort.SessionOptions()
    sess_options.execution_mode = ort.ExecutionMode.ORT_PARALLEL
    sess_options.inter_op_num_threads = 4
    sess_options.intra_op_num_threads = 4
    session = ort.InferenceSession('.perftools/t5-base/model.onnx', sess_options, providers=['CPUExecutionProvider'])

    time.sleep(10)