# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import onnxruntime as ort
from model_perf.server import ServerModelRunner
from model_perf.logger import logger
import optuna
from optuna.pruners import BasePruner
from optuna.samplers import TPESampler, GridSampler


class OrtTestAppConfig:
    def __init__(self) -> None:
        self.num_workers = 1
        self.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        self.num_interop_threads:int = 1
        self.num_intraop_threads:int = 1
        self.provider:str = 'CPUExecutionProvider'


class Model:
    def __init__(self, model_file, config: OrtTestAppConfig) -> None:
        sess_options = ort.SessionOptions()
        sess_options.execution_mode = config.execution_mode
        sess_options.inter_op_num_threads = int(config.num_interop_threads)
        sess_options.intra_op_num_threads = int(config.num_intraop_threads)
        self.session = ort.InferenceSession(model_file, sess_options, providers=[config.provider])
    
    def predit(self, q):
        self.session.run(None, {'input':q})


def RunModel(model_file, config: OrtTestAppConfig, queries, target_qps) -> None:
    runner = ServerModelRunner(Model, config.num_workers)(model_file, config)
    result = runner.benchmark(queries=queries, target_qps=target_qps)
    return result['latency/p90']


class DuplicatePruner(BasePruner):
    ''' skip trials that were already evaluated. optuna doens't provide 
    the mechanism to skip duplicate trails.
    '''
    def __init__(self):
        pass
    
    def prune(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> bool:
        all_trails = study.get_trials(deepcopy=False)
        for t in all_trails:
            if trial is t:
                continue
            if trial.params == t.params:
                return True
        return False


# Note: it is unreasonable for num_cores to be bigger than physical CPU cores. 
def tune_for_qps(model_file:str, queries, num_cores: int):
    def objective(trial: optuna.Trial):           
        num_workers = trial.suggest_int('num_workers', 1, num_cores, 1)            
        if trial.should_prune():
            raise optuna.TrialPruned()

        config = OrtTestAppConfig()
        config.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        config.num_intraop_threads = num_cores // num_workers
        config.provider = 'CPUExecutionProvider'
        trial.set_user_attr('ort_config', config.__dict__)
        params = {**trial.params,
                    **config.__dict__}
        logger.info(f'set hyperparameters to be {params}')
        latency_p90 = RunModel(model_file=model_file, config=config, queries=queries)
        return latency_p90

    num_workers = []
    for i in range(1, 256):
        if i <= num_cores and num_cores % i == 0:
            num_workers.append(i)
    search_space = {"num_workers": num_workers}
    study = optuna.create_study(study_name='ort_tune_for_qps',
                                direction='maximize', 
                                sampler=optuna.samplers.GridSampler(search_space), 
                                pruner=DuplicatePruner())
    # n_trials: The number of trials. If this argument is set to None, 
    #           there is no limitation on the number of trials.
    # n_jobs: The number of parallel jobs
    study.optimize(objective, n_trials=10, n_jobs=1, 
                    catch=(RuntimeError, optuna.TrialPruned))
    
    # if no completed trial, ValueError(No trials are completed yet) will be thrown.
    best_config = {**study.best_params,
                    **study.best_trial.user_attrs['ort_config']}
    best_result = {'qps': study.best_value}
    return best_config, best_result
