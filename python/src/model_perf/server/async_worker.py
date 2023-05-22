# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import threading
import multiprocessing
import asyncio
from .worker import Worker
from ..logger import logger


class AsyncWorker(Worker):
    def __init__(self, sut_cls, query_queue, response_queue, num_tasks=100):
        super().__init__(sut_cls, query_queue, response_queue)
        self.num_tasks = num_tasks
        self.event_loop = asyncio.get_event_loop()
        
    def start(self):
        running_tasks = set()
        pid = multiprocessing.current_process().pid
        tid = threading.get_ident()
        
        self.sut_obj = self.sut_cls(*self.sut_args[0], **self.sut_args[1])    
        if self.setup_call is not None:
            f = getattr(self.sut_obj, self.setup_call)
            if asyncio.iscoroutinefunction(f):
                self.event_loop.run_until_complete(f())
            else:
                f()
            
        logger.info(f'sut {self.sut_obj} is hosted in process {pid} thread {tid} worker {self}')
        # notify the main thread that the sut is ready
        self.response_queue.put((None, 'model created', None))
        inference_call = getattr(self.sut_obj, self.infer_call)
        should_stop = False
        while True:
            try:              
                while len(running_tasks) < self.num_tasks and not self.query_queue.empty():
                    query_sample_id, query = self.query_queue.get()
                    if query is None:
                        query = (query_sample_id,)
                    if query_sample_id is None:
                        self.query_queue.put((query_sample_id, query))
                        should_stop = True
                        break
                    new_task = self.event_loop.create_task(inference_call(*query), name=query_sample_id)
                    running_tasks.add(new_task)
                
                if should_stop:
                    for task in running_tasks:
                        task.cancel()
                    self.event_loop.stop()
                    break
                
                if len(running_tasks) == 0:
                    self.event_loop.run_until_complete(asyncio.sleep(0.1))
                    continue
                                   
                finished, unfinished = self.event_loop.run_until_complete(
                    asyncio.wait(running_tasks, return_when=asyncio.FIRST_COMPLETED, timeout=0.1))      
                for task in finished:                   
                    query_id = int(task.get_name())                        
                    # If no unhandled exception was raised in the wrapped coroutine,
                    # then a value of None is returned. Otherwise, exception is 
                    # re-raised when calling the result() method and need to be handled.
                    exception = task.exception()
                    response = {'error': False}
                    if exception is not None:
                        response['error'] = True
                        logger.warning(f'error happened during processing query {query_id} {query}', exc_info=exception)
                    else:
                        task_result = task.result()
                        if task_result is dict:
                            response.update(task_result)
                    self.response_queue.put((query_id, response)) #(query_id, response)
                running_tasks = unfinished
            except Exception as e:
                logger.error(f'error happened during running async tasks', exc_info=e)
        
        if self.teardown_call is not None:
            f = getattr(self.sut_obj, self.teardown_call)
            if asyncio.iscoroutinefunction(f):
                self.event_loop.run_until_complete(f())
            else:
                f()               

    def join(self):
        logger.info(f'worker {self} is terminated')


if __name__ == '__main__':
    pass