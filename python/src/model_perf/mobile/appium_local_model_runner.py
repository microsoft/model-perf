# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import Dict

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

from ..utils import subprocess_run_command


class AppiumLocalModelRunner:
    def __init__(self):
        self.install_python_client()

    def install_python_client(self):
        """
        Install Appium Python client
        """
        pip_install_args = ["pip", "install", "Appium-Python-Client"]
        subprocess_run_command(pip_install_args)

    def run_android_test(self, device_id: str, apk_path: str, operations: Dict, out_dir):
        options = UiAutomator2Options()
        options.platformName = "Android"
        options.udid = device_id
        options.app = apk_path

        # Appium1 points to http://127.0.0.1:4723/wd/hub by default
        driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)

        # To-do: do operations on elements
        element = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='Edit Description')
        print(element.text)
        driver.quit()

    def run_ios_test(self, device_id: str, app_path: str, operations: Dict, out_dir):
        options = XCUITestOptions()
        options.platformName = "iOS"
        options.udid = device_id
        options.app = app_path

        # Appium1 points to http://127.0.0.1:4723/wd/hub by default
        driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)

        # do operations on elements
        el = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='item')
        el.click()
        driver.quit()
