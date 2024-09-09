import unittest

import numpy as np

from tma.core.service.measurement.analysis.outlier_detection import ComparisonOutlierDetection


class TestThresholdOutlierDetection(unittest.TestCase):
    def test_basic_functionality(self):
        tod = ComparisonOutlierDetection(threshold=10)
        x_values = [1, 2, 3, 4, 5]
        y_values = [10, 20, 15, 25, 10]
        expected_outliers_x = np.array([2, 4, 5])
        expected_outliers_y = np.array([20, 25, 10])
        outlier_x, outlier_y = tod.detect(x_values, y_values)
        np.testing.assert_array_equal(outlier_x, expected_outliers_x)
        np.testing.assert_array_equal(outlier_y, expected_outliers_y)

    def test_no_outliers(self):
        tod = ComparisonOutlierDetection(threshold=11)
        x_values = [1, 2, 3, 4, 5]
        y_values = [10, 20, 30, 40, 50]
        expected_outliers_x = np.array([])
        expected_outliers_y = np.array([])
        outlier_x, outlier_y = tod.detect(x_values, y_values)
        np.testing.assert_array_equal(outlier_x, expected_outliers_x)
        np.testing.assert_array_equal(outlier_y, expected_outliers_y)

    def test_all_outliers(self):
        tod = ComparisonOutlierDetection(threshold=1)
        x_values = [1, 2, 3, 4]
        y_values = [1, 3, 6, 10]
        expected_outliers_x = np.array([2, 3, 4])
        expected_outliers_y = np.array([3, 6, 10])
        outlier_x, outlier_y = tod.detect(x_values, y_values)
        np.testing.assert_array_equal(outlier_x, expected_outliers_x)
        np.testing.assert_array_equal(outlier_y, expected_outliers_y)

    def test_single_element(self):
        tod = ComparisonOutlierDetection(threshold=1)
        x_values = [1]
        y_values = [100]
        expected_outliers_x = np.array([])
        expected_outliers_y = np.array([])
        outlier_x, outlier_y = tod.detect(x_values, y_values)
        np.testing.assert_array_equal(outlier_x, expected_outliers_x)
        np.testing.assert_array_equal(outlier_y, expected_outliers_y)

    def test_input_validation(self):
        tod = ComparisonOutlierDetection(threshold=1)
        x_values = [1, 2, 3]
        y_values = [100]
        with self.assertRaises(ValueError):
            tod.detect(x_values, y_values)
