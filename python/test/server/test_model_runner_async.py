# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import aiohttp
from model_perf.server import ServerModelRunner


class SystemUnderTest:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=32, verify_ssl=False))
    
    async def run(self):
        response = await self.session.get('http://www.google.com', timeout=5)
        #print("Status:", response.status)
        html = await response.text()
        
    async def start(self):
        pass


class TestModelRunner(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = ServerModelRunner(SystemUnderTest,
                                        async_worker=True,
                                        num_workers=1,
                                        num_tasks=32,                              
                                        tensorboard=True)
        self.runner.start()

    def tearDown(self) -> None:
        self.runner.stop()
    
    def test_server_mode(self): 
        report = self.runner.benchmark(queries=[(), (), ()],
                                       target_qps=2,
                                       min_duration_ms=10000)
        print(report)


if __name__ == '__main__':
    unittest.main()
