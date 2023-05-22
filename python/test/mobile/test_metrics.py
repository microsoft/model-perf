# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from pathlib import Path

import numpy

from model_perf.metrics import accuracy_score, confusion_matrix
from model_perf.utils import extract_latency_percentile


class TestMetrics(unittest.TestCase):

    def test_accuracy_score(self):
        expected_outputs = [{"sum": numpy.array([[2.2, 4.4]], dtype=numpy.float32)},
                            {"sum": numpy.array([[6.6, 8.8]], dtype=numpy.float32)},
                            {"sum": numpy.array([[11.0, 13.2]], dtype=numpy.float32)}]
        actual_output = [{'sum': numpy.array([[2.2, 4.4]])},
                         {'sum': numpy.array([[6.6, 8.8]])},
                         {'sum': numpy.array([[11.0, 13.2]])}]
        ret = accuracy_score(expected_outputs, actual_output)
        print(ret)

    @unittest.skip("Need valid log path")
    def test_utils(self):
        text = Path('../test_log.txt').read_text()
        percent = extract_latency_percentile(text)
        print(percent)

    def test_confusion_matrix(self):
        expe = [2, 0, 2, 2, 0, 1]
        pred = [0, 0, 2, 2, 0, 2]
        print(confusion_matrix(expe, pred, normalize=None))
        print(confusion_matrix(expe, pred, normalize='expected'))
        print(confusion_matrix(expe, pred, normalize='predicted'))
        print(confusion_matrix(expe, pred, normalize='all'))

        expe = ["cat", "ant", "cat", "cat", "ant", "bird"]
        pred = ["ant", "ant", "cat", "cat", "ant", "cat"]
        print(confusion_matrix(expe, pred, labels=["ant", "bird", "cat"], normalize=None))
        print(confusion_matrix(expe, pred, labels=["cat", "bird", "ant"], normalize=None))


if __name__ == '__main__':
    unittest.main()
