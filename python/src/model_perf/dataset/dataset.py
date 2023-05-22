# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
from pathlib import Path

from .json_helper import deserialize_tensors, NumpyEncoder, serialize_tensors


class Dataset:
    def __init__(self, inputs=None, outputs=None):
        self.inputs = []
        if inputs and len(inputs) > 0:
            self.inputs = inputs

        self.outputs = []
        if outputs and len(outputs) > 0:
            self.outputs = outputs

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        input = None
        if self.inputs and len(self.inputs) > idx:
            input = self.inputs[idx]

        output = None
        if self.outputs and len(self.outputs) > idx:
            output = self.outputs[idx]

        return input, output

    def from_json(self, json_path: Path):
        if not json_path or not json_path.exists():
            raise FileNotFoundError("JSON file: {0} not found".format(json_path))

        # clear inputs and outputs
        self.inputs = []
        self.outputs = []

        with open(json_path) as json_file:
            json_data = json.load(json_file)

            for json_entry in json_data:
                if "inputs" in json_entry:
                    processed_tensors = deserialize_tensors(json_entry["inputs"])
                    self.inputs.append(processed_tensors)

                if "outputs" in json_entry:
                    processed_tensors = deserialize_tensors(json_entry["outputs"])
                    self.outputs.append(processed_tensors)

    def to_json(self, target_path: Path):
        # process tensor to be Tuple <name, type, shape, values>
        json_data = []
        array_len = len(self.inputs) if len(self.inputs) > len(self.outputs) else len(self.outputs)

        for i in range(array_len):
            input, output = self[i]
            processed_data = {}
            if input:
                processed_data["inputs"] = serialize_tensors(input)

            if output:
                processed_data["outputs"] = serialize_tensors(output)

            json_data.append(processed_data)

        with open(target_path, "w", encoding="utf-8") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=2, cls=NumpyEncoder)
