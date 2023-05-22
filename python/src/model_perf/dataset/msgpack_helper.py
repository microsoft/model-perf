# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
from pathlib import Path
from typing import Any, List

import msgpack
import msgpack_numpy as m
import base64


def serialize_dataset(dataset, target_folder, target_file_name="dataset.msgpack") -> str:
    dataset_path = os.path.join(target_folder, target_file_name)

    with open(dataset_path, "wb") as file:
        packed = msgpack.packb(dataset, default=m.encode)
        file.write(packed)

    return dataset_path


def deserialize_dataset(dataset: Path) -> List[Any]:
    if not dataset or not dataset.exists():
        raise FileNotFoundError("Dataset file: {0} not found".format(dataset))

    with open(dataset, "rb") as file:
        byte_data = file.read()
        unpacked_data = msgpack.unpackb(byte_data, object_hook=m.decode)

    return unpacked_data

def deserialize_from_base64(input_base64: str):
    input_bytes = base64.b64decode(input_base64)
    unpacked_data = msgpack.unpackb(input_bytes, object_hook=m.decode)
    return unpacked_data