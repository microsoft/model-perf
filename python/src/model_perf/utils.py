# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import multiprocessing
import os
import re
import signal
import statistics
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import List, Any, Optional

import psutil
import requests

from .logger import logger


def get_datadir() -> Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = Path.home()
    if sys.platform.startswith('win'):
        return home / "AppData/Roaming"
    elif sys.platform.startswith('linux'):
        return home / ".local/share"
    elif sys.platform.startswith('darwin'):
        return home / "Library/Application Support"


def download_file(url, override=False) -> Path:
    dst_dir = get_datadir() / 'model-perf'

    os.makedirs(dst_dir, exist_ok=True)
    file_name = url.split('/')[-1]
    dst_file = Path(dst_dir / file_name).resolve()

    # NOTE the stream=True parameter below
    if dst_file.exists() and not override:
        print(f'File {dst_file} already exists, skip downloading')
        return dst_file

    print(f"Downloading {url} to {dst_file}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dst_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return dst_file


def subprocess_run_command(args):
    print("Command line arguments: {0}".format(" ".join(args)))
    result = subprocess.run(args, capture_output=True, text=True, timeout=600)
    # print(result.stdout)
    # print(result.stderr)


def extract_result_from_text(text: str, start_str: str, end_str: str):
    ret = ""
    cur = 0
    while True:
        start = text.find(start_str, cur)
        if start < 0:
            break
        if ret != "":
            ret += "\n"
        end = text.find(end_str, start)
        if end < 0:
            end = len(text)
        ret += text[start + len(start_str):end]
        cur = end + 1
    return ret


def extract_model_outputs_from_chrome_log(metrics_log: str):
    model_outputs = []
    metrics_json = json.loads(metrics_log)
    for entry in metrics_json:
        message = entry['message']
        metric_str = re.search("\{.*}", message)
        if metric_str is None or metric_str == '':
            continue
        metric_str = metric_str.group(0).replace('\\', '')
        metric = json.loads(metric_str)
        if 'outputs' in metric:
            model_outputs.append(metric)

    return model_outputs


def extract_model_outputs_from_firefox_log(metrics_log: str):
    model_outputs = []
    metric_lines = metrics_log.split('\n')
    for line in metric_lines:
        if not line.startswith('console.log: "{'):
            continue
        metric_str = re.search("\{.*}", line)
        if metric_str is None or metric_str == '':
            continue
        metric_str = metric_str.group(0).replace('\\', '')
        metric = json.loads(metric_str)
        if 'outputs' in metric:
            model_outputs.append(metric)

    return model_outputs


def extract_model_outputs_from_safari_log(metrics_log: str):
    model_outputs = []
    metrics = json.loads(metrics_log)
    for metric in metrics:
        if 'outputs' in metric:
            model_outputs.append(metric)

    return model_outputs


def extract_perf_metrics_from_chrome_log(metrics_log: str):
    perf_metrics = []
    metrics_json = json.loads(metrics_log)
    for entry in metrics_json:
        message = entry['message']
        metric_str = re.search("\{.*}", message)
        if metric_str is None or metric_str == '':
            continue
        metric_str = metric_str.group(0).replace('\\', '')
        metric = json.loads(metric_str)
        if 'cat' in metric:
            perf_metrics.append(metric)

    return extract_performance(json.dumps(perf_metrics))


def extract_perf_metrics_from_firefox_log(metrics_log: str):
    perf_metrics = []
    metric_lines = metrics_log.split('\n')
    for line in metric_lines:
        if not line.startswith('console.log: "{'):
            continue
        metric_str = re.search("\{.*}", line)
        if metric_str is None or metric_str == '':
            continue
        metric_str = metric_str.group(0).replace('\\', '')
        metric = json.loads(metric_str)
        if 'cat' in metric:
            perf_metrics.append(metric)

    return extract_performance(json.dumps(perf_metrics))


def extract_perf_metrics_from_safari_log(metrics_log: str):
    perf_metrics = []
    metrics = json.loads(metrics_log)
    for metric in metrics:
        if 'cat' in metric:
            perf_metrics.append(metric)

    return extract_performance(json.dumps(perf_metrics))


def regex_match(pattern: str, text: str) -> List[Any]:
    matches = re.findall(pattern, text)
    return matches


def extract_latency_percentile(latency_log: str):
    # latency
    min_result = int(regex_match(r"Min\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    p50_result = int(regex_match(r"50\.00\spercentile\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    p90_result = int(regex_match(r"90\.00\spercentile\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    p95_result = int(regex_match(r"95\.00\spercentile\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    p97_result = int(regex_match(r"97\.00\spercentile\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    p99_result = int(regex_match(r"99\.00\spercentile\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    p999_result = int(regex_match(r"99\.90\spercentile\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    max_result = int(regex_match(r"Max\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    mean_result = int(regex_match(r"Mean\slatency\s\(ns\)\s+:\s(\d+)", latency_log)[0]) / 1000000
    return {
        "Min": min_result,
        "P50": p50_result,
        "P90": p90_result,
        "P95": p95_result,
        "P97": p97_result,
        "P99": p99_result,
        "P99.9": p999_result,
        "Max": max_result,
        "Mean": mean_result
    }


def extract_performance(metrics_log: str):
    metrics_json = json.loads(metrics_log)

    all_cpu_series = []
    model_cpu_series = []
    all_memory_series = []
    model_memory_series = []
    event_series = []
    all_latency_series = []

    before_mem = 0
    max_mem_in_model_test = 0
    model_testing_start = False
    run_model_end = False
    latencies = {}

    for item in metrics_json:
        if item["cat"] == "Event":
            event_series.append({"name": item["name"], "time": item["ts"]})
            if model_testing_start == False and item["name"] == "ModelTestingStart":
                model_testing_start = True
            if run_model_end == False and item["name"] == "RunModelEnd":
                run_model_end = True
        elif item["cat"] == "Performance" and item["name"] == "CPU":
            all_cpu_series.append({"name": item["name"], "time": item["ts"], "value": item["args"]["CPU_Percentage"]})
            if model_testing_start == True and run_model_end == False:
                model_cpu_series.append(item["args"]["CPU_Percentage"])
        elif item["cat"] == "Performance" and item["name"] == "Memory":
            mem_kb = None
            if "Physical_Memory_KB" in item["args"]:
                # for windows, android and ios, use physical memory as memory size
                mem_kb = item["args"]["Physical_Memory_KB"]
            elif "JSHeapSize_KB" in item["args"]:
                # for browser validation, use js heap size as memory size
                mem_kb = item["args"]["JSHeapSize_KB"]
            else:
                raise ValueError("Memory log is not valid")

            all_memory_series.append({"name": item["name"], "time": item["ts"], "value": mem_kb})
            if not model_testing_start:
                before_mem = mem_kb
            else:
                if not run_model_end:
                    model_memory_series.append(mem_kb)
        elif item["cat"] == "Performance" and item["name"] == "Latency":
            latencies = item["args"]

    max_mem_in_model_test = max(model_memory_series)
    result = {
        "latency_ms": latencies,
        "peak_memory_kb": max_mem_in_model_test - before_mem,
        "avg_cpu_pct": statistics.mean(model_cpu_series),
        "event_series": event_series,
        "cpu_pct_series": all_cpu_series,
        "memory_kb_series": all_memory_series
    }

    return result


def normalize(s: str):
    return s.replace(' ', '').lower()


def run_process(args: List[str], cwd: Optional[str] = None, expect_return_codes: List[int] = [0]):
    logger.info(' '.join(args))
    ret = ''
    with subprocess.Popen(' '.join(args), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=cwd,
                          shell=True) as p:
        if p.stdout is not None:
            for line in p.stdout:
                ret += line
                logger.debug(line)
    if p.returncode not in expect_return_codes:
        raise subprocess.CalledProcessError(p.returncode, p.args)
    return ret


def inner_run(conn, args, wait_str, succ_str, show_log=False, log_id=''):
    ret = ''
    wait_str = normalize(wait_str)
    with subprocess.Popen(' '.join(args), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, shell=True) as p:
        if p.stdout is not None:
            for line in p.stdout:
                ret += line
                if show_log:
                    logger.info(log_id + line)
                else:
                    logger.debug(log_id + line)
                if normalize(line).find(wait_str) >= 0:
                    conn.send(succ_str)
                    conn.close()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)
    return ret


def run_background_process(args: List[str], wait_str: str, succ_str: str, show_log=False, log_id=''):
    logger.info(' '.join(args))
    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=inner_run, args=(child_conn, args, wait_str, succ_str, show_log, log_id,))
    p.start()
    logger.info(parent_conn.recv())
    parent_conn.close()
    return p


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        logger.info(f'kill child process {process.pid}')
        process.send_signal(sig)


def unzip(src_path: Path, target_dir: Path):
    # unzip file and replace separator
    with zipfile.ZipFile(src_path, 'r') as zip_ref:
        len_filelist = len(zip_ref.filelist)
        for idx in range(len_filelist):
            old_name = zip_ref.filelist[idx].filename
            new_name = old_name.replace("\\", os.sep)
            zip_ref.NameToInfo[new_name] = zip_ref.NameToInfo[old_name]
            zip_ref.filelist[idx].filename = zip_ref.filelist[idx].filename.replace("\\", os.sep)
        zip_ref.extractall(target_dir)
