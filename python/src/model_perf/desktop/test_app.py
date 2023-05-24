# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import zipfile
from ..utils import download_file


def download_testapp(release_version, inference_runtime, runtime_version, platform, cpu_arch, file_type='zip'):
    print(f'Downloading test app for {platform} {cpu_arch}')

    # normalize inference runtime name
    if inference_runtime == 'onnxruntime':
        inference_runtime = 'ort'

    # normalize inference runtime version
    runtime_version = runtime_version.replace('.', '_')

    # normalize platform
    if platform == 'windows':
        platform = 'win'

    # normalize cpu architecture
    if cpu_arch == 'win32':
        cpu_arch = 'x86'

    base_url = 'https://github.com/microsoft/model-perf/releases/download'
    url = f'{base_url}/{release_version}/{inference_runtime}_{runtime_version}_{platform}_{cpu_arch}.{file_type}'
    test_app_zip = download_file(url)

    # extract test app zip file
    if test_app_zip.name.endswith('.zip'):
        test_app_dir = test_app_zip.parent / test_app_zip.name[:-4]
        if not test_app_dir.exists():
            with zipfile.ZipFile(test_app_zip, 'r') as zip_ref:
                zip_ref.extractall(test_app_dir)
        test_app = test_app_dir / 'test_app.exe'
    else:
        test_app = test_app_zip

    return test_app


class WindowsTestApp:
    # only maintain the latest version of windows testing app to reduce package size
    ONNXRUNTIME_1_14_1_X64 = download_testapp('v0.0.1rc1', 'onnxruntime', '1.14.1', 'windows', 'x64')
    ONNXRUNTIME_1_14_1_X86 = download_testapp('v0.0.1rc1', 'onnxruntime', '1.14.1', 'windows', 'x86')
    ONNXRUNTIME_1_14_1_ARM64 = download_testapp('v0.0.1rc1', 'onnxruntime', '1.14.1', 'windows', 'arm64')
    ONNXRUNTIME_LATEST_X64 = ONNXRUNTIME_1_14_1_X64
    ONNXRUNTIME_LATEST_X86 = ONNXRUNTIME_1_14_1_X86
    ONNXRUNTIME_LATEST_ARM64 = ONNXRUNTIME_1_14_1_ARM64
