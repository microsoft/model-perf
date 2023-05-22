# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import threading
import random
import multiprocessing
import time
import inspect
from .sync_worker import SyncWorker
from .async_worker import AsyncWorker
from .load_gen import ServerLoadGen, SingleStreamLoadGen, PerfResult
from ..logger import logger


class SystemUnderTest:
    def __init__(self) -> None:
        pass
    
    def setup(self):
        pass
    
    def run(self):
        pass
    
    def teardown(self):
        pass


'''
Note: Multiprocessing.SimpleQueue is not a choice for driver and worker communication.
Reason:
Multiprocessing.SimpleQueue is built on the top of Pipe wihtout any additioan 
Python objects buffer but only the OS pipe buffer. On Windows, Pipe has a default 
buffer size of 8KB. If there are more than 8KB of data written to the pipe 
and no data was read from the pipe, the write operation will block until data is 
read from the pipe. As a result, they are not a perfect choice for storing issued queries 
because the query issue process will block if the worker is slow at consuming queries.
See the implementation of Pipe in the Python source code:
```
# Python\Python310\Lib\multiprocessing\queues.py
class SimpleQueue(object):
    def __init__(self, *, ctx):
    self._reader, self._writer = connection.Pipe(duplex=False)
    ...

# Python\Python310\Lib\multiprocessing\connection.py
# BUFSIZE=8192
def Pipe(duplex=True):
    address = arbitrary_address('AF_PIPE')
    if duplex:
        openmode = _winapi.PIPE_ACCESS_DUPLEX
        access = _winapi.GENERIC_READ | _winapi.GENERIC_WRITE
        obsize, ibsize = BUFSIZE, BUFSIZE
    else:
        openmode = _winapi.PIPE_ACCESS_INBOUND
        access = _winapi.GENERIC_WRITE
        obsize, ibsize = 0, BUFSIZE
    ...
```
'''
class ServerModelRunner:
    def __init__(self, sut_cls,
                 async_worker=False,
                 num_workers=1, num_threads=1, num_tasks=1,               
                 tensorboard=False):
        self.sut_cls = sut_cls
        self.sut_args = ([], {})
        
        self.async_worker = async_worker
        self.num_workers = num_workers
        if self.async_worker:
            self.num_worker_concurrency = num_tasks
        else:
            self.num_worker_concurrency = num_threads       
        self.workers = []
        
        self.query_queue = multiprocessing.Queue()
        self.response_queue = multiprocessing.Queue()
        self.response_thread = None
        
        self.queries = []
        self.done = False               
        self.report = {}
        
        self.load_gen = None
        self.perf_result = None
        
        self.enable_tensorboard = tensorboard
        self.tb_logs_thread = None
    
    def __call__(self, *args, **kwds):
        self.sut_args = (args, kwds)
        return self
    
    def reset(self):
        while not self.query_queue.empty():
            self.query_queue.get()
        
        while not self.response_queue.empty():
            self.response_queue.get()
        
        if self.async_worker:
            self.report = {'num_workers': self.num_workers, 'num_tasks': self.num_worker_concurrency}
        else:
            self.report = {'num_workers': self.num_workers, 'num_threads': self.num_worker_concurrency}
        self.done = False
    
    @staticmethod
    def worker_process_callback(async_worker, 
                                sut_cls, sut_args,
                                max_concurrency, query_queue, response_queue):
        if not async_worker:
            worker = SyncWorker(sut_cls=sut_cls, num_threads=max_concurrency,
                                query_queue=query_queue, response_queue=response_queue)(*sut_args[0], **sut_args[1])
        else:
            worker = AsyncWorker(sut_cls=sut_cls, num_tasks=max_concurrency, 
                                 query_queue=query_queue, response_queue=response_queue)(*sut_args[0], **sut_args[1])
        worker.start()
        worker.join()   
    
    def start(self):
        for _ in range(self.num_workers):
            worker = multiprocessing.Process(target=ServerModelRunner.worker_process_callback,
                                             args=(self.async_worker, 
                                                   self.sut_cls, self.sut_args,
                                                   self.num_worker_concurrency, self.query_queue, self.response_queue))
            self.workers.append(worker)
            worker.start()

        # wait sut to be ready for processing queries.
        num_ready = 0
        if self.async_worker:
            total_threads = self.num_workers
        else:
            total_threads = self.num_workers * self.num_worker_concurrency
        while num_ready < total_threads:
            self.response_queue.get()
            num_ready += 1
            if self.async_worker:
                logger.info(f'{num_ready} out of {total_threads} total async workers are ready, max concurrent tasks of each worker is {self.num_worker_concurrency}')               
            else:
                logger.info(f'{num_ready} out of {total_threads} total sync worker threads are ready')
              
        self.response_thread = threading.Thread(target=self.response_received_callback)
        self.response_thread.start()
        
        if self.enable_tensorboard:
            self.tb_logs_thread = threading.Thread(target=self.write_tensorboard_logs)
            self.tb_logs_thread.start()
    
    def response_received_callback(self):
        while True:
            query_sample_id, perf_response = self.response_queue.get()
            #logger.debug(f'receive response {query_sample_id}')
            if query_sample_id is None:
                break
            perf_response = {k: v for k, v in perf_response.items() if k in self.perf_result.complete_query_args()}          
            self.perf_result.complete_query(query_sample_id, **perf_response)       
        logger.info(f'stop receiving responses') 
        
    def stop(self):
        self.query_queue.put((None, None))     
        for mp_worker in self.workers:
            mp_worker.join()
        self.response_queue.put((None, None))
        self.response_thread.join()
        self.done = True
        logger.info(f'all {self.num_workers} workers are terminated')
        
        if self.enable_tensorboard:
            self.tb_logs_thread.join()
            logger.info(f'tensorboard logs thread is terminated')

    def benchmark(self, queries=None, target_qps=1, min_query_count=100, min_duration_ms=30000):
        self.reset()
        self.queries = queries
        if self.queries is None:
            logger.info(f'no queries are provided. then `SUT::predict(query_id: int)` should accept a query id and generate final model inputs itself. this is to avoid cost of query serilization/deserilization between ServerModelRunner and workers.')
        self.report['mode'] = 'server'
        self.report['qps/target'] = target_qps
        
        self.perf_result = PerfResult()
        logger.info(f'`SUT::predict` could return the following metrics in a dict to override default behaviors: {self.perf_result.complete_query_args()}')
        self.load_gen = ServerLoadGen(result=self.perf_result,
                                      target_qps=target_qps, 
                                      min_query_count=min_query_count,
                                      min_duration_ms=min_duration_ms)
                
        for q in self.load_gen.queries():         
            #self.perf_result.add_query(q)
            #self.perf_result.complete_query(q.id)          
            if self.queries is not None:
                self.query_queue.put((q.id, random.choice(self.queries)))         
            else:
                self.query_queue.put((q.id, None))
            pass
        
        logger.info(f'issued all queries')
        return self.get_report()
    
    def benchmark_single_stream(self, queries=None, min_query_count=100, min_duration_ms=30000):
        self.reset()
        self.queries = queries
        if self.queries is None:
            logger.info(f'no queries are provided. then `SUT::predict(query_id: int)` should accept a query id and generate final model inputs itself. serilization/deserilization of queries between ServerModelRunner and workers could be avoided.')
        self.report['mode'] = 'single_stream'
        
        self.perf_result = PerfResult()
        self.load_gen = SingleStreamLoadGen(result=self.perf_result,
                                            min_query_count=min_query_count,
                                            min_duration_ms=min_duration_ms)
                
        for q in self.load_gen.queries():         
            #self.perf_result.add_query(q)
            #self.perf_result.complete_query(q.id) 
            if self.queries is not None:
                self.query_queue.put((q.id, random.choice(self.queries)))         
            else:
                self.query_queue.put((q.id, None))
            pass
        
        logger.info(f'issued all queries')
        return self.get_report()
    
    def get_latencies(self):
        percentiles = [0.5, 0.9, 0.95, 0.97, 0.99, 0.999]
        latencies = self.perf_result.get_latencies(percentiles=percentiles, 
                                                   min=True, avg=True, max=True)
        if len(latencies) == 0:
            return {}
        
        res = {'latency/min':latencies[-3], 'latency/avg':latencies[-2], 'latency/max': latencies[-1]}
        for i, p in enumerate(percentiles):
            res[f'latency/p{int(p*100)}'] = latencies[i]
        for k in res.keys():
            res[k] = round(res[k], 3)
        return res
    
    def get_actual_qps(self):
        return self.perf_result.get_actual_qps()

    def get_report(self):
        return {**self.report, 
                'qps/issued': self.load_gen.get_issued_qps(), 
                'qps/actual':self.get_actual_qps(),
                '#queries/issued': self.load_gen.count_issued(),
                '#queries/succeeded': self.perf_result.count_succeeded(),
                '#queries/failed': self.perf_result.count_failed(),
                **self.get_latencies()}

    def get_tensorboard_scalars(self):
        legends = ['qps/issued', 'qps/actual', 'qps/target', 
                   "#queries/succeeded", "#queries/failed", "#queries/issued"]
        legends += [f"latency/p{int(p*100)}" for p in [0.5, 0.9, 0.95, 0.97, 0.99, 0.999]]
        legends += ['latency/min', 'latency/avg', 'latency/max']
        return legends

    def write_tensorboard_logs(self):
        try:
            from torch.utils.tensorboard import SummaryWriter
            logger.info(f'Run `tensorboard.exe --log-dir=runs` to visualize realtime performance results in TensorBoard.')
        except:
            logger.warning(f'TensorBoard support is enabled. But required packages are missing. Run `pip install torch tensorboard` to install them.')
            return

        figures = set([x.split('/')[0] for x in self.get_tensorboard_scalars()])
        layout = {f:["Multiline", []] for f in figures}
        for l in self.get_tensorboard_scalars():
            f = l.split('/')[0]
            layout[f][1].append(l)
        category = "Model Performance Results"      
        layout = {category: layout}
        wait_secs = 10
        writer = SummaryWriter(flush_secs=wait_secs)
        writer.add_custom_scalars(layout)
      
        step = 0
        while True:
            if self.done:
                break       
            report = self.get_report()
            logger.info(report)
            for k, v in report.items():
                if k.split('/')[0] in layout[category]:
                    writer.add_scalar(k, v, step)                             
            time.sleep(wait_secs)
            step += 1     
        writer.close()
    
    # This function is copied from legacy code. In the future, if we need this 
    # function, we should refactor it.
    def search_qps(self, queries,
                       latency_bound_ms=100, percentile=90, 
                       init_qps=10, min_duration_ms=10000,
                       log_dir='.'):
        logger.info(f'running in server mode, searching for max qps given P{percentile} latency is {latency_bound_ms}ms')

        self.report['latency_bound_ms'] = latency_bound_ms
        self.report['percentile'] = percentile
        eps = 0.05
        self.run_server_mode(queries=queries, target_qps=init_qps, min_duration_ms=min_duration_ms)
        latencies = self.parse_latency_result()
        start_latency = latencies[f'p{percentile}']
        message = {'target_qps': init_qps, 'latency': latencies}
        logger.info(message) 
        if abs(start_latency - latency_bound_ms) / latency_bound_ms < eps: # stop when we are very close
            logger.info(self.get_report())
            return init_qps
      
        if start_latency < latency_bound_ms:
            target_qps, last_latency = init_qps, start_latency         
            while last_latency < latency_bound_ms:
                left = target_qps
                target_qps *= 2
                self.run_server_mode(queries=queries, target_qps=target_qps, min_duration_ms=min_duration_ms, log_dir=log_dir)
                latencies = self.parse_latency_result()
                last_latency = latencies[f'p{percentile}']
                message = {'target_qps': target_qps, 'latency': latencies}
                logger.info(message)
            right = target_qps
        else:
            target_qps, last_latency = init_qps, start_latency
            while last_latency > latency_bound_ms:
                right = target_qps
                target_qps /= 2
                self.run_server_mode(queries=queries, target_qps=target_qps, min_duration_ms=min_duration_ms, log_dir=log_dir)
                latencies = self.parse_latency_result()
                cur_latency = latencies[f'p{percentile}']
                message = {'target_qps': target_qps, 'latency': latencies}
                logger.info(message)
                if abs(cur_latency - latency_bound_ms) / latency_bound_ms < eps: # stop when we are very close
                    return target_qps
                if abs(last_latency - cur_latency) / last_latency < eps:
                    raise RuntimeError(f'failed to search a feasible target qps, may be the p{percentile} latency of {latency_bound_ms} ms is unreachable')
                last_latency = cur_latency
            left = target_qps
        
        target_qps = (left + right) / 2
        while left < right and abs(right - left) / left > 0.01:
            self.run_server_mode(queries=queries, target_qps=target_qps, min_duration_ms=min_duration_ms, log_dir=log_dir)
            latencies = self.parse_latency_result()
            cur_latency = latencies[f'p{percentile}']
            message = {'target_qps': target_qps, 'latency': latencies}
            logger.info(message)
            if abs(cur_latency - latency_bound_ms) / latency_bound_ms < eps:
                logger.info(self.get_report())
                return target_qps
            
            if cur_latency < latency_bound_ms:
                left = target_qps
            else:
                right = target_qps           
            target_qps = (left + right) / 2
        
        logger.info(self.get_report())
        return target_qps
        #raise RuntimeError(f'failed to search for the target qps, may be the p{percentile} latency of {latency_bound_ms} ms is unreachable')

if __name__ == '__main__':
    pass