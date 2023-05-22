if(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    if(${CMAKE_GENERATOR_PLATFORM} MATCHES "^[Ww][Ii][Nn]32$")
        set(CPU_ARCH "x86")
    elseif(${CMAKE_GENERATOR_PLATFORM} MATCHES "^[Xx]64$")
        set(CPU_ARCH "x64")
    elseif(${CMAKE_GENERATOR_PLATFORM} MATCHES "^[Aa][Rr][Mm]64$")
        set(CPU_ARCH "arm64")
    elseif(${CMAKE_GENERATOR_PLATFORM} MATCHES "^[Aa][Rr][Mm]$")
        set(CPU_ARCH "arm")
    endif()
    set(ONNXRUNTIME_URL https://github.com/microsoft/onnxruntime/releases/download/v${ORT_VERSION}/onnxruntime-win-${CPU_ARCH}-${ORT_VERSION}.zip)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    set(ONNXRUNTIME_URL
        https://github.com/microsoft/onnxruntime/releases/download/v${ORT_VERSION}/onnxruntime-linux-x64-${ORT_VERSION}.tgz
    )
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(ONNXRUNTIME_URL
        https://github.com/microsoft/onnxruntime/releases/download/v${ORT_VERSION}/onnxruntime-osx-x64-${ORT_VERSION}.tgz
    )
elseif(${CMAKE_SYSTEM_NAME} MATCHES "iOS")
    set(ONNXRUNTIME_URL
        https://onnxruntimepackages.z14.web.core.windows.net/pod-archive-onnxruntime-c-${ORT_VERSION}.zip
    )
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Android")
    set(ONNXRUNTIME_URL
        https://repo1.maven.org/maven2/com/microsoft/onnxruntime/onnxruntime-android/${ORT_VERSION}/onnxruntime-android-${ORT_VERSION}.aar
    )
endif()
message("CMAKE_SYSTEM_NAME= ${CMAKE_SYSTEM_NAME}")
message("ONNXRUNTIME_URL = ${ONNXRUNTIME_URL}")
FetchContent_Declare(onnxruntime_prebuilt 
                     URL ${ONNXRUNTIME_URL}
                     DOWNLOAD_EXTRACT_TIMESTAMP FALSE)
FetchContent_MakeAvailable(onnxruntime_prebuilt)
message("onnxruntime_prebuilt_SOURCE_DIR=${onnxruntime_prebuilt_SOURCE_DIR}")

if(${CMAKE_SYSTEM_NAME} MATCHES "Android")
    add_library(onnxruntime SHARED IMPORTED)
    set_target_properties(onnxruntime PROPERTIES IMPORTED_LOCATION 
        ${onnxruntime_prebuilt_SOURCE_DIR}/jni/${ANDROID_ABI}/libonnxruntime.so)
    target_include_directories(onnxruntime INTERFACE 
        ${onnxruntime_prebuilt_SOURCE_DIR}/headers)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
    add_library(onnxruntime SHARED IMPORTED)
    set_target_properties(onnxruntime PROPERTIES IMPORTED_IMPLIB ${onnxruntime_prebuilt_SOURCE_DIR}/lib/onnxruntime.lib)
    set_target_properties(onnxruntime PROPERTIES BINARY_DIRECTORY ${onnxruntime_prebuilt_SOURCE_DIR}/lib)
    target_include_directories(onnxruntime INTERFACE ${onnxruntime_prebuilt_SOURCE_DIR}/include)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
    add_library(onnxruntime SHARED IMPORTED)
    set_target_properties(onnxruntime PROPERTIES IMPORTED_LOCATION 
        ${onnxruntime_prebuilt_SOURCE_DIR}/lib/onnxruntime.so)
    target_include_directories(onnxruntime INTERFACE 
        ${onnxruntime_prebuilt_SOURCE_DIR}/headers)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    add_library(onnxruntime SHARED IMPORTED)
    set_target_properties(onnxruntime PROPERTIES IMPORTED_LOCATION 
        ${onnxruntime_prebuilt_SOURCE_DIR}/lib/onnxruntime.dylib)
    target_include_directories(onnxruntime INTERFACE 
        ${onnxruntime_prebuilt_SOURCE_DIR}/include)
elseif(${CMAKE_SYSTEM_NAME} MATCHES "iOS")
    add_library(onnxruntime STATIC IMPORTED)
    set_target_properties(onnxruntime PROPERTIES IMPORTED_LOCATION 
        ${onnxruntime_prebuilt_SOURCE_DIR}/onnxruntime.xcframework/ios-arm64/onnxruntime.framework/onnxruntime)
    target_include_directories(onnxruntime INTERFACE 
        ${onnxruntime_prebuilt_SOURCE_DIR}/Headers)
    
else()
    message(FATAL_ERROR "${CMAKE_SYSTEM_NAME} is not supported yet")
endif()

