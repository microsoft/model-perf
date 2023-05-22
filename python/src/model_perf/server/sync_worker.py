# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import threading
import multiprocessing
from .worker import Worker
from ..logger import logger


class SyncWorker(Worker):
    def __init__(self, sut_cls, query_queue, response_queue, num_threads=1):
        super().__init__(sut_cls, query_queue, response_queue)
        self.num_threads = num_threads
        self.worker_threads = []

    def thread_callback(self):
        # notify the main thread that the thread is ready for processing
        self.response_queue.put((None, 'model created', None))
        inference_call = getattr(self.sut_obj, self.infer_call)
        while True:          
            query_sample_id, query = self.query_queue.get()
            if query is None:
                query = (query_sample_id,)
            if query_sample_id is None:
                self.query_queue.put((query_sample_id, query))
                break
            response = {'error': False}
            try:              
                result = inference_call(*query)
                if result is dict:
                    response.update(result)
            except Exception as e:
                response['error'] = True              
                logger.warning(f'error happened during processing query {query_sample_id} {query}', exc_info=e)
            self.response_queue.put((query_sample_id, response))             
    
    def start(self):
        pid = multiprocessing.current_process().pid
        tid = threading.get_ident()       
        self.sut_obj = self.sut_cls(*self.sut_args[0], **self.sut_args[1])         
        if self.setup_call is not None:
            getattr(self.sut_obj, self.setup_call)()         
        logger.info(f'sut {self.sut_obj} is hosted in process {pid} thread {tid} worker {self}')
        for _ in range(self.num_threads):
            worker_thread = threading.Thread(target=self.thread_callback)
            self.worker_threads.append(worker_thread)
            worker_thread.start()
        
    def join(self):   
        for th in self.worker_threads:
            th.join()
        logger.info(f'worker {self} is terminated')
        
        if self.teardown_call is not None:
            getattr(self.sut_obj, self.teardown_call)()   


if __name__ == '__main__':
    pass