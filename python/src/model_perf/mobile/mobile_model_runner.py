# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union, Tuple

from model_perf.dataset.msgpack_helper import serialize_dataset, deserialize_from_base64
from model_perf.model.model_assets import ModelAssets
from model_perf.model_runner import ModelRunner
from model_perf.utils import extract_result_from_text, extract_latency_percentile, extract_performance, unzip


class MobileModelRunner(ModelRunner):
    MODEL_OUTPUT_START = "MODEL_OUTPUT_START"
    MODEL_OUTPUT_END = "MODEL_OUTPUT_END"
    METRICS_OUTPUT_START = "METRICS_OUTPUT_START"
    METRICS_OUTPUT_END = "METRICS_OUTPUT_END"

    def __init__(self, model: ModelAssets,
                 test_app: Union[str, Path],
                 test_driver_app: Union[str, Path],
                 output_dir: Union[str, Path]):
        super().__init__(model, output_dir)
        # app
        if not test_app:
            raise ValueError("Test app is not valid")
        self.test_app = Path(test_app)

        # driver app
        if not test_driver_app:
            raise ValueError("Test driver app is not valid")
        self.test_driver_app = Path(test_driver_app)

        self.test_logs: List[str] = []
        self.device_infos: List[str] = []

    def run(self, inputs: List[Any], config: Dict[str, Any], mode='all'):
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        upload_dir = self.output_dir / 'upload'
        data_dir = upload_dir / 'data'
        self.upload_dir = upload_dir
        self.data_dir = data_dir
        
        # 1. copy the Appium Client (Java) and unzip it if it is zipped, copy test_app to the same directory
        if self.test_driver_app.name.endswith('.zip'):
            unzip(self.test_driver_app, upload_dir)
        else:
            shutil.copytree(self.test_driver_app, upload_dir)
        
        target_app_path = self.upload_dir / ('test_app' + self.test_app.suffix)
        shutil.copy(self.test_app.absolute().as_posix(), target_app_path.absolute().as_posix())

        # 2. serialize config
        data_dir.mkdir(parents=True)
        config_path = data_dir / 'config.json'
        inputs_file_name = 'model_inputs.msgpack'
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

        # 3. serialize inputs to a `model_inputs.json` file
        self.inputs_path = serialize_dataset(inputs, target_folder=data_dir, target_file_name='model_inputs.msgpack')

        # 4. copy model files
        model_dir = data_dir / 'models'
        model_dir.mkdir()
        for model_file in self.model.files:
            shutil.copyfile(os.path.join(self.model.root_dir, model_file),
                            os.path.join(model_dir, model_file))
        
        # 5. run test on backend, such as appcenter or avd
        self.test_logs = self.run_test_on_backend()
    
    def run_test_on_backend(self) -> List[str]:
        raise NotImplementedError
    
    def get_benchmark_result(self)->List[Any]:
        ret = []
        device_infos = self.get_device_infos()
        idx = 0
        for device_info, test_log in zip(device_infos, self.test_logs):
            metrics_log = extract_result_from_text(test_log, self.METRICS_OUTPUT_START, self.METRICS_OUTPUT_END)
            metrics = extract_performance(metrics_log)
            ret.append({"device_info": device_info,
                        **metrics})
            Path(self.upload_dir / 'data' / f'metrics_{idx}.json').write_text(metrics_log)
            idx += 1
        return ret

    def get_predict_result(self)->List[Any]:
        ret = []
        device_infos = self.get_device_infos()
        idx = 0
        for device_info, test_log in zip(device_infos, self.test_logs):
            result_base64 = extract_result_from_text(test_log, self.MODEL_OUTPUT_START, self.MODEL_OUTPUT_END)
            model_outputs = deserialize_from_base64(result_base64)
            ret.append({"device_info": device_info,
                        "model_outputs": model_outputs})
            Path(self.upload_dir / 'data' / f'model_outputs_{idx}.json').write_text(str(model_outputs))
            idx += 1
        return ret

    def predict_and_benchmark(self, inputs: List[Any], config: Dict[str, Any]={}) -> Tuple[List[Any], List[Any]]:
        self.run(inputs, config, mode='all')
        return (self.get_predict_result(), self.get_benchmark_result())

    def predict(self, inputs: List[Any], config: Dict[str, Any]={}) -> List[Any]:
        self.run(inputs, config, mode='predict')
        return self.get_predict_result()

    def benchmark(self, inputs: List[Any], config: Dict[str, Any]={}) -> List[Any]:
        self.run(inputs, config, mode='benchmark')
        return self.get_benchmark_result()

    def get_device_infos(self) -> List[str]:
        # Device information should follow the format: Tuple(Device, OS version, CPU processor/architecture). Example:
        # Windows, 10.0.20348, Intel64 Family 6 Model 79 Stepping 1 GenuineIntel
        # Samsung Galaxy S5, Android 6.0.1, armeabi-v7a
        # Google Pixel 4a, Android 13, arm64-v8a
        raise NotImplementedError
