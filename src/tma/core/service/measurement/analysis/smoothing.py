from abc import ABC, abstractmethod

import numpy as np


class SmoothingStrategy(ABC):
    """
    An abstract base class to define a smoothing strategy.

    This class provides the framework for smoothing strategies by defining an abstract method for smoothing.

    Methods:
    - smooth(data): Abstract method to perform smoothing.

    """

    @abstractmethod
    def smooth(self, data):
        pass


class MovingAverageSmoothing(SmoothingStrategy):
    """
    A class implementing moving average smoothing strategy.

    Attributes:
    - window_size (int): The size of the moving average window. Defaults to 5.
    """

    def __init__(self, window_size=5):
        """
        Initializes a MovingAverageSmoothing instance with the specified window size.

        Parameters:
        - window_size (int): The size of the moving average window. Defaults to 5.
        """
        self.window_size = window_size

    def smooth(self, data):
        weights = np.ones(self.window_size) / self.window_size
        smoothed_data = np.convolve(data, weights, mode='valid')
        return np.round(smoothed_data, 3)
