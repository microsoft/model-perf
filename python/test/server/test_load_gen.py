# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from model_perf.server.load_gen import ServerLoadGen, PerfResult


class TestLoadGen(unittest.TestCase):
    def setUp(self) -> None:
        pass
    
    def tearDown(self) -> None:
        pass
    
    @unittest.skip('')
    def test_server(self):        
        load_gen = ServerLoadGen(total_sample_count=100, target_qps=10)
        for q in load_gen.queries():
            print(f'query {q.id} {q.index} issued at {q.issued_at}')
    
    @unittest.skip('')
    def test_qps_c(self):
        perf_result = PerfResult()
        load_gen = ServerLoadGen(perf_result, total_sample_count=100, target_qps=1000, min_duration_ms=120000)
        actual_qps = load_gen.test_qps()
        print(f'actual qps {actual_qps}')
        self.assertAlmostEqual(actual_qps, 1000, delta=10)
    
    def test_qps_py(self):
        perf_result = PerfResult()
        load_gen = ServerLoadGen(perf_result, total_sample_count=100, target_qps=1000, min_duration_ms=120000)
        for q in load_gen.queries():
            pass
        actual_qps = load_gen.get_issued_qps()
        print(f'actual qps {actual_qps}')
        self.assertAlmostEqual(actual_qps, 1000, delta=10)


if __name__ == '__main__':
    unittest.main()
