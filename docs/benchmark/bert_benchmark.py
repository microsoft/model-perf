# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import numpy as np
import plotly
import plotly.graph_objects as go
from model_perf.model import Bert
from model_perf.server import MLPerfBenchmark


if __name__ == '__main__':
    
    reports = []
    m = Bert('bert-base-uncased')
    num_params = m.num_parameters()
    num_tokens_xs = [4, 8, 12, 16, 20, 24, 28, 32]
    for x in num_tokens_xs:
        query = m.gen_query(x-2)
        flops = m.estimate_flops(query)
        num_tokens = m.num_tokens(query)
        bench = MLPerfBenchmark(Bert,
                                num_workers=1,
                                mode='mp')('bert-base-uncased')
        bench.start()
        perf = bench.run_single_stream(queries=[{'query':query}], min_query_count=100)
        bench.stop()
        report = {'model': 'bert-base', 'params': num_params, 'tokens': num_tokens, 'flops': flops, 'avg_latency': perf['latency']['avg'], }
        print(report)
        reports.append(report)
    
    with open("bert_report.json", "w") as outfile:
        json.dump(reports, outfile, indent=4)

    latencies_ys = [report['avg_latency'] for report in reports]
    fig = go.Figure(data=go.Scatter(x=num_tokens_xs, y=latencies_ys))
    fig.update_layout(xaxis_title='Num of Tokens',
                      yaxis_title='Latency (ms)')

    plotly.offline.plot(fig, filename='bert_latency.html')
    #plotly.offline.plot([fig], include_plotlyjs=False, output_type='div')
