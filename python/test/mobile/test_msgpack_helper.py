# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from pathlib import Path

import numpy
from model_perf.dataset.msgpack_helper import serialize_dataset, deserialize_dataset


class TestMsgpackHelper(unittest.TestCase):
    def test_serialize_inputs(self):
        model_inputs = [
            {"input_email_body": numpy.array([["Here is the file1", "Here is the file2"], ["Here is the file3", "Here is the file4"]], dtype=numpy.str_)},
            {"input_email_body": numpy.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]], dtype=numpy.float64), 'modelInput': numpy.full((1, 1, 64, 64), 0.5, dtype=numpy.float32)},
            {"input_email_body": numpy.array([["a", "bc", "de", "fg"], ["abc", "de", "你吃饭了吗", "ijkl"]])},
            {"entity_predictions": numpy.array([0.04877366, 0.9512263]), "top_entity_index": numpy.array([1]), "top_entity_score": numpy.array([0.9512263]), "top_entity_name": numpy.array(["#file#"]), "reach_threshold": numpy.array([True], dtype=numpy.bool_)}]
        inputs_path = serialize_dataset(model_inputs, ".", "model_inputs.msgpack")
        print(inputs_path)

    @unittest.skip('ignore')
    def test_deserialize_inputs(self):
        inputs_path = Path(__file__).parent / "model_outputs.msgpack"
        model_inputs = deserialize_dataset(inputs_path)
        print(model_inputs)


if __name__ == '__main__':
    unittest.main()
