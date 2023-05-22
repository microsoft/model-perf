# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from model_perf.server import ServerModelRunner

class SystemUnderTest:
    def __init__(self) -> None:
        pass
    
    def run(self):
        sum = 0
        for i in range(1, 10000):
            sum += i
        return None

runner = ServerModelRunner(SystemUnderTest, 
                           num_workers=1,
                           max_concurrency=1,
                           tensorboard=True)
runner.start()
report = runner.benchmark(queries=[()],
                          target_qps=1000,
                          min_duration_ms=120000)
print(report)
runner.stop()
