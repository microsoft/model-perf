# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import unittest
from pathlib import Path

import numpy

from model_perf import metrics
from model_perf.dataset.msgpack_helper import deserialize_dataset
from model_perf.desktop import DesktopModelRunner, WindowsTestApp
from model_perf.model.model_assets import ModelAssets


class TestDesktopModelRunner(unittest.TestCase):

    def setUp(self) -> None:
        self.add_model_path = os.path.join(os.path.dirname(__file__), '../resources/add.onnx')
        self.greater_model_path = os.path.join(os.path.dirname(__file__), '../resources/greater.onnx')
        self.identity_model_path = os.path.join(os.path.dirname(__file__), '../resources/identity.onnx')

    @staticmethod
    def run_add_model_with_test_app(model_path, test_app_path, output_path):
        onnx_model = ModelAssets(path=model_path)
        model_runner = DesktopModelRunner(model=onnx_model, test_app=test_app_path, output_dir=output_path)

        inputs = [[numpy.array([[1.1, 1.1]], dtype=numpy.float32), numpy.array([[2.2, 2.2]], dtype=numpy.float32)],
                  [numpy.array([[3.3, 3.3]], dtype=numpy.float32), numpy.array([[4.4, 4.4]], dtype=numpy.float32)],
                  [numpy.array([[5.5, 5.5]], dtype=numpy.float32), numpy.array([[6.6, 6.6]], dtype=numpy.float32)]]

        # there is only 1 output from 1 device
        predicted_outputs, benchmark_outputs = model_runner.predict_and_benchmark(inputs=inputs,
                                                                                  config={'model': {
                                                                                      'input_names': ['x', 'y'],
                                                                                      'output_names': ['sum']}})

        expected_outputs = [[numpy.array([[3.3, 3.3]], dtype=numpy.float32)],
                            [numpy.array([[7.7, 7.7]], dtype=numpy.float32)],
                            [numpy.array([[12.1, 12.1]], dtype=numpy.float32)]]

        # accuracy
        print(predicted_outputs)
        accuracy = metrics.accuracy_score(expected_outputs, predicted_outputs[0]["model_outputs"], equal_function=None)
        print(accuracy)

        # performance
        print(benchmark_outputs)

    @staticmethod
    def run_greater_model_with_test_app(model_path, test_app_path, output_path):
        onnx_model = ModelAssets(path=model_path)
        model_runner = DesktopModelRunner(model=onnx_model, test_app=test_app_path, output_dir=output_path)

        inputs = [[numpy.array([[1.0, 1.0]], dtype=numpy.float32), numpy.array([[4.0, 2.0]], dtype=numpy.float32)]]

        # there is only 1 output from 1 device
        predicted_outputs, benchmark_outputs = model_runner.predict_and_benchmark(inputs=inputs,
                                                                                  config={'model': {
                                                                                      'input_names': ['x', 'y'],
                                                                                      'output_names': ['greater']}})

        expected_outputs = [[numpy.array([[False, False]], dtype=numpy.bool_)]]

        # accuracy
        print(predicted_outputs)
        accuracy = metrics.accuracy_score(expected_outputs, predicted_outputs[0]["model_outputs"], equal_function=None)
        print(accuracy)

        # performance
        print(benchmark_outputs)

    @staticmethod
    def run_identity_model_with_test_app(model_path, test_app_path, output_path):
        onnx_model = ModelAssets(path=model_path)
        model_runner = DesktopModelRunner(model=onnx_model, test_app=test_app_path, output_dir=output_path)

        inputs = [[numpy.array([[False, True]], dtype=numpy.bool_)]]

        # there is only 1 output from 1 device
        predicted_outputs, benchmark_outputs = model_runner.predict_and_benchmark(inputs=inputs,
                                                                                  config={'model': {
                                                                                      'input_names': ['z'],
                                                                                      'output_names': ['identity']}})

        expected_outputs = [[numpy.array([[False, True]], dtype=numpy.bool_)]]

        # accuracy
        print(predicted_outputs)
        accuracy = metrics.accuracy_score(expected_outputs, predicted_outputs[0]["model_outputs"], equal_function=None)
        print(accuracy)

        # performance
        print(benchmark_outputs)

    def test_greater_model_with_win_x64_app(self):
        self.run_greater_model_with_test_app(self.greater_model_path, WindowsTestApp.ONNXRUNTIME_LATEST_X64, './output_greater')

    def test_identity_model_with_win_x64_app(self):
        self.run_identity_model_with_test_app(self.identity_model_path, WindowsTestApp.ONNXRUNTIME_1_14_1_X64, './output_identity')

    def test_add_model_with_win_x86_app(self):
        self.run_add_model_with_test_app(self.add_model_path, WindowsTestApp.ONNXRUNTIME_LATEST_X86, './output_add')

    @unittest.skip('ignore')
    def test_deserialize_inputs(self):
        inputs_path = Path(__file__).parent / "output/data/model_inputs.msgpack"
        model_inputs = deserialize_dataset(inputs_path)
        print(model_inputs)


if __name__ == "__main__":
    unittest.main()
