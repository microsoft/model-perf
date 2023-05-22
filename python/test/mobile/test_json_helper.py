# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from pathlib import Path

import numpy

from model_perf.dataset.json_helper import serialize_model_inputs, deserialize_model_inputs, deserialize_model_outputs_from_file


class TestJSONHelper(unittest.TestCase):

    def test_serialize_array(self):
        model_inputs = [
            {"input_email_body": numpy.array([["Here is the file1", "Here is the file2"], ["Here is the file3", "Here is the file4"]], dtype=numpy.str_)},
            {"input_email_body": numpy.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]], dtype=numpy.float64), 'modelInput': numpy.full((1, 1, 64, 64), 0.5, dtype=numpy.float32)},
            {"input_email_body": numpy.array([["a", "bc", "de", "fg"], ["abc", "de", "你吃饭了吗", "ijkl"]])},
            {"entity_predictions": numpy.array([0.04877366, 0.9512263]), "top_entity_index": numpy.array([1]), "top_entity_score": numpy.array([0.9512263]),
             "top_entity_name": numpy.array(["#file#"]), "reach_threshold": numpy.array([True], dtype=numpy.bool_)}
        ]
        json_path = serialize_model_inputs(model_inputs, ".", "model_inputs.json")
        print(json_path)

    def test_deserialize_input(self):
        json_path = Path(__file__).parent / "test_model_inputs.json"
        model_inputs = deserialize_model_inputs(json_path)
        print(len(model_inputs))

    def test_deserialize_output(self):
        json_path = Path(__file__).parent / "test_model_outputs.json"
        model_outputs = deserialize_model_outputs_from_file(json_path)
        print(len(model_outputs))


if __name__ == '__main__':
    unittest.main()
