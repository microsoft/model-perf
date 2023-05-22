// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#include <jni.h>
#include <string>
#include <memory>

#include "driver.h"

using namespace model_perf;

extern "C" JNIEXPORT void JNICALL
Java_com_example_modeltestandroid_MainActivity_testModelFromJNI(
        JNIEnv* env,
        jobject thiz,
        jstring config_path_jstr
        ) {
    const char* config_path_cstr = env->GetStringUTFChars(config_path_jstr, NULL);
    std::string config_path(config_path_cstr);
    // Logger::CreateSystemLogger(true, false, "/storage/emulated/0/ModelTest/data/log.txt", true);

    Driver* driver_ptr = new Driver(config_path);
    driver_ptr->RunModel();
    driver_ptr->RunPerfTest();
    delete(driver_ptr);
    env->ReleaseStringUTFChars(config_path_jstr, config_path_cstr);
}
