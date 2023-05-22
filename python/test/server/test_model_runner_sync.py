# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import time
from model_perf.server import ServerModelRunner


class SystemUnderTest:
    def __init__(self) -> None:
        pass
    
    def run(self):
        sum = 0
        for i in range(1, 10000):
            sum += i


def native_python_run():
    sut = SystemUnderTest()
    start = time.time()
    n = 10000
    for _ in range(0, n):
        sut.run()
    end = time.time()
    print((end - start) * 1000 / n)


@unittest.skip("skip")
class TestModelRunner(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = ServerModelRunner(SystemUnderTest,
                                        num_workers=8,
                                        num_threads=1,
                                        tensorboard=True)
        self.runner.start()
    
    def tearDown(self) -> None:
        self.runner.stop()
    
    def test_server_mode(self): 
        report = self.runner.benchmark(queries=[(), (), ()],
                                       target_qps=10000, min_duration_ms=120000)
        print(report)
    
    @unittest.skip("skip")  
    def test_single_stream_mode(self): 
        report = self.runner.benchmark_single_stream(
            queries=[(), (), ()], min_duration_ms=120000)
        print(report)


class SystemUnderTestWithQueries:
    def __init__(self, queries) -> None:
        self.queries = queries
    
    def run(self, query_id):
        q = self.queries[query_id % len(self.queries)]
        return q


class TestModelRunner(unittest.TestCase):
    def setUp(self) -> None:
        queries = ['a', 'b', 'c']
        self.runner = ServerModelRunner(SystemUnderTestWithQueries,
                                        num_workers=8,
                                        num_threads=1,
                                        tensorboard=True)(queries)
        self.runner.start()
    
    def tearDown(self) -> None:
        self.runner.stop()
    
    def test_server_mode(self): 
        report = self.runner.benchmark(target_qps=10000, min_duration_ms=10000)
        print(report)
    
    @unittest.skip("skip")  
    def test_single_stream_mode(self): 
        report = self.runner.benchmark_single_stream(min_duration_ms=10000)
        print(report)


if __name__ == '__main__':
    unittest.main()
    
    