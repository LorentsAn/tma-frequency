from abc import ABC, abstractmethod

import numpy as np

from tma.core.service.exceptions.parameter_error import ParameterError


class BulkCalculationStrategy(ABC):
    """
    An abstract base class to define a calculation strategy for bulk susceptibility.

    This class provides the framework for calculation strategies based on different parameters such as volume and mass.
    It includes a static method to validate necessary parameters based on the chosen strategy.
    """

    nominal_volume = 9.99363

    @abstractmethod
    def calculate(self, data):
        """
        Abstract method to perform calculation based on the strategy.

        Parameters:
        - data (iterable): The data on which the calculation is to be performed.

        Returns:
        - The result of the calculation as modified by the specific strategy.

        Raises:
        - NotImplementedError: If the method is not implemented by the derived class.
        """
        pass

    @staticmethod
    def validate_parameters(strategy, actual_volume, mass, density):
        """
        Validates the parameters required for the calculation based on the selected strategy.

        Parameters:
        - strategy (str): The calculation strategy ('volume' or 'mass').
        - actual_volume (float): The actual volume value for the volume calculation strategy.
        - mass (float): The mass value for the mass calculation strategy.
        - density (float): The density value required for the mass calculation strategy.

        Raises:
        - ParameterError: If any required parameter is not provided or invalid.
        """
        if strategy == 'volume':
            if actual_volume is None or actual_volume == 0:
                raise ParameterError("Volume is not provided or equals zero.")
        elif strategy == 'mass':
            if mass is None or mass == 0:
                raise ParameterError("Mass is not provided or equals zero.")
            if density is None:
                raise ParameterError("Density is not provided.")


class VolumeCalculation(BulkCalculationStrategy):
    """
    A calculation strategy class for volume-based calculations.

    Attributes:
    - actual_volume (float): The actual volume of the sample.
    - nominal_volume (float): The nominal (reference) volume for the calculation. Defaults to 10.
    """

    def __init__(self, actual_volume, nominal_volume=None):
        """
        Initializes a VolumeCalculation instance with actual and nominal volumes.

        Parameters:
        - actual_volume (float): The actual volume of the sample.
        - nominal_volume (float): The nominal volume used as a reference in calculations. Defaults to 10.
        """
        if nominal_volume is None:
            nominal_volume = self.nominal_volume
        self.actual_volume = actual_volume
        self.nominal_volume = nominal_volume

    def calculate(self, data):
        if self.actual_volume == 0:
            raise ValueError("Actual volume cannot be zero.")
        data_array = np.array(data)
        ratio = self.nominal_volume / self.actual_volume
        return np.round(data_array * ratio, 3)


class MassSusceptibilityCalculation(BulkCalculationStrategy):
    """
    A calculation strategy class for mass susceptibility calculations.

    Attributes:
    - mass (float): The mass of the sample.
    - density (float): The density of the sample.
    - nominal_volume (float): The nominal (reference) volume for the calculation. Defaults to 10.
    """

    def __init__(self, mass, density, nominal_volume=None):
        """
        Initializes a MassSusceptibilityCalculation instance with mass, density, and nominal volume.

        Parameters:
        - mass (float): The mass of the sample.
        - density (float): The density of the sample.
        - nominal_volume (float): The nominal volume used as a reference in calculations. Defaults to 10.
        """
        if nominal_volume is None:
            nominal_volume = self.nominal_volume
        self.mass = mass
        self.density = density
        self.nominal_volume = nominal_volume

    def calculate(self, data):
        if self.mass == 0:
            raise ValueError("Mass cannot be zero.")
        data_array = np.array(data)
        ratio = (self.nominal_volume * self.density) / self.mass
        return np.round(data_array * ratio, 1)
