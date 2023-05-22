# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from pathlib import Path
from typing import List, Union

from .mobile_model_runner import MobileModelRunner
from .appcenter_helper import AppCenterHelper
from .test_app import AndroidTestApp
from ..logger import logger
from model_perf.model.model_assets import ModelAssets


class AppCenterModelRunner(MobileModelRunner):
    def __init__(self, model: ModelAssets,
                 test_app: Union[str, Path] = AndroidTestApp.ONNXRUNTIME_1_12_0,
                 test_driver_app: Union[str, Path] = '',
                 output_dir: Union[str, Path] = '',
                 appcenter_token: str = '',
                 appcenter_owner: str = '',
                 appcenter_app: str = '',
                 appcenter_deviceset: str = ''):
        super().__init__(model=model,test_app=test_app,test_driver_app=test_driver_app,output_dir=output_dir)
        
        if not appcenter_token and 'APPCENTER_TOKEN' in os.environ:
            appcenter_token = os.environ['APPCENTER_TOKEN']
        if not appcenter_token:
            raise ValueError("Cannot find appcenter api token. Please either set environment variable 'APPCENTER_TOKEN' or provide it")

        self.appcenter_helper = AppCenterHelper(test_framework="appium",
                                                owner=appcenter_owner,
                                                app=appcenter_app,
                                                deviceset=appcenter_deviceset,
                                                api_token=appcenter_token)
        self.device_infos = self.get_device_infos()

    def run_test_on_backend(self) -> List[str]:
        # upload appium test to app center
        upload_log = self.appcenter_helper.upload_test(test_app=self.test_app.as_posix(),
                                                       test_driver_dir=self.upload_dir.as_posix(),
                                                       data_dir=self.data_dir.relative_to(self.upload_dir).as_posix())

        # fetch run_id from log
        self.run_id = self.appcenter_helper.get_test_run_id_from_log(upload_log)
        if not self.run_id:
            raise RuntimeError("failed to submit job to app center, invalid job id returned.")
        logger.info(f'job submitted to app center, run_id = {self.run_id}')

        # fetch test logs
        test_logs = self.appcenter_helper.fetch_test_logs(self.run_id)
        return test_logs
    
    def get_device_infos(self):
        return self.appcenter_helper.get_device_infos()
