# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
import platform
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from model_perf.dataset.msgpack_helper import serialize_dataset, deserialize_dataset
from model_perf.model.model_assets import ModelAssets
from model_perf.model_runner import ModelRunner
from model_perf.utils import subprocess_run_command, extract_performance


class DesktopModelRunner(ModelRunner):
    def __init__(self, model: ModelAssets, test_app: Union[str, Path], output_dir: Union[str, Path]):
        super().__init__(model_assets=model, output_dir=output_dir)
        self.inputs_path = None

        # app
        if not test_app:
            raise ValueError("Test app is not valid")
        self.test_app = Path(test_app)

        self.metrics_log: str = ""
        self.model_outputs: List[Any] = []

    def run_model(self, inputs: List[Any], config: Dict[str, Any], mode='all'):
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        test_app_dir = self.output_dir / 'test_app'
        data_dir = self.output_dir / 'data'

        # 1. unzip test app if it is zipped
        if self.test_app.name.endswith('.zip'):
            with zipfile.ZipFile(self.test_app, 'r') as zip_ref:
                zip_ref.extractall(test_app_dir)
                self.test_app = test_app_dir / 'test_app.exe'

        # 2. serialize config
        data_dir.mkdir(parents=True)
        config_path = data_dir / 'config.json'
        inputs_file_name = 'model_inputs.msgpack'
        config['root_dir'] = data_dir.resolve().as_posix()
        config['dataset'] = {'path': inputs_file_name}
        config['model']['path'] = f"models/{self.model.model_files[0]}"
        if 'load_gen' not in config.keys():
            config['load_gen'] = {
                "scenario": "SingleStream",
                "min_query_count": 100,
                "min_duration_ms": 1000
            }
        if 'metrics_collector' not in config.keys():
            config['metrics_collector'] = {
                "interval_ms": 10  # milliseconds
            }

        with config_path.open('w') as f:
            json.dump(config, f)

        # 3. serialize inputs to a model_inputs file
        self.inputs_path = serialize_dataset(inputs, target_folder=data_dir, target_file_name=inputs_file_name)

        # 4. copy model files
        model_dir = data_dir / 'models'
        model_dir.mkdir()
        for model_file in self.model.files:
            shutil.copyfile(os.path.join(self.model.root_dir, model_file),
                            os.path.join(model_dir, model_file))

        # 5. run model with test app
        args = [str(self.test_app.resolve().as_posix()), str(config_path.resolve().as_posix()), str(mode)]
        subprocess_run_command(args)

    def run(self, inputs: List[Any], config: Dict[str, Any], mode):
        self.run_model(inputs, config, mode)
        if mode == 'all' or mode == 'predict':
            self.model_outputs = deserialize_dataset(self.output_dir / 'data' / 'model_outputs.msgpack')
        self.metrics_log = Path(self.output_dir / 'data' / 'metrics.json').read_text()

    def predict_and_benchmark(self, inputs: List[Any], config: Dict[str, Any]={}) -> Tuple[List[Any], List[Any]]:
        self.run(inputs, config, mode='all')
        predict_result = {"device_info": self.get_device_info(), "model_outputs": self.model_outputs}

        benchmark_result = {"device_info": self.get_device_info()}
        metrics = extract_performance(self.metrics_log)
        benchmark_result = {**benchmark_result, **metrics}

        return [predict_result], [benchmark_result]

    def predict(self, inputs: List[Any], config: Dict[str, Any]={}) -> List[Any]:
        self.run(inputs, config, mode='predict')
        predict_result = {"device_info": self.get_device_info(), "model_outputs": self.model_outputs}
        return [predict_result]

    def benchmark(self, inputs: List[Any], config: Dict[str, Any]={}) -> List[Any]:
        self.run(inputs, config, mode='benchmark')
        benchmark_result = {"device_info": self.get_device_info()}

        # latency, cpu, memory
        metrics = extract_performance(self.metrics_log)
        benchmark_result = {**benchmark_result, **metrics}
        return [benchmark_result]

    def get_device_info(self) -> str:
        # Device information should follow the format: Tuple(Device, OS version, CPU processor/architecture). Example:
        # Windows, 10.0.20348, Intel64 Family 6 Model 79 Stepping 1 GenuineIntel
        # Samsung Galaxy S5, Android 6.0.1, armeabi-v7a
        # Google Pixel 4a, Android 13, arm64-v8a
        return '{0}, {1}, {2}'.format(platform.system(), platform.version(), platform.processor())
