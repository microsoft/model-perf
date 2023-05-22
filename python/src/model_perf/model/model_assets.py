# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pathlib import Path
from typing import List, Union


class ModelAssets:
    def __init__(self, root_dir: Union[str, Path] = '', files: List[str] = [], path: Union[str, Path] = ''):
        if root_dir and len(files) > 0:
            self.model_root_dir = Path(root_dir)
            self.model_files = files
        elif path:
            self.model_root_dir = Path(path).parent
            self.model_files = [Path(path).name]
        else:
            raise ValueError("Model path is not valid")

    def exists(self):
        if not self.model_root_dir.exists():
            raise ValueError(f"Model root directory: {self.model_root_dir} doesn't exist")

        model_paths = [self.model_root_dir / model_file for model_file in self.model_files]
        for model_path in model_paths:
            if not model_path.exists():
                raise ValueError(f"Model path: {model_path} doesn't exist")

        return True

    @property
    def path(self):
        if len(self.model_files) > 1:
            raise RuntimeError(f'{len(self.model_files)} model files in {self.model_root_dir}, there is ambiguity.')
        return self.model_root_dir / self.model_files[0]

    @path.setter
    def path(self, value: Union[str, Path]):
        self.model_root_dir = Path(value).parent
        self.model_files = [Path(value).name]

    @property
    def root_dir(self):
        return self.model_root_dir

    @property
    def files(self):
        return self.model_files
