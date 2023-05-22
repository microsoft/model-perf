# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.options import Options as SafariOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class WebDriver:
    def __init__(self, browser: str, out_dir: str):
        self.browser = browser.lower()
        self.out_dir = out_dir
        # create web driver
        self.driver = self.get_driver(self.browser)

    def run(self, config_path: str):
        if not Path(config_path).exists():
            raise ValueError('Config file: {0} does not exist'.format(config_path))

        # input files
        config_path = Path(config_path).resolve()
        config_dir = Path(config_path).parent
        model_input_path = Path(config_dir / 'model_inputs.json').resolve()

        # load web page
        self.driver.get('http://localhost:3000')
        time.sleep(2)  # Let user actually see something!

        # start monitoring
        start_monitoring_btn = self.driver.find_element(by=By.ID, value='StartMonitoring')
        start_monitoring_btn.click()

        # upload config json file
        config_file = self.driver.find_element(by=By.XPATH, value="//input[@name='JsonConfigFile']")
        config_file.send_keys(str(config_path))
        time.sleep(2)

        # import ort js script
        import_script_btn = self.driver.find_element(by=By.ID, value='ImportOrtScript')
        import_script_btn.click()
        time.sleep(2)

        # upload model input json file
        input_file = self.driver.find_element(by=By.XPATH, value="//input[@name='ModelInputFile']")
        input_file.send_keys(str(model_input_path))
        time.sleep(2)

        # create inference session
        create_session_btn = self.driver.find_element(by=By.ID, value='CreateInferenceSession')
        create_session_btn.click()
        time.sleep(5)  # Wait for inference session to be created.

        # run model
        run_model_btn = self.driver.find_element(by=By.ID, value='RunModel')
        run_model_btn.click()
        time.sleep(5)  # Wait for model running.

        # Run perf test
        run_perf_test_btn = self.driver.find_element(by=By.ID, value='RunPerfTest')
        run_perf_test_btn.click()
        time.sleep(10)  # Wait for performance testing.

        # stop monitoring
        stop_monitoring_btn = self.driver.find_element(by=By.ID, value='StopMonitoring')
        stop_monitoring_btn.click()

        # get log
        browser_name = str(self.driver.capabilities['browserName']).lower()
        browser_version = self.driver.capabilities['browserVersion']
        platform_name = str(self.driver.capabilities['platformName']).lower()
        if self.browser == 'chrome' or self.browser == 'msedge' or self.browser == 'edge':
            log_data = self.driver.get_log('browser')
            file = open(Path(self.out_dir) / "metrics_{0}_{1}_{2}.json".format(browser_name, browser_version, platform_name), "w")
            json.dump(log_data, file)
            file.close()
        elif self.browser == 'firefox':
            cwd = os.getcwd()
            if (Path(cwd) / "geckodriver.log").exists():
                src = str(Path(cwd) / "geckodriver.log")
                tgt = str(self.out_dir) + "/metrics_{0}_{1}_{2}.log".format(browser_name, browser_version, platform_name)
                shutil.copy(src, tgt)
            else:
                raise FileNotFoundError("Log file: {0} not found".format(str(Path(cwd) / "geckodriver.log")))
        elif self.browser == 'safari':
            # get logs from html element because Safari web driver cannot retrieve log from console.log
            logs_element = self.driver.find_element(by=By.ID, value='MetricsLogs')
            inner_html = logs_element.get_attribute('innerHTML')
            p_strs = inner_html[3:-4].split('</p><p>')
            p_arr = [json.loads(p) for p in p_strs]
            file = open(Path(self.out_dir) / "metrics_{0}_{1}_{2}.json".format(browser_name, browser_version, platform_name), "w")
            json.dump(p_arr, file)
            file.close()

        self.driver.quit()

    @staticmethod
    def get_driver(browser: str):
        # disable WDM progress bar because it will output to error stream
        os.environ['WDM_PROGRESS_BAR'] = '0'

        if browser == 'chrome':
            # create Chrome web driver
            service = ChromeService(executable_path=ChromeDriverManager().install())
            # enable browser logging
            d = DesiredCapabilities.CHROME
            d['goog:loggingPrefs'] = {'browser': 'ALL'}
            driver = webdriver.Chrome(service=service, desired_capabilities=d)

            return driver
        elif browser == 'msedge' or browser == 'edge':
            # create Edge web driver
            service = EdgeService(EdgeChromiumDriverManager().install())
            # enable browser logging
            d = DesiredCapabilities.EDGE
            d['ms:loggingPrefs'] = {'browser': 'ALL'}
            driver = webdriver.Edge(service=service, capabilities=d)
            return driver
        elif browser == 'firefox':
            # remove firefox log file if exists
            log_path = Path(os.getcwd()) / "geckodriver.log"
            if log_path.exists():
                os.remove(log_path)

            # create Firefox web driver
            service = FirefoxService(GeckoDriverManager().install())
            options = FirefoxOptions()
            # provide access to console logs in Firefox
            options.set_preference('devtools.console.stdout.content', True)
            driver = webdriver.Firefox(service=service, options=options)
            return driver
        elif browser == 'safari':
            # enable safari driver
            enable_args = ["safaridriver", "--enable"]
            print(" ".join(enable_args))
            result = subprocess.run(enable_args, capture_output=True, text=True, shell=True)
            print(result.stdout)
            print(result.stderr)
            # create Safari web driver
            options = SafariOptions()
            options.set_capability('safari:diagnose', True)
            driver = webdriver.Safari(options=options)
            return driver
        else:
            raise ValueError('Cannot find web driver for browser: {0}'.format(browser))
