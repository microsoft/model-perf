# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import atexit
import torch
from model_perf.model import GPT2
from model_perf.server import MLPerfBenchmark
from torch.profiler import profile, record_function, ProfilerActivity
from transformers import pipeline, set_seed
from transformers import GPT2Tokenizer, GPT2LMHeadModel


set_seed(42)

def prompt(m):
    gpt = GPT2()
    gpt.predict('Hello, my dog is cute Hello')
    
    for _ in range(10):
        m.predict('Hello, my dog is cute')

def profile_xx():
    generator = pipeline('text-generation', model='gpt2')
    with profile(activities=[ProfilerActivity.CPU], 
                 record_shapes=True, 
                 #with_flops=True,
                 with_stack=True
                 ) as prof:
        with record_function("model_inference"):
            generator("Hello, I'm a language model,", max_length=30, num_return_sequences=4)
    #print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=100))
    #print(prof.key_averages(group_by_stack_n=5).table(sort_by="cpu_time_total", row_limit=100))
    print(prof.key_averages(group_by_input_shape=True).table(sort_by="cpu_time_total", row_limit=300))

def profile_tensorboard():
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2', pad_token_id=tokenizer.eos_token_id)
    input_ids = tokenizer.encode("Hello, I'm a language model,", return_tensors='pt')
    with torch.profiler.profile(activities=[ProfilerActivity.CPU],
                                #schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
                                on_trace_ready=torch.profiler.tensorboard_trace_handler('./log/gpt2_latest'),
                                record_shapes=True,
                                profile_memory=True,
                                with_stack=True) as prof:
        for _ in range(0, 10):
            output = model.generate(input_ids, max_length=32)
            print(tokenizer.decode(output[0], skip_special_tokens=True))
            #prof.step()

class GPT2SUT:
    def __init__(self) -> None:
        self.model = GPT2()
    
    def run(self, query):
        self.model.generate(query)

def benchmark():
    bench = MLPerfBenchmark(GPT2SUT, num_workers=4, mode='mt', share_sut=True)()
    bench.start()
    bench.run_server_mode(queries=[{'query': 'a b c d e f g '}], target_qps=4, min_duration_ms=30000)
    #bench.run_single_stream(queries=[{'query': 'Hello, my dog is '}])
    bench.stop()


if __name__ == '__main__':
    #GPT2SUT().run('Hello, my dog is ')
    benchmark()
    #profile_tensorboard()
    
    atexit._run_exitfuncs()
