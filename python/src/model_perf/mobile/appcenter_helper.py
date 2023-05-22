# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
from ..utils import extract_result_from_text
from ..logger import logger
from ..utils import run_process
from typing import List
from pathlib import Path

import requests


class AppCenterHelper:
    base_url = "https://api.appcenter.ms/v0.1"
    supported_test_frameworks = ["appium"]

    def __init__(self, test_framework: str, owner: str, app: str, deviceset: str, api_token: str):
        if test_framework not in self.supported_test_frameworks:
            raise ValueError("Test framework: {0} not supported".format(test_framework))
        self.test_framework = test_framework

        if not api_token:
            raise ValueError("appcenter API token is not valid")
        if not owner:
            raise ValueError("appcenter owner is not valid")
        if not app:
            raise ValueError("appcenter app is not valid")           
        if not deviceset:
            raise ValueError("appcenter device set is not valid")

        self.owner = owner
        self.deviceset = deviceset
        self.app = app
        self.app_id = f"{owner}/{app}"
        self.app_url = f"{self.base_url}/apps/{self.app_id}"

        self.api_token = api_token
        self.headers = {"X-API-Token": api_token, "accept": "application/json"}
        self.locale = "en_US"
        self.test_series = "master"
        self.test_parameters = {}

        self.deviceset_id = self.fetch_deviceset_id(self.deviceset)
        self.device_infos = self.fetch_device_infos(self.deviceset_id)
        logger.info(f'Testing with device_info: {self.device_infos}')

    def fetch_deviceset_id(self, deviceset_name:str):
        all_devicesets = requests.get(f"{self.app_url}/owner/device_sets", headers=self.headers).json()
        for deviceset in all_devicesets:
            if deviceset["name"] == deviceset_name:
                return deviceset["id"]
        raise RuntimeError(f"Cannot find deviceset {deviceset_name}")

    def fetch_device_infos(self, deviceset_id:str):
        deviceset_info = requests.get(f"{self.app_url}/owner/device_sets/{deviceset_id}", headers=self.headers).json()
        if "deviceConfigurations" not in deviceset_info:
            raise RuntimeError(f"Invalid deviceset_id {deviceset_id}")
        # Use arm64-v8a for cpu arc, as there is no other arcs in current supported devicesets
        return [f'{item["model"]["name"]}, {item["osName"]}, arm64-v8a' for item in deviceset_info["deviceConfigurations"]]

    def get_device_infos(self):
        return self.device_infos

    def fetch_report(self, test_run_id: str):
        res = requests.get(f"{self.app_url}/test_runs/{test_run_id}/report", headers=self.headers)
        return res.json()

    def fetch_test_logs(self, test_run_id: str) -> List[str]:
        self.test_reports = self.fetch_report(test_run_id)
        self.test_logs = []
        for single_device_report in self.test_reports["device_logs"]:
            test_log_url = single_device_report["test_log"]
            res = requests.get(test_log_url)
            self.test_logs.append(res.text)
        return self.test_logs

    def get_test_run_id_from_log(self, log: str):
        return extract_result_from_text(log, "##vso[task.setvariable variable=TEST_RUN_ID]", "\n")

    def upload_test(self, test_app: str, test_driver_dir: str, data_dir: str = ''):
        """
        Upload Test to App Center
        """
        if not Path(test_app).exists():
            raise ValueError(f"test_app {test_app} not exists")
        
        if not Path(test_driver_dir).exists():
            raise ValueError(f"test_driver_dir {test_driver_dir} not exists")

        if not (Path(test_driver_dir) / data_dir).exists():
            raise ValueError(f"data_dir {data_dir} in folder {test_driver_dir} not exists")

        run_args = ["appcenter", "test", "run", self.test_framework, "--app", self.app_id, "--devices", f"{self.owner}/{self.deviceset}",
                    "--app-path", test_app, "--test-series", self.test_series, "--locale", self.locale, "--build-dir",
                    test_driver_dir]

        if data_dir:
            run_args.extend(["--include", data_dir])

        run_args.extend(["--token", self.api_token])

        run_args.extend(["--vsts-id-variable", f"TEST_RUN_ID", "--debug"])
        logger.info(' '.join(run_args))

        ret = run_process(args=run_args)
        return ret

    @staticmethod
    def install_app_center_cli():
        """
        Install App Center CLI
        """
        cli_install_args = ["npm", "install", "-g", "appcenter-cli"]
        return subprocess.run(cli_install_args, capture_output=True)
