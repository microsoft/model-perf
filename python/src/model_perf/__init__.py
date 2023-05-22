# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

__version__ = '0.1rc5'

import platform
from packaging import version
import os
import platform

# add the lib folder to env
if platform.system() == 'Windows':
    dll_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib'))
    dll_paths = [dll_path, os.environ['PATH']]
    os.environ['PATH'] = ';'.join(dll_paths)
else:
    pass
    #raise NotImplementedError(f'platform {platform.system()} is not supported')

from .globals import set_model_cache_dir, get_model_cache_dir
