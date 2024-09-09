from abc import ABC, abstractmethod

import numpy as np

from tma.core.service.exceptions.parameter_error import ParameterError


class MassCalculationStrategy(ABC):
    """
    An abstract base class to define a calculation strategy for mass properties (Mass susceptibility).

    This class provides the framework for calculation strategies based on mass.
    It includes a static method to validate necessary parameters.

    Methods:
    - calculate(data): Abstract method to perform calculation based on the strategy.
    - validate_parameters(mass): Static method to validate mass parameter.
    """

    @abstractmethod
    def calculate(self, data):
        pass

    @staticmethod
    def validate_parameters(mass):
        if mass is None or mass == 0:
            raise ParameterError("Mass is not provided or equals zero.")


class MassCalculation(MassCalculationStrategy):
    """
    A calculation strategy class for mass-based calculations.

    Attributes:
    - mass (float): The mass of the sample.
    - nominal_volume (float): The nominal (reference) volume for the calculation. Defaults to 10.
    """

    def __init__(self, mass, nominal_volume=10):
        """
        Initializes a MassCalculation instance with mass and nominal volume.

        Parameters:
        - mass (float): The mass of the sample.
        - nominal_volume (float): The nominal volume used as a reference in calculations. Defaults to 10.
        """
        self.mass = mass
        self.nominal_volume = nominal_volume

    def calculate(self, data):
        if self.mass == 0:
            raise ValueError("Mass cannot be zero.")
        data_array = np.array(data)
        ratio = self.nominal_volume / self.mass
        return np.round(data_array * ratio / 10, 1)  # we need E-8
