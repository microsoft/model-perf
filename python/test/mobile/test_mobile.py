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

    def setUp(self):
        self.root_dir = Path(__file__).parent / "../../.."
        self.android_apk_path = (self.root_dir / "test_apps/android/test_app/app/build/outputs/apk/release/app-arm64-v8a-release.apk").absolute()
        self.android_appium_client_path = (self.root_dir / "test_apps/android/test_driver_app/target/upload").absolute()
        self.model = ModelAssets(path=(Path(__file__).parent / "../resources/add.onnx"))
        self.ios_ipa_path = (self.root_dir / "test_apps/ios/test_app/build.ios/test_app.ipa/com.company.test_app.ipa").absolute()
        self.ios_appium_client_path = (self.root_dir / "test_apps/ios/test_driver_app/target/upload").absolute()
        
        self.ios_appcenter_owner = os.getenv("IOS_APPCENTER_OWNER") or ''
        self.ios_appcenter_app = os.getenv("IOS_APPCENTER_APP") or ''
        self.android_appcenter_owner = os.getenv("ANDROID_APPCENTER_OWNER") or ''
        self.android_appcenter_app = os.getenv("ANDROID_APPCENTER_APP") or ''

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

    @unittest.skipUnless(platform.system().lower() == 'windows', "")
    def test_android(self):
        device_set_name = "pixel-4a"
        model_runner = AppCenterModelRunner(model=self.model, test_app=self.android_apk_path,
                                            test_driver_app=self.android_appium_client_path,
                                            output_dir=Path(__file__).parent / 'output_test_android', 
                                            appcenter_owner=self.android_appcenter_owner, appcenter_app=self.android_appcenter_app, appcenter_deviceset=device_set_name)

        self.run_add_model_mobile(model_runner)

    @unittest.skipUnless(platform.system().lower() == 'darwin', "")
    def test_ios(self):
        device_set_name = "iphone14-16-1"
        model_runner = AppCenterModelRunner(model=self.model, test_app=self.ios_ipa_path,
                                            test_driver_app=self.ios_appium_client_path,
                                            output_dir=Path(__file__).parent / 'output_test_ios', 
                                            appcenter_owner=self.ios_appcenter_owner, appcenter_app=self.ios_appcenter_app, appcenter_deviceset=device_set_name)

        self.run_add_model_mobile(model_runner)

    @unittest.skip('ignore')
    def test_avd_model_runner_android(self):
        model_runner = AVDModelRunner(model=self.model, test_app=self.android_apk_path, 
                                      test_driver_app=self.android_appium_client_path,
                                      output_dir=Path(__file__).parent / 'output_test_avd_model_runner_android',
                                      )
        self.run_add_model_mobile(model_runner)

    @unittest.skip('ignore')
    def test_avd_model_runner_ios(self):
        model_runner = AVDModelRunner(model=self.model, test_app=self.ios_ipa_path, 
                                      test_driver_app=self.ios_appium_client_path,
                                      output_dir=Path(__file__).parent / 'output_test_avd_model_runner_ios',
                                      )
        self.run_add_model_mobile(model_runner)

if __name__ == '__main__':
    unittest.main()
