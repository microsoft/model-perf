cmake_minimum_required(VERSION 3.16)

set(DEVELOPMENT_PROJECT_NAME "test_app")                     # <== Set to your project name, e.g. project.xcodeproj
set(DEVELOPMENT_TEAM_ID "UBF8T346G9")                       # <== Set to your team ID from Apple
set(APP_NAME "test_app")                                     # <== Set To your app's name
set(APP_BUNDLE_IDENTIFIER "com.company.test_app")                # <== Set to your app's bundle identifier
set(TEST_NAME "Tests")                                      # <== Set to your test's name
set(TEST_BUNDLE_IDENTIFIER "com.company.tests")             # <== Set to your tests's bundle ID
set(CODE_SIGN_IDENTITY "Apple Development")                  # <== Set to your preferred code sign identity, to see list:
                                                            # /usr/bin/env xcrun security find-identity -v -p codesigning
                                                         
set(DEPLOYMENT_TARGET 16.1)                                  # <== Set your deployment target version of iOS
set(DEVICE_FAMILY "1")                                      # <== Set to "1" to target iPhone, set to "2" to target iPad, set to "1,2" to target both
set(LOGIC_ONLY_TESTS 0)                                     # <== Set to 1 if you do not want tests to be hosted by the application, speeds up pure logic tests but you can not run them on real devices

project(${DEVELOPMENT_PROJECT_NAME} VERSION 0.1)
include(FindXCTest)

message(STATUS XCTestFound:${XCTest_FOUND})

set(PRODUCT_NAME ${APP_NAME})
set(EXECUTABLE_NAME ${APP_NAME})
set(MACOSX_BUNDLE_EXECUTABLE_NAME ${APP_NAME})
set(MACOSX_BUNDLE_INFO_STRING ${APP_BUNDLE_IDENTIFIER})
set(MACOSX_BUNDLE_GUI_IDENTIFIER ${APP_BUNDLE_IDENTIFIER})
set(MACOSX_BUNDLE_BUNDLE_NAME ${APP_BUNDLE_IDENTIFIER})
set(MACOSX_BUNDLE_LONG_VERSION_STRING "1.0")
set(MACOSX_BUNDLE_SHORT_VERSION_STRING "1.0")
set(MACOSX_BUNDLE_BUNDLE_VERSION "1.0")
set(MACOSX_BUNDLE_COPYRIGHT "Copyright YOU")
set(MACOSX_DEPLOYMENT_TARGET ${DEPLOYMENT_TARGET})

set(APP_HEADER_FILES
    ./test_app.h
    ./AppDelegate.h
    ./SceneDelegate.h
    ./ViewController.h
)

set(APP_SOURCE_FILES
    ./test_app.cpp
    ./AppDelegate.m
    ./ViewController.mm
    ./SceneDelegate.m
    ./main.mm
)

set(RESOURCES
    ./Base.lproj/Main.storyboard
    ./Base.lproj/LaunchScreen.storyboard
)


# Turn on ARC
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fobjc-arc -std=c++17")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fobjc-arc -std=c++17")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -fobjc-arc -std=c++17")

# Build the C++ dynamically linked framework
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../../cpp/test_app_common ${CMAKE_CURRENT_BINARY_DIR}/test_app_common)


add_executable(
    ${APP_NAME}
    MACOSX_BUNDLE
    ${APP_HEADER_FILES}
    ${APP_SOURCE_FILES}
    ${RESOURCES}
)
target_link_libraries(${APP_NAME} test_app_common)

target_sources(${APP_NAME} PRIVATE Assets.xcassets)
set_source_files_properties(Assets.xcassets PROPERTIES
    MACOSX_PACKAGE_LOCATION Resources
)

# To disable bitcode:
set(ENABLE_BITCODE OFF)
set_target_properties(${APP_NAME} PROPERTIES XCODE_ATTRIBUTE_ENABLE_BITCODE "NO")

# Locate system libraries on iOS
find_library(UIKIT UIKit)
find_library(FOUNDATION Foundation)
find_library(MOBILECORESERVICES MobileCoreServices)
find_library(CFNETWORK CFNetwork)
find_library(SYSTEMCONFIGURATION SystemConfiguration)

# link the frameworks located above
target_link_libraries(${APP_NAME} ${UIKIT})
target_link_libraries(${APP_NAME} ${FOUNDATION})
target_link_libraries(${APP_NAME} ${MOBILECORESERVICES})
target_link_libraries(${APP_NAME} ${CFNETWORK})
target_link_libraries(${APP_NAME} ${SYSTEMCONFIGURATION})

# Create the app target
set_target_properties(${APP_NAME} PROPERTIES
                      XCODE_ATTRIBUTE_DEBUG_INFORMATION_FORMAT "dwarf-with-dsym"
                      RESOURCE "${RESOURCES}"
                      XCODE_ATTRIBUTE_IPHONEOS_DEPLOYMENT_TARGET ${DEPLOYMENT_TARGET}
                      XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY ${CODE_SIGN_IDENTITY}
                      XCODE_ATTRIBUTE_DEVELOPMENT_TEAM ${DEVELOPMENT_TEAM_ID}
                      XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY ${DEVICE_FAMILY}
                      MACOSX_BUNDLE_INFO_PLIST ${CMAKE_CURRENT_SOURCE_DIR}/info.plist
                      XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC YES
                      XCODE_ATTRIBUTE_COMBINE_HIDPI_IMAGES NO
                      XCODE_ATTRIBUTE_INSTALL_PATH "$(LOCAL_APPS_DIR)"
                      XCODE_ATTRIBUTE_ENABLE_TESTABILITY YES
                      XCODE_ATTRIBUTE_GCC_SYMBOLS_PRIVATE_EXTERN YES
                      XCODE_ATTRIBUTE_CODE_SIGN_STYLE "Automatic"
                      XCODE_ATTRIBUTE_CLANG_CXX_LANGUAGE_STANDARD "gnu++20"
                      XCODE_ATTRIBUTE_FRAMEWORK_SEARCH_PATHS "${PROJECT_BINARY_DIR}/cppframework/\${CONFIGURATION}\${EFFECTIVE_PLATFORM_NAME}/"
                      GCC_C_LANGUAGE_STANDARD "gnu11"
                      XCODE_ATTRIBUTE_ASSETCATALOG_COMPILER_APPICON_NAME "AppIcon"
                      XCODE_ATTRIBUTE_ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME "AccentColor"
                      XCODE_ATTRIBUTE_INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents "YES"
				              XCODE_ATTRIBUTE_INFOPLIST_KEY_UILaunchStoryboardName "LaunchScreen"
                      XCODE_ATTRIBUTE_INFOPLIST_KEY_UIMainStoryboardFile "Main"
                      XCODE_ATTRIBUTE_INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight"
				              XCODE_ATTRIBUTE_INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight"
)


