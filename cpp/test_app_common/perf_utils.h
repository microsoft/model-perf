// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once
#include <chrono>
#include <ctime>
#include <iomanip>
#include <math.h>
#include <sstream>
#include <string.h>
#include <string>

#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__)
#include <pdh.h>
#include <psapi.h>
#include <tchar.h>
#pragma comment(lib, "pdh")

#elif __APPLE__
#include <TargetConditionals.h>
#include <sys/types.h>
#include <unistd.h>
#include <mach/mach.h>
#if TARGET_IPHONE_SIMULATOR
#include <sys/types.h>
#include <unistd.h>
// iOS, tvOS, or watchOS Simulator
#elif TARGET_OS_MACCATALYST
// Mac's Catalyst (ports iOS API into Mac, like UIKit).
#elif TARGET_OS_IPHONE
// iOS, tvOS, or watchOS device
#elif TARGET_OS_MAC
// Other kinds of Apple platforms
#else
#error "Unknown Apple Platform"
#endif

#elif __ANDROID__
// Below __linux__ check should be enough to handle Android,
// but something may be unique to Android.
#include <sys/sysinfo.h>
#include <sys/times.h>
#include <sys/types.h>
#include <unistd.h>

#elif __linux__
#include <sys/sysinfo.h>
#include <sys/times.h>
#include <sys/types.h>
#include <sys/vtimes.h>
#include <unistd.h>

#else
#error "Unsupported Platform!"
#endif

namespace model_perf {

struct CPUUsage {
    float process_usage = 0.0;
};

struct MemoryUsage {
    float virtual_process_usage = 0.0;
    float physical_process_usage = 0.0;
};

#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__)
class PerformanceUtils {
    // Solution based on https://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process
  private:
    ULARGE_INTEGER last_cpu_ = { 0 };
    ULARGE_INTEGER last_kernel_cpu_ = { 0 };
    ULARGE_INTEGER last_user_cpu_ = { 0 };
    int num_processors_ = 1;

  public:
    PerformanceUtils() {
        SYSTEM_INFO sys_info;
        FILETIME ftime, fkernel, fuser;

        GetSystemInfo(&sys_info);
        num_processors_ = sys_info.dwNumberOfProcessors > 0 ? sys_info.dwNumberOfProcessors : 1;

        GetSystemTimeAsFileTime(&ftime);
        memcpy(&last_cpu_, &ftime, sizeof(FILETIME));

        GetProcessTimes(GetCurrentProcess(), &ftime, &ftime, &fkernel, &fuser);
        memcpy(&last_kernel_cpu_, &fkernel, sizeof(FILETIME));
        memcpy(&last_user_cpu_, &fuser, sizeof(FILETIME));
    }

    ~PerformanceUtils() {}

    CPUUsage GetCPUUsage() {
        CPUUsage usage;
        FILETIME ftime, fkernel, fuser;
        ULARGE_INTEGER now, kernel, user;
        GetSystemTimeAsFileTime(&ftime);
        memcpy(&now, &ftime, sizeof(FILETIME));
        GetProcessTimes(GetCurrentProcess(), &ftime, &ftime, &fkernel, &fuser);
        memcpy(&kernel, &fkernel, sizeof(FILETIME));
        memcpy(&user, &fuser, sizeof(FILETIME));
        float process_time = static_cast<float>(kernel.QuadPart - last_kernel_cpu_.QuadPart) + static_cast<float>(user.QuadPart - last_user_cpu_.QuadPart);
        float system_time = static_cast<float>(now.QuadPart - last_cpu_.QuadPart);

        // if system time elapsed == 0, return 0
        float percent = 0.0;
        percent = system_time == 0 ? 0 : process_time / system_time;
        percent /= static_cast<float>(num_processors_);
        last_cpu_ = now;
        last_kernel_cpu_ = kernel;
        last_user_cpu_ = user;
        usage.process_usage = percent * 100.0f;
        return usage;
    }

    MemoryUsage GetMemoryUsage() {
        PROCESS_MEMORY_COUNTERS_EX pmc;
        GetProcessMemoryInfo(GetCurrentProcess(), (PROCESS_MEMORY_COUNTERS*)&pmc, sizeof(pmc));

        MEMORYSTATUSEX mem_info;
        mem_info.dwLength = sizeof(MEMORYSTATUSEX);
        GlobalMemoryStatusEx(&mem_info);

        MemoryUsage memory;
        memory.virtual_process_usage = (float)pmc.PrivateUsage / 1024.0f;
        memory.physical_process_usage = (float)pmc.WorkingSetSize / 1024.0f;
        return memory;
    }
    static uint64_t GetPid() {
        return GetCurrentProcessId();
    }
};

#elif __APPLE__
class PerformanceUtils {
  public:
    thread_array_t         threads;
    mach_msg_type_number_t threadCount;
    mach_msg_type_number_t maxThreadCount;
    PerformanceUtils() {
        maxThreadCount = 0;
    }

    ~PerformanceUtils() {
        vm_deallocate(mach_task_self(), (vm_offset_t) threads, maxThreadCount * sizeof(thread_t));
    }

    CPUUsage GetCPUUsage() {
        CPUUsage c = { 0 };
        if (task_threads(mach_task_self(), &threads, &threadCount) != KERN_SUCCESS) {
            return { -1 };
        }
        maxThreadCount = std::max(maxThreadCount, threadCount);
        double usage = 0;
        for (int i = 0; i < threadCount; i++) {
            thread_info_data_t     threadInfo;
            mach_msg_type_number_t threadInfoCount = THREAD_INFO_MAX;
            if (thread_info(threads[i], THREAD_BASIC_INFO, (thread_info_t) threadInfo, &threadInfoCount) != KERN_SUCCESS) {
                usage = -1;
                break;
            }
            auto info = (thread_basic_info_t) threadInfo;
            if ((info->flags & TH_FLAGS_IDLE) == 0) {
                usage += double(info->cpu_usage) / TH_USAGE_SCALE;
            }
        }
        c.process_usage = usage;
        return c;
    }

    MemoryUsage GetMemoryUsage() {
        MemoryUsage m = { 0 };
        struct task_basic_info info;
        mach_msg_type_number_t size = sizeof(info);
        kern_return_t kern = task_info(mach_task_self(), TASK_BASIC_INFO, (task_info_t)&info, &size);
        if (kern != KERN_SUCCESS){
            std::cout<< "Failed to get memory info" << std::endl;
            return m;
        }
        m.physical_process_usage = info.resident_size / 1024.0f;
        return m;
    }
    static uint64_t GetPid() {
        return getpid();
    }
};

// #elif __ANDROID__
// Below __linux__ check should be enough to handle Android,
// but something may be unique to Android.

#elif __linux__ || __ANDROID__
class PerformanceUtils {
  private:
    long long int ParseLine(char* line) {

        // This assumes that a digit will be found and the line ends in " Kb".
        int i = strlen(line);
        const char* p = line;
        while (*p < '0' || *p > '9')
            p++;
        line[i - 3] = '\0';
        return atoll(p);
    }
    clock_t last_cpu_ = { 0 };
    clock_t last_sys_cpu_ = { 0 };
    clock_t last_user_cpu_ = { 0 };
    int num_processors_ = 0;

  public:
    PerformanceUtils() {
        struct tms time_sample;
        char line[128];

        last_cpu_ = times(&time_sample);
        last_sys_cpu_ = time_sample.tms_stime;
        last_user_cpu_ = time_sample.tms_utime;
        FILE* file = fopen("/proc/cpuinfo", "r");
        if (file) {
            num_processors_ = 0;
            while (fgets(line, 128, file) != NULL) {
                if (strncmp(line, "processor", 9) == 0)
                    num_processors_++;
            }
            fclose(file);
        }
    }

    ~PerformanceUtils() {}

    CPUUsage GetCPUUsage() {

        struct tms time_sample;
        clock_t now;
        float percent = 0.0;
        now = times(&time_sample);
        if (now <= last_cpu_) {
            // Overflow detection. Just skip this value.
            percent = -1.0;
        } else {
            percent = (time_sample.tms_stime - last_sys_cpu_) +
                      (time_sample.tms_utime - last_user_cpu_);
            percent /= (now - last_cpu_);
            percent /= num_processors_;
            percent *= 100;
        }
        last_cpu_ = now;
        last_sys_cpu_ = time_sample.tms_stime;
        last_user_cpu_ = time_sample.tms_utime;
        CPUUsage c;
        c.process_usage = percent;
        return c;
    }

    MemoryUsage GetMemoryUsage() {
        MemoryUsage m;
        m.physical_process_usage = m.virtual_process_usage = 0;
        FILE* file = fopen("/proc/self/status", "r");
        if (file == NULL) {
            fprintf(stderr, "no /proc/self/status is found");
            exit(0);
        }
        char line[128];
        while (
          fgets(line, 128, file) != NULL &&
          (m.virtual_process_usage == 0 || m.physical_process_usage == 0)) {
            if (strncmp(line, "VmSize:", 7) == 0) {
                m.virtual_process_usage = ParseLine(line);
            } else if (strncmp(line, "VmRSS:", 6) == 0) {
                m.physical_process_usage = ParseLine(line);
            }
        }
        fclose(file);
        return m;
    }
    static uint64_t GetPid() {
        return getpid();
    }
};

#else
#error "Unsupported Platform!"
#endif
} // namespace model_perf
