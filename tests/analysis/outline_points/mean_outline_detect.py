import unittest
import numpy as np

from tma.core.service.measurement.analysis.outlier_detection import MeanOutlierDetection


class TestMeanOutlierDetection(unittest.TestCase):
    def test_equal_lengths(self):
        """
        Test that the method raises an error if x_values and y_values have different lengths.
        """
        mod = MeanOutlierDetection(threshold=2)
        x_values = [0, 1, 2]
        y_values = [1, 2]  # Shorter list
        with self.assertRaises(ValueError):
            mod.detect(x_values, y_values)

    def test_no_outliers(self):
        """
        Test that the method returns empty arrays when there are no outliers.
        """
        mod = MeanOutlierDetection(threshold=2)
        x_values = np.linspace(0, 10, 10)
        y_values = np.array([1] * 10)  # All values are the same
        outlier_x, outlier_y = mod.detect(x_values, y_values)
        self.assertEqual(len(outlier_x), 0)
        self.assertEqual(len(outlier_y), 0)

    def test_detection_of_outliers(self):
        """
        Test that the method correctly identifies outliers.
        """
        mod = MeanOutlierDetection(threshold=1)
        x_values = np.array([0, 1, 2, 3, 4])
        y_values = np.array([0, 2, 0, 10, 0])  # '10' is a clear outlier
        outlier_x, outlier_y = mod.detect(x_values, y_values)
        self.assertTrue((outlier_x == [0, 2, 3, 4]).all())
        self.assertTrue((outlier_y == [0, 0, 10, 0]).all())

    def test_first_outline(self):
        """
        Test that the method correctly identifies outliers.
        """
        mod = MeanOutlierDetection(threshold=4)
        x_values = np.array([0, 1, 2, 3, 4, 5])
        y_values = np.array([10, 3, 4, 3.5, 6, 4])  # '10' is a clear outlier
        outlier_x, outlier_y = mod.detect(x_values, y_values)
        self.assertTrue((outlier_x == [0]).all())
        self.assertTrue((outlier_y == [10]).all())

if __name__ == '__main__':
    unittest.main()
