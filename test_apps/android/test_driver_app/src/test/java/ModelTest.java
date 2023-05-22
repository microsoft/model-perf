// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import com.microsoft.appcenter.appium.EnhancedAndroidDriver;
import com.microsoft.appcenter.appium.Factory;
import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.nativekey.AndroidKey;
import io.appium.java_client.android.nativekey.KeyEvent;
import io.appium.java_client.remote.MobileCapabilityType;
import io.appium.java_client.remote.MobilePlatform;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestWatcher;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.remote.DesiredCapabilities;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.concurrent.TimeUnit;
import java.nio.file.Path;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Base64;

public class ModelTest {

    @Rule
    public TestWatcher watcher = Factory.createWatcher();

    private EnhancedAndroidDriver driver;

    @Before
    public void SetUp() throws MalformedURLException {
        // remember to remain this value empty when check-in
        Path appPath = Paths.get("test_app.apk");
        System.out.println("appPath is: " + appPath.toAbsolutePath().toString());
    
        DesiredCapabilities capabilities = new DesiredCapabilities();
        capabilities.setCapability(MobileCapabilityType.PLATFORM_NAME, MobilePlatform.ANDROID);
        capabilities.setCapability(MobileCapabilityType.APP, appPath.toAbsolutePath().toString());
        capabilities.setCapability(MobileCapabilityType.AUTOMATION_NAME, "UiAutomator2");
        capabilities.setCapability("autoGrantPermissions", false);
        capabilities.setCapability("fullReset", true);
        capabilities.setCapability("appWaitPackage", "com.android.settings");
        capabilities.setCapability("appWaitActivity", "*");
        capabilities.setCapability("appWaitDuration", "10000");

        // The enhanced driver is provided primarily to enable the label feature
        driver  = Factory.createAndroidDriver(new URL("http://127.0.0.1:4723/wd/hub"), capabilities);
        driver.label("Start App");
    }

    @After
    public void TearDown(){
        driver.label("Stop App");
        driver.quit();
    }

    @Test
    public void TestModelInference() throws IOException, InterruptedException {
        // turn on all file access permission.
        WebElement permissionSwitch = driver.findElement(AppiumBy.className("android.widget.Switch"));
        permissionSwitch.click();
        TimeUnit.SECONDS.sleep(3);
        driver.label("Allow All File Access");
        driver.pressKey(new KeyEvent(AndroidKey.BACK));

        // get data directory
        WebElement dataDirTextInput = driver.findElement(AppiumBy.accessibilityId("Data Directory"));
        String remoteDataDir = dataDirTextInput.getText();
        String localDataDir = "data";

        // push model and data files.
        System.out.println(String.format("localDataDir: %s remoteDataDir: %s", localDataDir, remoteDataDir));
        Path localDataDirPath = Paths.get(localDataDir);
        Files.walk(localDataDirPath).forEach(path -> {
            if (!path.toFile().isDirectory()) {
                System.out.println(path.toString());
                Path pathRelative = localDataDirPath.relativize(path);
                String pathRelativeString = pathRelative.toString().replace("\\", "/");
                System.out.println(pathRelativeString);
                try {    
                    driver.pushFile(String.format("%s/%s", remoteDataDir, pathRelativeString), path.toFile());
                }
                catch (IOException e) {
                    System.out.println("Not find");
                }
            }
        });

        // run test on the device.
        WebElement startButton = driver.findElement(AppiumBy.accessibilityId("Start Testing"));
        startButton.click();
        driver.label("Make Inference Calls");

        // Sleep 10 seconds to wait inference call ends
        // TODO:Use callback function instead
        TimeUnit.SECONDS.sleep(10);

        // pull result files back.
        byte[] model_output = driver.pullFile(String.format("%s/model_outputs.msgpack", remoteDataDir));
        byte[] metrics_output = driver.pullFile(String.format("%s/metrics.json", remoteDataDir));
        System.out.println("MODEL_OUTPUT_START");
        String model_output_base64 = Base64.getEncoder().encodeToString(model_output);
        System.out.println(new String(model_output_base64));
        System.out.println("MODEL_OUTPUT_END");
        System.out.println("METRICS_OUTPUT_START");
        System.out.println(new String(metrics_output));
        System.out.println("METRICS_OUTPUT_END");
    }
}
