# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from perftools.logger import logger
import numpy as np
import onnxruntime as ort
from perftools.server.ort_tuner import OrtTuner
from perftools.server.ort_config import OrtSession
from perftools.server.ort_runtime import OrtRuntime
from perftools.server.benchmark import Benchmark
from perftools.server.onnx_model_factory import ONNXModelFactory
import multiprocessing
from ray import tune


def tune_ort_options(model, lantency_bound_ms, percentile, init_qps=10):
    cpu_cores = multiprocessing.cpu_count()
    runtime = OrtRuntime('1.10', False)
    tuner = OrtTuner(model, runtime)   
    ret = tuner.tune_for_qps(
        lantency_bound_ms, percentile, init_qps=init_qps,
        num_cores=cpu_cores)
    return ret


if __name__ == '__main__':  
    factory = ONNXModelFactory(cache_dir='.perftools')
    models = [
        factory.create_bert('bert-base-uncased'), 
        #factory.create_bert('prajjwal1/bert-small'),
        #factory.create_bert('prajjwal1/bert-medium'),
        #factory.create_bert('bert-large-uncased'),
        #factory.create_bert('albert-base-v2'),
        #factory.create_gpt2('gpt2'),
        #factory.create_t5_encoder('t5-base')
    ]
    #latencies = [50, 100, 200, 500]
    latencies = [100]
    max_evals = 10

    reports = []
    for model in models:
        latency_percentile = 90     
        best_config = None
        for lat in latencies:
            report = {'model': model.model_name, 'latency': lat, 'percentile': latency_percentile}
            best_result = {'qps': 0}
            if not best_config:
                try:       
                    best_config, best_result = tune_ort_options(
                        model, 
                        lantency_bound_ms=lat, 
                        percentile=latency_percentile, 
                        init_qps=50)
                except Exception as e:
                    logger.warn(str(e))
            else:
                sessions = []
                for i in range(0, int(best_config['num_workers'])):
                    sess_options = ort.SessionOptions()
                    sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                    sess_options.intra_op_num_threads = best_config['num_intraop_threads']
                    runtime = OrtRuntime('1.10', False)
                    s = OrtSession(model, runtime, sess_options)
                    sessions.append(s)
                inference_calls = [s.run for s in sessions]
                perf = Benchmark(inference_calls, queries=model.inputs)
                try:
                    qps = perf.run_search_qps(latency_bound_ms=lat, 
                                              percentile=latency_percentile, 
                                              init_qps=50)
                    best_result = {'qps': qps}
                except Exception as e:
                    logger.warn(str(e))
                
                for s in sessions:
                    del s

            report['params'] = best_config
            report['qps'] = best_result['qps']
            reports.append(report)
    
    for report in reports:
        print(report)
