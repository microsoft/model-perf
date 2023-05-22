# Appium

## Prerequisites

1. Install node
2. Install mvn
3. Install appcenter cli and appium client
```shell
npm install -g appcenter-cli appium
```

## Build

```shell
mvn -DskipTests -P prepare-for-upload package
```

## Test in Local

Start appium client locally first
```shell
appium
```

Then do mvn test
```shell
mvn test
```

## Test in appcenter
App Center runs Java 8(class file version 52)
```shell
appcenter test run appium --app "APP_ID" --devices "DEVICE_SET_ID" --app-path "PATH_TO_FILE.apk"  --test-series "main" --locale "en_US" --build-dir target/upload
```