# Model Performance Toolkit

Model Performance Toolkit (model-perf) is a Python package to benchmark machine learning models running on target servers or devices.

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

if __name__ == "__main__":

    # model runner to run model on server
    model_runner = ServerModelRunner(SystemUnderTest, 
                                     num_workers=8, # each worker is a standalone process
                                     num_threads=1, # threads per worker
                                     tensorboard=False)

    # start server model runner
    model_runner.start()
    report = model_runner.benchmark(queries=[(), (), ()], 
                                    target_qps=10000, 
                                    min_duration_ms=120000)
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
