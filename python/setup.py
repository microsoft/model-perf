# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import setuptools
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

setuptools.setup(
    distclass=BinaryDistribution,
    include_package_data=True
)