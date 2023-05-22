# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from perftools.model.onnx_model_factory import ONNXModelFactory
from perftools.dataset.dataset_factory import DataSetFactory
from perftools.server.ort_tuner import OrtTuner


class TestOrtTuner(unittest.TestCase):
    def test_tune_for_qps(self):
        model_factory = ONNXModelFactory(cache_dir='.perftools')
        model = model_factory.create_bert('bert-base-uncased')
        datset_factory = DataSetFactory(cache_dir='.perftools')
        dataset = datset_factory.create_bert('bert-base-uncased')
        
        tuner = OrtTuner(model, dataset.inputs)   
        best_config, best_result = tuner.tune_for_qps(
            latency_bound_ms=100, percentile=90,
            num_cores=4,
            init_qps=50)
        print((best_config, best_result))


if __name__ == '__main__':
    unittest.main()