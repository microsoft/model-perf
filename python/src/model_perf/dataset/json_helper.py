# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import os
from pathlib import Path
from typing import Any, List

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.reshape((1, -1)).tolist()
        return json.JSONEncoder.default(self, obj)


def serialize_tensors(tensors_dict):
    tensors = []
    for key, value in tensors_dict.items():
        if not isinstance(value, np.ndarray):
            raise ValueError("Value needs to be numpy array")
        tensor = {
            "name": key,
            "type": str(value.dtype),
            "shape": value.shape,
            "values": value
        }
        tensors.append(tensor)

    return tensors


def deserialize_tensors(tensors_list: List[Any]):
    processed_tensors = {}
    for tensor in tensors_list:
        # convert shape to 1D array
        tensor["shape"] = tensor["shape"] if len(tensor["shape"]) == 0 else tensor["shape"][0] if type(tensor["shape"][0]) is list else tensor["shape"]
        # reshape values array and convert to list
        tensor["values"] = np.asarray(tensor["values"]).astype(tensor["type"]).reshape(tensor["shape"])

        processed_tensors[tensor["name"]] = tensor["values"]

    return processed_tensors


def serialize_model_inputs(model_inputs, target_folder, target_file_name="inputs.json") -> str:
    model_inputs_path = os.path.join(target_folder, target_file_name)

    # process model inputs to be Tuple <name, type, shape, values>
    processed_model_inputs = []
    for model_input in model_inputs:
        processed_model_input = {"inputs": serialize_tensors(model_input)}
        processed_model_inputs.append(processed_model_input)

    with open(model_inputs_path, "w", encoding="utf-8") as file:
        json.dump(processed_model_inputs, file, ensure_ascii=False, indent=None, cls=NumpyEncoder)

    return model_inputs_path


def deserialize_model_inputs(model_inputs_path: Path) -> List[Any]:
    model_inputs = []

    if not model_inputs_path or not model_inputs_path.exists():
        raise FileNotFoundError("Model inputs file: {0} not found".format(model_inputs_path))

    with open(model_inputs_path) as json_file:
        json_data = json.load(json_file)

        for input_json in json_data:
            processed_json = deserialize_tensors(input_json["inputs"])
            model_inputs.append(processed_json)

    return model_inputs


def deserialize_model_outputs_from_object(json_data: List[Any]) -> List[Any]:
    model_outputs = []

    for output_json in json_data:
        processed_json = deserialize_tensors(output_json["outputs"])
        model_outputs.append(processed_json)

    return model_outputs


def deserialize_model_outputs_from_file(model_outputs_path: Path) -> List[Any]:
    if not model_outputs_path or not model_outputs_path.exists():
        raise FileNotFoundError("Model outputs file: {0} not found".format(model_outputs_path))

    with open(model_outputs_path) as json_file:
        json_data = json.load(json_file)
    return deserialize_model_outputs_from_object(json_data)


def deserialize_model_outputs_from_str(model_outputs_str: str) -> List[Any]:
    json_data = json.loads(model_outputs_str)
    return deserialize_model_outputs_from_object(json_data)
