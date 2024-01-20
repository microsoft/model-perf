# Model Performance Toolkit

Model Performance Toolkit (model-perf) is a Python package backed by test applications for different platforms (Windows/MacOS, Android/iOS, Web) to benchmark machine learning models on different target platforms and devices (e.g., Google Pixel for Android, iPhone for iOS).

## Installation

Install from Pip

```bash
python -m pip install model-perf --upgrade
```

Build and Install from Source _(for developers)_

```bash
git clone https://github.com/microsoft/model-perf.git

# We suggest don't use conda, please use native python.
python -m pip install --upgrade aiohttp[speedups] build mypy pip setuptools twine virtualenv wheel

# Pay attention to the auto-detected Python intepretor path in log. If it is wrong, specify the Python version to help detect the right one.
# Linux
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Windows
cmake -S . -B build -A x64
cmake --build build --config RelWithDebInfo
```

## Example
### Run Android Benchmark
```python
from model_perf.metrics import accuracy_score
from model_perf.mobile import AppCenterModelRunner
from model_perf.model import ModelAssets

# model runner to run model on android devices
model_runner = AppCenterModelRunner(model=ModelAssets(path='./add.onnx'),
                                    test_app='./test_apps/android/test_app/app-arm64-v8a-debug.apk',
                                    test_driver_app='./test_apps/android/test_driver_app/target/upload',
                                    output_dir='output_test_android',
                                    appcenter_owner='test-owner',
                                    appcenter_app='test-app',
                                    appcenter_deviceset='pixel-4a')

# inputs of model
inputs = [[numpy.array([[1.1, 1.1]], dtype=numpy.float32), numpy.array([[2.2, 2.2]], dtype=numpy.float32)],
          [numpy.array([[3.3, 3.3]], dtype=numpy.float32), numpy.array([[4.4, 4.4]], dtype=numpy.float32)],
          [numpy.array([[5.5, 5.5]], dtype=numpy.float32), numpy.array([[6.6, 6.6]], dtype=numpy.float32)]]

# predict and benchmark
predict_outputs, benchmark_outputs = model_runner.predict_and_benchmark(inputs=inputs,
                                                                        config={'model': {'input_names': ['x', 'y'], 'output_names': ['sum']}})

# expected outputs of model
expected_outputs = [[numpy.array([[3.3, 3.3]], dtype=numpy.float32)],
                    [numpy.array([[7.7, 7.7]], dtype=numpy.float32)],
                    [numpy.array([[12.1, 12.1]], dtype=numpy.float32)]]

# calculate accuracy
accuracy = accuracy_score(expected_outputs, predict_outputs[0])
print(f"accuracy = {accuracy}")

# print benchmark outputs
print(benchmark_outputs[0])
```

### Run Server Benchmark
```python
from model_perf.server import ServerModelRunner

# the system under test
class SystemUnderTest:
    def __init__(self) -> None:
        pass

    def run(self):
        sum = 0
        for i in range(1, 10000):
            sum += i

# model runner to run model on server
model_runner = ServerModelRunner(SystemUnderTest, num_workers=8, num_threads=1, tensorboard=True)

# start server model runner
model_runner.start()
report = model_runner.benchmark(queries=[(), (), ()], target_qps=10000, min_duration_ms=120000)
model_runner.stop()

# print benchmark report
print(report)
```


## Build the Docs

Run the following commands and open ``docs/_build/html/index.html`` in browser.

```bash
python -m pip install sphinx myst-parser sphinx-rtd-theme sphinxemoji
cd docs/

make html         # for linux
.\make.bat html   # for windows
```


## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
