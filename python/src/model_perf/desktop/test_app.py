# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import tempfile

from ..utils import download_file


def download_testapp(inference_runtime, runtime_version, platform, cpu_arch):
    print(f'Downloading test app for {platform} {cpu_arch}')
    # to-do, replace the url here with real link from GitHub
    runtime_version = runtime_version.replace('.', '_')
    if platform == 'windows':
        platform = 'win'
    url = f'https://{inference_runtime}_{runtime_version}_{platform}_{cpu_arch}.zip'
    test_app = download_file(url, './test_app')
    return test_app


class WindowsTestApp:
    # only maintain the latest version of windows testing app to reduce package size
    ONNXRUNTIME_1_14_1_x64 = ''  # download_testapp('ort', '1.14.1', 'windows', 'x64')
    ONNXRUNTIME_1_14_1_x86 = ''  # download_testapp('ort', '1.14.1', 'windows', 'x86')
    ONNXRUNTIME_LATEST_x64 = ONNXRUNTIME_1_14_1_x64
    ONNXRUNTIME_LATEST_x86 = ONNXRUNTIME_1_14_1_x86
