# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import unittest
from pathlib import Path

import numpy

from model_perf.metrics import accuracy_score
from model_perf.mobile import AppCenterModelRunner, AVDModelRunner
from model_perf.model import ModelAssets
import platform


class TestMobile(unittest.TestCase):

    def setUp(self) -> None:
        self.root_dir = Path(__file__).parent / "../../.."
        self.android_apk_path = (self.root_dir / "test_apps/android/test_app/app/build/outputs/apk/debug/app-arm64-v8a-debug.apk").absolute()
        self.android_appium_client_path = (self.root_dir / "test_apps/android/test_driver_app/target/upload").absolute()
        self.model = ModelAssets(path=(Path(__file__).parent / "../resources/add.onnx"))
        self.ios_ipa_path = (self.root_dir / "test_apps/ios/test_app/build.ios/test_app.ipa/com.company.test_app.ipa").absolute()
        self.ios_appium_client_path = (self.root_dir / "test_apps/ios/test_driver_app/target/upload").absolute()
        

    @staticmethod
    def run_add_model_mobile(model_runner):
        inputs = [[numpy.array([[1.1, 1.1]], dtype=numpy.float32), numpy.array([[2.2, 2.2]], dtype=numpy.float32)],
                  [numpy.array([[3.3, 3.3]], dtype=numpy.float32), numpy.array([[4.4, 4.4]], dtype=numpy.float32)],
                  [numpy.array([[5.5, 5.5]], dtype=numpy.float32), numpy.array([[6.6, 6.6]], dtype=numpy.float32)]]

        predict_outputs, benchmark_outputs = model_runner.predict_and_benchmark(inputs=inputs, config={'model': {
                                                                                                       'input_names': ['x', 'y'],
                                                                                                       'output_names': ['sum']}})
        print('predict result')
        expected_outputs = [[numpy.array([[3.3, 3.3]], dtype=numpy.float32)],
                            [numpy.array([[7.7, 7.7]], dtype=numpy.float32)],
                            [numpy.array([[12.1, 12.1]], dtype=numpy.float32)]]

        for idx, output in enumerate(predict_outputs):
            print(f'predict result for device {idx}')
            print(output)
            accuracy = accuracy_score(expected_outputs, output)
            print(f"accuracy = {accuracy}")

        print('benchmark result')
        for idx, output in enumerate(benchmark_outputs):
            print(f'benchmark result for device {idx}')
            print(output)

    def test_android(self):
        owner_name = "test-owner"
        app_name = "test-app"
        device_set_name = "pixel-4a"

        model_runner = AppCenterModelRunner(model=self.model, test_app=self.android_apk_path,
                                            test_driver_app=self.android_appium_client_path,
                                            output_dir=Path(__file__).parent / 'output_test_android', 
                                            appcenter_owner=owner_name, appcenter_app=app_name, appcenter_deviceset=device_set_name)

        self.run_add_model_mobile(model_runner)

    def test_ios(self):
        owner_name = "test-owner"
        app_name = "test-app"
        device_set_name = "iphone14-16-1"
        model_runner = AppCenterModelRunner(model=self.model, test_app=self.ios_ipa_path,
                                            test_driver_app=self.ios_appium_client_path,
                                            output_dir=Path(__file__).parent / 'output_test_ios', 
                                            appcenter_owner=owner_name, appcenter_app=app_name, appcenter_deviceset=device_set_name)

        self.run_add_model_mobile(model_runner)

    def test_avd_model_runner_android(self):
        model = ModelAssets(path=(Path(__file__).parent / "../add.onnx"))
        model_runner = AVDModelRunner(model=self.model, test_app=self.android_apk_path, 
                                      test_driver_app=self.android_appium_client_path,
                                      output_dir=Path(__file__).parent / 'output_test_avd_model_runner_android',
                                      )
        self.run_add_model_mobile(model_runner)

    def test_avd_model_runner_ios(self):
        model = ModelAssets(path=(Path(__file__).parent / "../add.onnx"))
        model_runner = AVDModelRunner(model=self.model, test_app=self.ios_ipa_path, 
                                      test_driver_app=self.ios_appium_client_path,
                                      output_dir=Path(__file__).parent / 'output_test_avd_model_runner_ios',
                                      )
        self.run_add_model_mobile(model_runner)

if __name__ == '__main__':
    unittest.main()
