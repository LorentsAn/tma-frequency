import numpy as np
from abc import ABC, abstractmethod

from scipy.signal import argrelextrema

from tma.core.service.measurement.analysis.outlier_detection import ComparisonOutlierDetection
from tma.core.service.measurement.analysis.second_derivative import SecondDerivativeCalculation, \
    FirstDerivativeCalculation, ThirdDerivativeCalculation


class CuriePointCalculationStrategy(ABC):
    """
    An abstract base class to define a calculation strategy for the Curie point.

    This class provides the framework for calculation strategies based on smoothing and differentiation of magnetization data.
    """

    @abstractmethod
    def calculate(self, temperatures, magnetization):
        """
        Abstract method to perform calculation based on the strategy.

        Parameters:
        - temperatures (iterable): The temperature data points.
        - magnetization (iterable): The magnetization data points corresponding to the temperatures.

        Returns:
        - The result of the calculation as modified by the specific strategy.
        """
        pass


class MaxSecondDerivativePointCalculation(CuriePointCalculationStrategy):
    """
    A calculation strategy class for Curie point calculation based on the second derivative of the magnetization.

    Attributes:
    - smoothness_degree (int): The degree of smoothing for the Savitzky-Golay filter.
    - eval_range (tuple): The range of temperature values to evaluate for the Curie point.
    """

    def __init__(self, smoothness_degree=2, threshold=0):
        """
        Initializes a CuriePointCalculation instance with smoothness degree and evaluation range.

        Parameters:
        - smoothness_degree (int): The degree of smoothing (window length) for the Savitzky-Golay filter.
        - eval_range (tuple): The tuple representing the range (min, max) of temperatures to evaluate the Curie point.
        """
        self.smoothness_degree = smoothness_degree
        self.threshold = threshold

    def calculate(self, temperatures, magnetization):
        """
        Calculate the Curie point based on the second derivative of the magnetization data after smoothing.

        Returns:
        - curie_point (float): The calculated Curie point temperature.
        """
        # Validate the smoothness degree is positive and odd
        if self.smoothness_degree <= 0:
            raise ValueError("Smoothness degree must be a positive number.")

        temperatures = np.array(temperatures)
        magnetization = np.array(magnetization)

        second_derivative_calculation = SecondDerivativeCalculation(sigma=self.smoothness_degree)
        x_values, second_derivative = second_derivative_calculation.calculate(temperatures, magnetization)

        third_derivative_calculation = ThirdDerivativeCalculation(sigma=self.smoothness_degree)
        x_values, third_derivative = third_derivative_calculation.calculate(temperatures, magnetization)

        zero_crossings = np.where(np.diff(np.sign(third_derivative)))[0]

        significant_crossings = []

        for i in range(len(zero_crossings) - 1):
            start_index = zero_crossings[i]
            end_index = zero_crossings[i + 1]
            max_derivative = np.max(np.abs(second_derivative[start_index:end_index]))
            if third_derivative[start_index] > 0 and max_derivative > self.threshold:
                significant_crossings.append(zero_crossings[i])

        significant_temperatures = temperatures[significant_crossings]
        significant_magnetization = magnetization[significant_crossings]

        return significant_temperatures, significant_magnetization


class MaxFirstDerivativePointCalculation(CuriePointCalculationStrategy):
    """
    A calculation strategy class for Curie point calculation based on the second derivative of the magnetization.

    Attributes:
    - smoothness_degree (int): The degree of smoothing for the Savitzky-Golay filter.
    - eval_range (tuple): The range of temperature values to evaluate for the Curie point.
    """

    def __init__(self, smoothness_degree=2, threshold=0):
        """
        Initializes a CuriePointCalculation instance with smoothness degree and evaluation range.

        Parameters:
        - smoothness_degree (int): The degree of smoothing (window length) for the Savitzky-Golay filter.
        - eval_range (tuple): The tuple representing the range (min, max) of temperatures to evaluate the Curie point.
        """
        self.smoothness_degree = smoothness_degree
        self.threshold = threshold

    def calculate(self, temperatures, magnetization):
        """
        Calculate the Curie point based on the second derivative of the magnetization data after smoothing.

        Returns:
        - curie_point (float): The calculated Curie point temperature.
        """
        if self.smoothness_degree <= 0:
            raise ValueError("Smoothness degree must be a positive number.")

        temperatures = np.array(temperatures)
        magnetization = np.array(magnetization)

        first_derivative_calculation = FirstDerivativeCalculation(sigma=self.smoothness_degree)
        x_values, first_derivative = first_derivative_calculation.calculate(temperatures, magnetization)

        second_derivative_calculation = SecondDerivativeCalculation(sigma=self.smoothness_degree)
        x_values, second_derivative = second_derivative_calculation.calculate(temperatures, magnetization)

        zero_crossings = np.where(np.diff(np.sign(second_derivative)))[0]

        significant_crossings = []

        for i in range(len(zero_crossings) - 1):
            start_index = zero_crossings[i]
            end_index = zero_crossings[i + 1]
            max_derivative = np.max(np.abs(first_derivative[start_index:end_index]))
            if max_derivative > self.threshold:
                significant_crossings.append(zero_crossings[i])

        significant_temperatures = temperatures[significant_crossings]
        significant_magnetization = magnetization[significant_crossings]

        return significant_temperatures, significant_magnetization


class InflectionPointCalculation(CuriePointCalculationStrategy):
    def __init__(self, smoothness_degree=2, threshold=0):
        """
        Initializes a CuriePointCalculation instance with smoothness degree and evaluation range.

        Parameters:
        - smoothness_degree (int): The degree of smoothing (window length) for the Savitzky-Golay filter.
        - eval_range (tuple): The tuple representing the range (min, max) of temperatures to evaluate the Curie point.
        """
        self.smoothness_degree = smoothness_degree
        self.threshold = threshold

    def calculate(self, temperatures, magnetization):
        """
        Calculate the Curie point based on the second derivative of the magnetization data after smoothing.

        Returns:
        - curie_point (float): The calculated Curie point temperature.
        """

        temperatures = np.array(temperatures)
        magnetization = np.array(magnetization)

        second_derivative_calculation = SecondDerivativeCalculation(self.smoothness_degree)
        temp, second_derivative = second_derivative_calculation.calculate(temperatures, magnetization)

        sign_changes = np.array(np.where(np.diff(np.sign(second_derivative)) != 0)[0])

        second_derivative_calculation = ComparisonOutlierDetection(self.threshold)
        significant_temps, significant_mags = second_derivative_calculation.detect(temperatures,
                                                                                   second_derivative)

        temp_result, magnetization_result = [], []
        temperatures = np.array(temperatures)
        second_derivative = np.array(second_derivative)
        for temp, magnetization_value, index in zip(temperatures[sign_changes], second_derivative[sign_changes],
                                                    sign_changes):
            if temp in significant_temps and magnetization_value in significant_mags:
                temp_result.append(temp)
                magnetization_result.append(magnetization[index])

        return temp_result, magnetization_result
