# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy


class TestAppiumClient(unittest.TestCase):
    def test_appium_client(self):
        options = UiAutomator2Options()
        options.platformName = "Android"
        # id of emulator on local device
        options.udid = 'emulator-5554'
        options.app = '../build/outputs/apk/debug/app-arm64-v8a-debug.apk'
        options.app_wait_package = 'com.android.settings'
        options.app_wait_activity = '*'
        options.app_wait_duration = 10000
        options.full_reset = True
        options.auto_grant_permissions = True

        # Appium1 points to http://127.0.0.1:4723/wd/hub by default
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)
        # find by android:contentDescription
        element = self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='Data Directory')
        print(element.text)


if __name__ == '__main__':
    unittest.main()
