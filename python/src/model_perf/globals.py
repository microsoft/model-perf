# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from ast import Global
import os

MODEL_CACHE_DIR = '.perftools/models'


def set_model_cache_dir(p):
    global MODEL_CACHE_DIR
    MODEL_CACHE_DIR = os.path.abspath(p)


def get_model_cache_dir():
    global MODEL_CACHE_DIR
    return MODEL_CACHE_DIR
