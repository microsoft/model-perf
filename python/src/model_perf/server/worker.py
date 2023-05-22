# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import threading
import multiprocessing
from ..logger import logger


class Worker:
    def __init__(self, sut_cls, query_queue, response_queue):
        self.sut_cls = sut_cls
        self.sut_args = ([], {})
        self.sut_obj = None
        self.setup_call, self.infer_call, self.teardown_call = None, None, None
        self.detect_sut_functions()
        
        self.query_queue = query_queue
        self.response_queue = response_queue
    
    def __call__(self, *args, **kwds):
        self.sut_args = (args, kwds)
        return self

    def detect_sut_functions(self):
        for fun in dir(self.sut_cls):
            if fun.lower() in ['setup', 'start', 'init', 'open', 'create', 'load']:
                self.setup_call = fun
            if fun.lower() in ['forward', 'predict', 'run', 'infer', 'inference', 'execute']:
                self.infer_call = fun
            if fun.lower() in ['teardown', 'stop', 'destroy', 'close', 'exit', 'quit', 'clear', 'clean', 'cleanup', '__del__']:
                self.teardown_call = fun
        
        logger.info(f'sut: {self.sut_cls.__name__}, setup_call: {self.setup_call}, inference_call: {self.infer_call}, teardown_call: {self.teardown_call}')    
    
    def start(self):
        raise NotImplementedError()
        
    def join(self):   
        raise NotImplementedError()


if __name__ == '__main__':
    pass