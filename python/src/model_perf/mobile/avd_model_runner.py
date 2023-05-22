# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from pathlib import Path
from typing import Union, List

from .mobile_model_runner import MobileModelRunner
from .test_app import AndroidTestApp
from ..logger import logger
from ..utils import run_background_process, run_process, kill_child_processes
import os
from model_perf.model.model_assets import ModelAssets


class AVDModelRunner(MobileModelRunner):
    def __init__(self, model: ModelAssets,
                 test_app: Union[str, Path] = AndroidTestApp.ONNXRUNTIME_1_12_0,
                 test_driver_app: Union[str, Path] = '',
                 output_dir: Union[str, Path] = '',
                 android_abi: str = 'x86_64',
                 android_api_level: int = 32,
                 android_home: str = ''):
        super().__init__(model=model, test_app=test_app, test_driver_app=test_driver_app, output_dir=output_dir)

        if android_abi not in ['x86', 'x86_64', 'arm64-v8a', 'armeabi-v7a']:
            raise RuntimeError("Virtual device android_system_abi should be in ['x86', 'x86_64', 'arm64-v8a', 'armeabi-v7a']")
        if android_api_level < 31 or android_api_level > 32:
            raise RuntimeError("Only Android API level 31, 32 are supported now.")
        self.os_version = 12
        
        emulator_name = f'model_test_emulator_{android_abi}_{android_api_level}'
        self.emulator_name = emulator_name        
        if not android_home and 'ANDROID_HOME' in os.environ:
            android_home = os.environ['ANDROID_HOME']
        if not android_home:
            raise ValueError(
                "Cannot find android_home. Please either set environment variable 'ANDROID_HOME' or provide it")
        self.android_home = Path(android_home)
        self.avdmanager_path = str(self.android_home / 'cmdline-tools/latest/bin/avdmanager')
        self.sdkmanager_path = str(self.android_home / 'cmdline-tools/latest/bin/sdkmanager')
        self.emulator_path = str(self.android_home / 'emulator/emulator')
        self.emulator_handle = None
        self.appium_handle = None
        self.android_abi = android_abi
        self.android_api_level = android_api_level

        self.create_virtual_device(emulator_name, android_abi, android_api_level)
        self.check_dependency()

    def check_virtual_device(self, name:str):
        args = [f'{self.avdmanager_path}', 'list', 'avds']
        res = run_process(args)
        return res.find(f'Name: {name}\n')>=0

    def create_virtual_device(self, name:str, android_system_abi:str, android_api_level:int):
        if self.check_virtual_device(name):
            logger.info(f"Vritual device {name} already created, use previous one")
        else:
            args = ['echo', 'y', '|', f'{self.sdkmanager_path}', '--install', f'"system-images;android-{android_api_level};google_apis;{android_system_abi}"']
            res = run_process(args, expect_return_codes=[0,1])
            logger.info(f"install system image: {res}")
            args = ['echo', 'no', '|', f'{self.avdmanager_path}', 'create', 'avd', '-n', name, '-k', f'"system-images;android-{android_api_level};google_apis;{android_system_abi}"', '-f']
            res = run_process(args)
            logger.info(f"create avd: {res}")
            args = [f'{self.avdmanager_path}', 'list', 'avds']
            res = run_process(args)
            logger.info(f"list avds: {res}")
            if self.check_virtual_device(name):
                logger.info(f"Create virtual device {name} successful")
            else:
                raise RuntimeError("Create virtual device {name} failed")

    def start_appium_server(self):
        args = ['appium', '--log-level', 'debug']
        wait_str = 'Appium REST http interface listener started on'
        succ_str = 'Start appium successfully'
        self.appium_handle = run_background_process(args=args, wait_str=wait_str, succ_str=succ_str, show_log=True, log_id='[APPIUM]')

    def check_dependency(self):
        # check appium node js client
        args = ['appium', '--version']
        res = run_process(args)
        logger.info(f"Detected appium with version {res}")
        # check mvn
        args = ['mvn', '--version']
        res = run_process(args)
        logger.info(f"Detected mvn {res}")
        # check emulator
        args = [self.emulator_path, '-list-avds']
        res = run_process(args)
        logger.info(f"Detected emulator {res}")

        # check accel
        args = [self.emulator_path, '-accel-check']
        res = run_process(args)
        logger.info(f"emulator -accel-check {res}")

    def start_emulator(self):
        args = [self.emulator_path, '-netdelay', 'none', '-netspeed', 'full', '-avd', self.emulator_name, '-no-snapshot', '-no-audio', '-no-window', '-accel', 'on', '-gpu', 'swiftshader_indirect']
        wait_str = 'INFO    | boot completed'
        succ_str = 'Start emulator successfully'
        self.emulator_handle = run_background_process(args=args, wait_str=wait_str, succ_str=succ_str)

    def run_appium_test(self):
        args = ['mvn', 'test']
        cwd = self.upload_dir.absolute().as_posix()
        res = run_process(args=args, cwd=cwd)
        return res
    
    def clean(self):
        if self.appium_handle:
            kill_child_processes(self.appium_handle.pid)
            self.appium_handle.terminate()
            self.appium_handle.join()
            self.appium_handle = None
        if self.emulator_handle:
            kill_child_processes(self.emulator_handle.pid)
            self.emulator_handle.terminate()
            self.emulator_handle.join()
            self.emulator_handle = None

    def run_test_on_backend(self) -> List[str]:
        self.start_appium_server()
        self.start_emulator()
        res = self.run_appium_test()
        self.clean()
        return [res]

    def get_device_infos(self) -> List[str]:
        return [f'Android Emulator, Android {self.os_version}, {self.android_abi}']
        