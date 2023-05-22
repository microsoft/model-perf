# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import glob
import json
import os
import shutil
import subprocess
from ..logger import logger
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from modelperf.dataset.json_helper import serialize_model_inputs, deserialize_model_outputs_from_file
from modelperf.model.model import Model
from modelperf.model_runner import ModelRunner
from modelperf.utils import extract_model_outputs_from_chrome_log, extract_perf_metrics_from_chrome_log, \
    extract_perf_metrics_from_firefox_log, extract_model_outputs_from_firefox_log, extract_perf_metrics_from_safari_log, \
    extract_model_outputs_from_safari_log, unzip
from modelperf.web.web_driver import WebDriver


class WebModelRunner(ModelRunner):

    def __init__(self, model: Model, test_app: Union[str, Path], browsers: [], output_dir: Union[str, Path]):
        super().__init__(model=model, output_dir=output_dir)
        self.inputs_path = None
        # browsers to test model on
        self.browsers = ['msedge' if b.lower() == 'edge' else b.lower() for b in browsers]
        if len(self.browsers) == 0:
            raise ValueError('Browsers need to be specified for model testing.')

        # app
        if not test_app:
            raise ValueError("Test app is not valid")
        self.test_app = Path(test_app)

        # output logs
        self.metrics_logs: Dict[str, str] = {}

    def run(self, inputs: List[Any], config: Dict[str, Any]):
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        test_app_dir = self.output_dir / 'test_app'
        data_dir = self.output_dir / 'data'

        # 1. unzip test app if it is zipped
        if self.test_app.name.endswith('.zip'):
            unzip(self.test_app, test_app_dir)

        # 2. serialize config
        data_dir.mkdir(parents=True)
        config_path = data_dir / 'config.json'
        config['dataset'] = {"queries_path": "model_inputs.json"}
        config['inference_session'] = {"model_path": f"models/{self.model.model_files[0]}"}
        if 'metrics_collector' not in config.keys():
            config['metrics_collector'] = {
                "interval": 100  # milliseconds
            }

        with config_path.open('w') as f:
            json.dump(config, f)

        # 3. serialize inputs to a `model_inputs.json` file
        self.inputs_path = serialize_model_inputs(inputs, target_folder=data_dir, target_file_name='model_inputs.json')

        # 4. copy model files
        model_dir = data_dir / 'models'
        model_dir.mkdir()
        for model_file in self.model.files:
            shutil.copyfile(os.path.join(self.model.root_dir, model_file), os.path.join(model_dir, model_file))

        # 5.1 copy data to test web app folder for serving
        new_config_path = test_app_dir / 'config.json'
        shutil.copyfile(config_path, new_config_path)
        shutil.copyfile(self.inputs_path, test_app_dir / 'model_inputs.json')
        shutil.copytree(model_dir, test_app_dir / 'models')
        # 5.2 install npm package serve and kill-port
        self.install_serve_and_kill()
        # 5.3 serve test web app
        serve = self.serve_web_app(test_app_dir.absolute().as_posix())

        try:
            # 6. run web drivers to test
            for browser in self.browsers:
                browser = browser.lower()
                web_driver = WebDriver(browser, data_dir)
                web_driver.run(new_config_path)
                metrics_files = glob.glob(str(data_dir) + '/metrics_{0}*'.format(browser))
                if len(metrics_files) == 0:
                    raise ValueError('No metrics log file found.')
                key = Path(metrics_files[0]).stem[8:]
                self.metrics_logs[key] = Path(metrics_files[0]).read_text()
        except Exception as e:
            logger.exception(e)
        finally:
            # kill serve process
            serve.kill()
            serve.wait()
            self.kill_web_app("3000").wait()

    def predict_and_benchmark(self, inputs: List[Any], config: Dict[str, Any] = None) -> Tuple[List[Any], List[Any]]:
        if config is None:
            config = {}
        self.run(inputs, config)
        predict_result = self.predict(inputs, config, run=False)
        benchmark_result = self.benchmark(inputs, config, run=False)
        return predict_result, benchmark_result

    def get_benchmark_result(self):
        ret = []
        for browser_info, metrics_log in self.metrics_logs.items():
            perf_metrics = None
            if browser_info.startswith('chrome') or browser_info.startswith('msedge'):
                perf_metrics = extract_perf_metrics_from_chrome_log(metrics_log)
            elif browser_info.startswith('firefox'):
                perf_metrics = extract_perf_metrics_from_firefox_log(metrics_log)
            elif browser_info.startswith('safari'):
                perf_metrics = extract_perf_metrics_from_safari_log(metrics_log)
            perf_result = {"device_info": self.get_device_info(browser_info)}
            perf_result = {**perf_result, **perf_metrics}
            ret.append(perf_result)
            Path(self.output_dir / 'data' / f'perf_metrics_{browser_info}.json').write_text(json.dumps(perf_result))
        return ret

    def get_predict_result(self):
        ret = []
        for browser_info, metrics_log in self.metrics_logs.items():
            model_outputs = None
            if browser_info.startswith('chrome') or browser_info.startswith('msedge'):
                model_outputs = extract_model_outputs_from_chrome_log(metrics_log)
            elif browser_info.startswith('firefox'):
                model_outputs = extract_model_outputs_from_firefox_log(metrics_log)
            elif browser_info.startswith('safari'):
                model_outputs = extract_model_outputs_from_safari_log(metrics_log)
            model_outputs_path = self.output_dir / 'data' / f'model_outputs_{browser_info}.json'
            Path(model_outputs_path).write_text(json.dumps(model_outputs))
            ret.append({"device_info": self.get_device_info(browser_info), "model_outputs": deserialize_model_outputs_from_file(model_outputs_path)})
        return ret

    @staticmethod
    def get_device_info(browser_info: str) -> str:
        # Device information should follow the format: Tuple(Device, OS version, CPU processor/architecture). Example:
        # Windows, 10.0.20348, Intel64 Family 6 Model 79 Stepping 1 GenuineIntel
        # Samsung Galaxy S5, Android 6.0.1, armeabi-v7a
        # Google Pixel 4a, Android 13, arm64-v8a
        # chrome, 111.0.5563.65, windows
        device_info = browser_info.split('_')
        return '{0}, {1}, {2}'.format(device_info[0], device_info[1], device_info[2])

    @staticmethod
    def install_serve_and_kill():
        install_args = ["npm", "install", "-g", "serve"]
        print(" ".join(install_args))
        result = subprocess.run(install_args, capture_output=True, text=True, shell=True)
        print(result.stdout)
        print(result.stderr)

        install_args = ["npm", "install", "-g", "kill-port"]
        print(" ".join(install_args))
        result = subprocess.run(install_args, capture_output=True, text=True, shell=True)
        print(result.stdout)
        print(result.stderr)

    @staticmethod
    def serve_web_app(test_app_dir: str):
        serve_args = ["serve", "-s", "."]
        print(" ".join(serve_args))
        # run at background
        serve = subprocess.Popen(serve_args, shell=True, cwd=test_app_dir)
        return serve

    @staticmethod
    def kill_web_app(port: str):
        kill_args = ["kill-port", port]
        print(" ".join(kill_args))
        # run at background
        kill = subprocess.Popen(kill_args, shell=True)
        return kill
