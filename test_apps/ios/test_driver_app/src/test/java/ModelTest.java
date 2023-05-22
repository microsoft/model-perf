// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import com.microsoft.appcenter.appium.EnhancedIOSDriver;
import com.microsoft.appcenter.appium.Factory;
import io.appium.java_client.AppiumBy;
import io.appium.java_client.remote.MobileCapabilityType;
import io.appium.java_client.remote.MobilePlatform;

import org.junit.*;
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
import java.nio.ByteBuffer;
import java.util.Base64;


public class ModelTest {

    @Rule
    public TestWatcher watcher = Factory.createWatcher();
    static String RUNNING = "Running";
    static String DONE = "Done";
    static String ERROR = "Error";
    static String NOT_STARTED = "NOT_STARTED";
    private EnhancedIOSDriver driver;
    private String bundleId = "com.company.test_app";

    @Before
    public void SetUp() throws MalformedURLException {
        DesiredCapabilities capabilities = new DesiredCapabilities();
        
        Path appPath = Paths.get("test_app.ipa");
        capabilities.setCapability(MobileCapabilityType.PLATFORM_VERSION, "16.1");
        capabilities.setCapability(MobileCapabilityType.DEVICE_NAME, "iPhone 13");
        capabilities.setCapability(MobileCapabilityType.UDID, "00008110-000A4C3C22A2801E");
        capabilities.setCapability("xcodeOrgId", "UBF8T346G9");
        capabilities.setCapability("xcodeSigningId", "iPhone Developer");

        capabilities.setCapability(MobileCapabilityType.PLATFORM_NAME, MobilePlatform.IOS);
        System.out.println("appPath is: " + appPath.toAbsolutePath().toString());
        capabilities.setCapability(MobileCapabilityType.APP, appPath.toAbsolutePath().toString());
        capabilities.setCapability(MobileCapabilityType.AUTOMATION_NAME, "XCUITest");
        capabilities.setCapability("autoGrantPermissions", true);
        capabilities.setCapability("autoAcceptAlerts", true);
        capabilities.setCapability("autoDismissAlerts", true);
        capabilities.setCapability("fullReset", false);
        capabilities.setCapability("appWaitActivity", "*");

        // The enhanced driver is provided primarily to enable the label feature
        driver  = Factory.createIOSDriver(new URL("http://127.0.0.1:4723/wd/hub"), capabilities);
        driver.label("Start App");
    }

    @After
    public void TearDown(){
        driver.label("Stop App");
        driver.quit();
    }

    @Test
    public void TestModelInference() throws IOException, InterruptedException {
        // get data directory
        System.out.println(driver.getPageSource());
        String remoteDataDir = String.format("@%s:data/Documents/data", bundleId);
        String localDataDir = "data";

        // push model and data files.
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
        WebElement startButton = driver.findElement(AppiumBy.accessibilityId("startButton"));
        startButton.click();
        driver.label("Click start button");

        // Sleep 10 seconds to wait inference call ends
        while (true) {
            WebElement statusField = driver.findElement(AppiumBy.accessibilityId("statusField"));
            String statusText = statusField.getText();
            if (statusText.equals(RUNNING)) {
                System.out.println("Still running, wait for 1s");
                TimeUnit.SECONDS.sleep(1);
            }
            else if (statusText.equals(ERROR) || statusText.equals(NOT_STARTED)) {
                Assert.fail("Internal error during app runs");
            }
            else if (statusText.equals(DONE)) {
                System.out.println("Run succeed, processing data");
                break;
            }
        }

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
