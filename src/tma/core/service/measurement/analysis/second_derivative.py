from abc import ABC, abstractmethod

import numpy as np
from scipy.ndimage import gaussian_filter1d


class DerivativeCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, temperatures, magnetization):
        """
        Abstract method to perform derivative calculation based on the strategy.

        Parameters:
        - temperatures (iterable): The temperature data points.
        - magnetization (iterable): The magnetization data points corresponding to the temperatures.

        Returns:
        - A tuple of temperatures and the calculated derivative.
        """
        pass


class FirstDerivativeCalculation(DerivativeCalculationStrategy):
    def __init__(self, sigma=2):
        """
        Initializes the derivative calculation with a smoothing factor.

        Parameters:
        - sigma (int): The degree of smoothing for the Gaussian filter.
        """
        self.sigma = sigma

    def calculate(self, x_values, y_values):
        """
        Calculate the first derivative of magnetization data after smoothing.

        Returns:
        - A tuple of x_values and the calculated first derivative.
        """
        # Validate the smoothness degree is positive and odd
        if self.sigma <= 0:
            raise ValueError("Smoothness degree must be a positive number.")

        dy = np.gradient(y_values, x_values)
        dy = gaussian_filter1d(dy, sigma=self.sigma)

        return x_values, dy


class SecondDerivativeCalculation(DerivativeCalculationStrategy):
    def __init__(self, sigma=2):
        """
        Initializes the derivative calculation with a smoothing factor.

        Parameters:
        - sigma (int): The degree of smoothing for the Gaussian filter.
        """
        self.sigma = sigma

    def calculate(self, x_values, y_values):
        """
        Calculate the second derivative of magnetization data after smoothing.

        Returns:
        - A tuple of x_values and the calculated second derivative.
        """
        if self.sigma <= 0:
            raise ValueError("Smoothness degree must be a positive number.")

        dy = np.gradient(y_values, x_values)
        d2y = np.gradient(dy, x_values)
        d2y = gaussian_filter1d(d2y, sigma=self.sigma)

        return x_values, d2y


class ThirdDerivativeCalculation(DerivativeCalculationStrategy):
    def __init__(self, sigma=2):
        """
        Initializes the derivative calculation with a smoothing factor.

        Parameters:
        - sigma (int): The degree of smoothing for the Gaussian filter.
        """
        self.sigma = sigma

    def calculate(self, x_values, y_values):
        """
        Calculate the third derivative of magnetization data after smoothing.

        Returns:
        - A tuple of x_values and the calculated third derivative.
        """
        if self.sigma <= 0:
            raise ValueError("Smoothness degree must be a positive number.")

        dy = np.gradient(y_values, x_values)
        d2y = np.gradient(dy, x_values)
        d3y = np.gradient(d2y, x_values)
        d3y = gaussian_filter1d(d3y, sigma=self.sigma)

        return x_values, d3y
