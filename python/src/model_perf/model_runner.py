# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import Dict, Any, List, Tuple, Union
from pathlib import Path
from .model import ModelAssets


class ModelRunner:
    def __init__(self, model_assets: ModelAssets, output_dir: Union[str, Path] = ''):
        # output_dir
        output_dir = Path(output_dir) if output_dir else Path().resolve() / 'output'
        self.output_dir = output_dir
        # model
        if not model_assets or not model_assets.exists():
            raise ValueError("Model is not valid")
        self.model = model_assets

    def predict_and_benchmark(self, inputs: List[Any], config: Dict[str, Any]={}) -> Tuple[List[Any], List[Any]]:
        raise NotImplementedError

    def predict(self, inputs: List[Any], config: Dict[str, Any]={}) -> List[Any]:
        raise NotImplementedError

    def benchmark(self, inputs, config: Dict[str, Any]={}) -> List[Any]:
        raise NotImplementedError
