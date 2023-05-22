app_path=`realpath ../../../../apps/ios/test_app/build.ios/test_app.ipa/com.company.test_app.ipa`
echo "Running app center test"
echo "app_path = ${app_path}"
mvn -DskipTests -P prepare-for-upload package
appcenter test run appium --app "test-org/test-app" --devices "test-org/iphone14-16-1" --app-path ${app_path} --test-series "master" --locale "en_US" --build-dir target/upload --include data