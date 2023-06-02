# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import setuptools
from setuptools.dist import Distribution
from glob import glob


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

setuptools.setup(
    distclass=BinaryDistribution,
    include_package_data=True,
    data_files=[("model_perf/cpp/load_gen", glob('src/model_perf/cpp/load_gen/*.*', recursive=True)),
                ("model_perf/cpp/test_app_common", glob('src/model_perf/cpp/test_app_common/*.*', recursive=True)),
                ("model_perf/cpp/test_app_common/ort", glob('src/model_perf/cpp/test_app_common/ort/*.*', recursive=True)),
                ("model_perf/third_party", glob('src/model_perf/third_party/*.*', recursive=True))],
)
