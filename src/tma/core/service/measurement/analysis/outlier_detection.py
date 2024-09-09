from abc import abstractmethod, ABC

import numpy as np


class OutlierDetectionStrategy(ABC):
    @abstractmethod
    def detect(self, x_values, y_values):
        """
        Abstract method to perform outlier detection based on the strategy.

        Parameters:
        - x_values (iterable): The x-axis data points.
        - y_values (iterable): The y-axis data points corresponding to the x_values.

        Returns:
        - A tuple of x_values and y_values that are considered outliers.
        """
        pass


class ComparisonOutlierDetection(OutlierDetectionStrategy):
    def __init__(self, threshold):
        """
        Initializes the outlier detection with a numerical threshold.

        Parameters:
        - threshold (float): The value above which a y-value is considered an outlier.
        """
        self.threshold = threshold

    def detect(self, x_values, y_values):
        """
        Detects outliers in y_values that are above a specified threshold.

        Returns:
        - A tuple of x_values and y_values that are considered outliers.
        """
        if len(x_values) != len(y_values):
            raise ValueError("Arrays have different sizes")

        x_values = np.array(x_values)
        y_values = np.array(y_values)

        deviations = np.abs(np.diff(y_values))

        significant_deviations = deviations >= self.threshold
        outlier_indices = np.where(significant_deviations)[0] + 1

        outlier_x = x_values[outlier_indices]
        outlier_y = y_values[outlier_indices]

        return outlier_x, outlier_y


class MeanOutlierDetection(OutlierDetectionStrategy):
    def __init__(self, threshold):
        """
        Initializes the outlier detection with a numerical threshold.

        Parameters:
        - threshold (float): The value above which a y-value is considered an outlier.
        """
        self.threshold = threshold

    def detect(self, x_values, y_values):
        """
        Detects outliers in y_values that are above a specified threshold.

        Returns:
        - A tuple of x_values and y_values that are considered outliers.
        """
        if len(x_values) != len(y_values):
            raise ValueError("Arrays have different sizes")

        x_values = np.array(x_values)
        y_values = np.array(y_values)

        mean_y = np.mean(y_values)

        deviations = np.abs(y_values - mean_y)
        outliers = np.where(deviations >= self.threshold)[0]

        outlier_x = x_values[outliers]
        outlier_y = y_values[outliers]

        return outlier_x, outlier_y


class StandardDeviationOutlierDetection(OutlierDetectionStrategy):
    def __init__(self, threshold):
        """
        Initializes the outlier detection based on standard deviation.

        Parameters:
        - threshold (float): The number of standard deviations away from the mean
                               a y-value needs to be considered an outlier.
        """
        self.threshold = threshold

    def detect(self, x_values, y_values):
        """
        Detects outliers in y_values that are a specified number of standard deviations
        away from the mean of y_values.

        Returns:
        - A tuple of x_values and y_values that are considered outliers.
        """
        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have the same number of elements")

        x_values = np.array(x_values)
        y_values = np.array(y_values)

        mean_y = np.mean(y_values)
        std_dev = np.std(y_values)

        deviations = np.abs(y_values - mean_y)
        outliers = np.where(deviations > self.threshold * std_dev)[0]

        outlier_x = x_values[outliers]
        outlier_y = y_values[outliers]

        return outlier_x, outlier_y


class MovingAverageOutlierDetection(OutlierDetectionStrategy):
    def __init__(self, window_size, threshold):
        """
        Initializes the outlier detection with a moving average window size and a threshold.

        Parameters:
        - window_size (int): The size of the moving average window.
        - threshold (float): The threshold for determining outliers from the moving average.
        """
        self.window_size = window_size
        self.threshold = threshold

    def detect(self, x_values, y_values):
        """
        Detects outliers by comparing y-values to a moving average. Y-values significantly
        diverging from their moving average by more than the threshold are considered outliers.

        Returns:
        - A tuple of x_values and y_values that are considered outliers.
        """
        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have the same number of elements")

        x_values = np.array(x_values)
        y_values = np.array(y_values)

        weights = np.ones(self.window_size) / self.window_size
        moving_avg = np.convolve(y_values, weights, mode='valid')

        adjusted_x_values = x_values[self.window_size - 1:]

        deviations = np.abs(y_values[self.window_size - 1:] - moving_avg)

        outliers = np.where(deviations > self.threshold)[0]

        outlier_x = adjusted_x_values[outliers]
        outlier_y = y_values[self.window_size - 1:][outliers]

        return outlier_x, outlier_y
