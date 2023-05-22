// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#import <Foundation/Foundation.h>
#import "ViewController.h"
#import "test_app.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sys/types.h>
#include <dlfcn.h>
#include <dirent.h>

static NSString *RUNNING = @"Running";
static NSString *DONE = @"Done";
static NSString *ERROR = @"Error";
static NSString *NOT_STARTED = @"NOT_STARTED";

@interface ViewController ()
{
    IBOutlet UIButton *startButton;
    IBOutlet UIButton *resetButton;
    IBOutlet UITextField *modelOutputsField;
    IBOutlet UITextField *modelConfigField;
    IBOutlet UITextField *statusField;
}
@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.
    statusField.text = NOT_STARTED;
}
- (IBAction)clickStart {
    
    NSURL *docDirURL = [[NSFileManager defaultManager] URLForDirectory:NSDocumentDirectory inDomain:NSUserDomainMask appropriateForURL:nil create:false error:NULL];
    assert(docDirURL != nil);
    
    std::string docDirStr(docDirURL.fileSystemRepresentation);
    NSLog(@"Root Directory=%s\n", docDirStr.c_str());
    std::string configPath = docDirStr + "/data/config.json";
    assert(std::filesystem::exists(configPath));
    std::string metricsPath = docDirStr + "/data/metrics.json";
    if (std::filesystem::exists(metricsPath)) {
        std::filesystem::remove(metricsPath);
        NSLog(@"Remove existed mlperf summary path in %s\n", metricsPath.c_str());
    }
    std::string modelOutputPath = docDirStr + "/data/model_outputs.msgpack";
    if (std::filesystem::exists(modelOutputPath)) {
        std::filesystem::remove(modelOutputPath);
        NSLog(@"Remove existed model output path in %s\n", modelOutputPath.c_str());
    }
    statusField.text = RUNNING;
    
    model_perf::RunModelTest(configPath);
    
    assert(std::filesystem::exists(metricsPath));
    assert(std::filesystem::exists(modelOutputPath));
    
    std::ifstream f(modelOutputPath, std::ios::in | std::ios::binary);
    auto sz = std::filesystem::file_size(modelOutputPath);
    modelOutputsField.text = [NSString stringWithFormat:@"output size=%lu", sz];
    
    statusField.text = DONE;
}

@end
