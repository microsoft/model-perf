# Appcenter Model Runner Test

## Prerequisites

1. Follow [Model Test App](../../../../apps/android/model_test_app/README.md) to setup android app

2. Follow [Appium](../../../../apps/android/test_driver_app/README.md) to setup appium and appcenter

3. Install python package
```shell
cd python
pip install -r requirements.txt
pip install -e .
```

## Run

To run in appcenter, you will need a token, request token and permission for orgnization https://appcenter.ms/orgs/test-org/apps/test-app/

Fill the line [here](./test_appcenter_model_runner.py) with your token 
```python
api_token = ""
```

Then run the python file

```shell
cd python/src/test/mobile
python test_appcenter_model_runner.py
```