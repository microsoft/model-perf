# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Metric and scoring

Follow sklearn conventions to calculate various metrics. Refer to:
    * https://scikit-learn.org/stable/modules/model_evaluation.html
"""
import math
import numpy


def equal_func(expected, predicted, float_rel_tol=0.01, float_abs_tol=0.0, verbose=True) -> bool:
    """
    Function for performing comparisons between two variables.
    """
    if not isinstance(expected, type(predicted)):
        if verbose:
            print("Types not equal: expected: {0} != actual: {1}".format(type(expected), type(predicted)))
        return False

    if isinstance(expected, (int, numpy.integer, bool, numpy.bool_, str, numpy.str_)):
        return expected == predicted
    elif isinstance(expected, (float, numpy.floating)):
        return math.isclose(expected, predicted, rel_tol=float_rel_tol, abs_tol=float_abs_tol)
    elif isinstance(expected, list):
        if len(expected) != len(predicted):
            return False
        for i in range(len(expected)):
            if not equal_func(expected[i], predicted[i], float_rel_tol, float_abs_tol, verbose):
                if verbose:
                    print("Expected: {0} != actual: {1}".format(expected[i], predicted[i]))
                return False
        return True
    elif isinstance(expected, numpy.ndarray):
        total_size = expected.size
        expected_list = expected.reshape(1, -1).tolist()[0]
        actual_list = predicted.reshape(1, -1).tolist()[0]
        if len(expected_list) != len(actual_list):
            return False
        for i in range(total_size):
            if not equal_func(expected_list[i], actual_list[i], float_rel_tol, float_abs_tol, verbose):
                if verbose:
                    print("Expected: {0} != actual: {1}".format(expected_list[i], actual_list[i]))
                return False
        return True
    elif isinstance(expected, dict):
        for key, expected_values in expected.items():
            actual_values = predicted[key]
            if not equal_func(expected_values, actual_values, float_rel_tol, float_abs_tol, verbose):
                if verbose:
                    print("{0}: expected: {1} != actual: {2}".format(key, expected_values, actual_values))
                return False
        return True
    else:
        return False


def accuracy_score(expected, predicted, equal_function=None, normalize: bool = True):
    """
    Compare model predictions with expected outputs.
    """
    if len(expected) != len(predicted):
        return False

    total_cnt = len(expected)
    equal_cnt = 0

    # compare each output
    for i in range(len(expected)):
        # tensors in dictionary
        expected_tensors = expected[i]
        actual_tensors = predicted[i]

        # compare tensors in each output
        tensors_equal = True
        compare_func = equal_function if equal_function is not None else equal_func
        if not compare_func(expected_tensors, actual_tensors):
            tensors_equal = False

        if tensors_equal:
            equal_cnt += 1

    accuracy = 0.0 if total_cnt == 0 else equal_cnt / total_cnt

    if normalize:
        return accuracy
    else:
        return equal_cnt


def confusion_matrix(expected, predicted, labels=None, normalize=None):
    """
    Compute confusion matrix to evaluate the accuracy of a classification.
    """
    expected = numpy.asarray(expected)
    predicted = numpy.asarray(predicted)

    # check consistency
    if expected.size != predicted.size:
        raise ValueError("Length of expected and predicted samples are not equal.")

    if labels is None:
        labels = numpy.array(sorted(set(numpy.concatenate((expected, predicted)))))
    else:
        labels = numpy.asarray(labels)
        n_labels = labels.size
        if n_labels == 0:
            raise ValueError("'labels' should contains at least one label.")
        elif expected.size == 0:
            return numpy.zeros((n_labels, n_labels), dtype=int)
        elif len(numpy.intersect1d(expected, labels)) == 0:
            raise ValueError("At least one label specified must be in expected")

    if normalize not in ["expected", "predicted", "all", None]:
        raise ValueError("normalize must be one of {'expected', 'predicted', 'all', None}")

    num_classes = labels.size

    # If labels are not consecutive integers starting from zero, then
    # expected and predicted must be converted into index form
    need_index_conversion = not (
            labels.dtype.kind in {"i", "u", "b"}
            and numpy.all(labels == numpy.arange(num_classes))
            and numpy.min(expected) >= 0
            and numpy.min(predicted) >= 0
    )
    if need_index_conversion:
        label_to_ind = {y: x for x, y in enumerate(labels)}
        predicted = numpy.array([label_to_ind.get(x, num_classes + 1) for x in predicted])
        expected = numpy.array([label_to_ind.get(x, num_classes + 1) for x in expected])

    # intersect predicted, expected with labels, eliminate items not in labels
    ind = numpy.logical_and(predicted < num_classes, expected < num_classes)
    if not numpy.all(ind):
        predicted = predicted[ind]
        expected = expected[ind]

    # calculate confusion matrix
    conf_matrix = numpy.zeros((num_classes, num_classes), dtype=int)
    for i in range(len(expected)):
        conf_matrix[expected[i]][predicted[i]] += 1

    with numpy.errstate(all="ignore"):
        if normalize == "expected":
            conf_matrix = conf_matrix / conf_matrix.sum(axis=1, keepdims=True)
        elif normalize == "predicted":
            conf_matrix = conf_matrix / conf_matrix.sum(axis=0, keepdims=True)
        elif normalize == "all":
            conf_matrix = conf_matrix / conf_matrix.sum()
        conf_matrix = numpy.nan_to_num(conf_matrix)

    return conf_matrix
