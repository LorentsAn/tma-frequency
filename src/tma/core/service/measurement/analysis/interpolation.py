import numpy as np

from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
from scipy.interpolate import lagrange


class InterpolationStrategy(ABC):
    """
    An abstract base class to define interpolation and extrapolation strategies.

    This class provides the framework for interpolation and extrapolation strategies
    by defining abstract methods for interpolation and extrapolation.

    Methods:
    - interpolate(x, y, point): Abstract method for interpolation.
    - extrapolate(x, y, point): Abstract method for extrapolation.
    """

    @abstractmethod
    def interpolate(self, x, y, point):
        """
        Abstract method to interpolate a value at a given point.

        Parameters:
        - x (array-like): The x-coordinates of the data points.
        - y (array-like): The y-coordinates of the data points.
        - point (float): The point at which interpolation is to be performed.

        Returns:
        - The interpolated value at the given point.
        """
        pass

    @abstractmethod
    def extrapolate(self, x, y, point):
        """
        Abstract method to extrapolate a value at a given point.

        Parameters:
        - x (array-like): The x-coordinates of the data points.
        - y (array-like): The y-coordinates of the data points.
        - point (float): The point at which extrapolation is to be performed.

        Returns:
        - The extrapolated value at the given point.
        """
        pass


class LinearInterpolation(InterpolationStrategy):
    """
    A class implementing linear interpolation strategy.

    This class performs linear interpolation and extrapolation based on given data points.
    """

    def interpolate(self, x, y, point):
        f = interp1d(x, y)
        return f(point)

    def extrapolate(self, x, y, point):
        f = interp1d(x, y, fill_value='extrapolate')
        return f(point)


class SplineInterpolation(InterpolationStrategy):
    """
    A class implementing spline interpolation strategy.

    This class performs spline interpolation and extrapolation based on given data points.
    """

    def interpolate(self, x, y, point):
        f = interp1d(x, y, kind='cubic')
        return f(point)

    def extrapolate(self, x, y, point):
        f = interp1d(x, y, kind='cubic', fill_value='extrapolate')
        return f(point)


class LagrangeInterpolation(InterpolationStrategy):
    """
    A class implementing Lagrange polynomial interpolation strategy.

    This class performs Lagrange polynomial interpolation and extrapolation based on given data points.
    """

    def interpolate(self, x, y, point):
        polynomial = lagrange(x, y)
        return polynomial(point)

    def extrapolate(self, x, y, point):
        polynomial = lagrange(x, y)
        return polynomial(point)


class PiecewiseLinearInterpolation(InterpolationStrategy):
    """
    A class implementing piecewise linear interpolation strategy.

    This class performs piecewise linear interpolation and extrapolation based on given data points.
    """

    def interpolate(self, x, y, point):
        f = interp1d(x, y, kind='linear')
        return f(point)

    def extrapolate(self, x, y, point):
        f = interp1d(x, y, kind='linear', fill_value='extrapolate')
        return f(point)


class LeastSquaresInterpolation(InterpolationStrategy):
    """
    A class implementing least squares polynomial interpolation strategy.

    This class performs least squares polynomial interpolation and extrapolation based on given data points.

    Attributes:
    - degree (int): The degree of the polynomial used for interpolation.
    """

    def __init__(self, degree=2):
        self.degree = degree

    def interpolate(self, x, y, point):
        coefs = np.polyfit(x, y, self.degree)
        polynomial_function = np.poly1d(coefs)
        return polynomial_function(point)

    def extrapolate(self, x, y, point):
        coefs = np.polyfit(x, y, self.degree)
        polynomial_function = np.poly1d(coefs)
        return polynomial_function(point)
