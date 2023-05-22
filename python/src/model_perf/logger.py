# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import logging
import sys

logger = logging.getLogger('model_perf')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
