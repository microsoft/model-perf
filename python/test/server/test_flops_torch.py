# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import torch
from torch.profiler import profile, record_function, ProfilerActivity


class MatMul(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.a = torch.rand((8, 4))
        self.b = torch.rand((4, 8))

    def forward(self):
        return torch.matmul(self.a, self.b)
    

m = MatMul()
with profile(activities=[ProfilerActivity.CPU], record_shapes=True, with_flops=True) as prof:
    with record_function("model_inference"):
        m.forward()
flops = sum(i.flops for i in prof.key_averages())
print(flops)
#print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=10)) 