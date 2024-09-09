from typing import Optional, Dict

import numpy as np

from tma.core.service.measurement.analysis.bulk_calculation import BulkCalculationStrategy, VolumeCalculation, \
    MassSusceptibilityCalculation
from tma.core.service.measurement.analysis.curie_calculation import CuriePointCalculationStrategy
from tma.core.service.measurement.analysis.interpolation import InterpolationStrategy, LinearInterpolation, \
    SplineInterpolation, LagrangeInterpolation, PiecewiseLinearInterpolation, LeastSquaresInterpolation
from tma.core.service.measurement.analysis.mass_calculation import MassCalculationStrategy
from tma.core.service.measurement.analysis.outlier_detection import OutlierDetectionStrategy
from tma.core.service.measurement.analysis.second_derivative import DerivativeCalculationStrategy
from tma.core.service.measurement.analysis.smoothing import SmoothingStrategy


class DataCalculation:
    def __init__(self):
        self.interpolation_strategy: Optional[InterpolationStrategy] = None
        self.smoothing_strategy: Optional[SmoothingStrategy] = None
        self.bulk_calculation_strategy: Optional[BulkCalculationStrategy] = None
        self.mass_calculation_strategy: Optional[MassCalculationStrategy] = None
        self.second_derivative_strategy: Optional[DerivativeCalculationStrategy] = None
        self.curie_calculation_strategy: Optional[CuriePointCalculationStrategy] = None
        self.outline_detection_strategy: Optional[OutlierDetectionStrategy] = None

    _interpolation_strategies: Dict[str, InterpolationStrategy] = {
        "Linear Interpolation": LinearInterpolation(),
        "Spline Interpolation": SplineInterpolation(),
        "Lagrange Interpolation": LagrangeInterpolation(),
        "Piecewise Linear Interpolation": PiecewiseLinearInterpolation(),
        "Least Squares Interpolation": LeastSquaresInterpolation(),
    }

    _bulk_strategies: Dict[str, BulkCalculationStrategy] = {
        "volume": VolumeCalculation,
        "mass": MassSusceptibilityCalculation,
    }

    @classmethod
    def get_available_interpolation_methods(cls):
        return list(cls._interpolation_strategies.keys())

    @classmethod
    def get_available_bulk_methods(cls):
        return list(cls._bulk_strategies.keys())

    def set_interpolation_strategy(self, strategy_name: str):
        if strategy_name not in self._interpolation_strategies:
            strategy_name = "Linear Interpolation"
        self.interpolation_strategy = self._interpolation_strategies[strategy_name]

    def set_smoothing_strategy(self, strategy, **config):
        self.smoothing_strategy = strategy(**config)

    def set_bulk_calculation_strategy(self, strategy, volume=None, mass=None, density=None):
        if strategy not in self._bulk_strategies:
            raise NotImplementedError('No such method')

        BulkCalculationStrategy.validate_parameters(strategy, volume, mass, density)

        if strategy == 'volume':
            self.bulk_calculation_strategy = VolumeCalculation(volume)
        elif strategy == 'mass':
            self.bulk_calculation_strategy = MassSusceptibilityCalculation(mass, density)

    def set_mass_calculation_strategy(self, strategy, **config):
        MassCalculationStrategy.validate_parameters(**config)
        self.mass_calculation_strategy = strategy(**config)

    def set_curie_calculation_strategy(self, strategy, **config):
        self.curie_calculation_strategy = strategy(**config)

    def set_second_derivative_strategy(self, strategy, **config):
        self.second_derivative_strategy = strategy(**config)

    def set_outline_detection_strategy(self, strategy, **config):
        self.outline_detection_strategy = strategy(**config)

    def smooth(self, data) -> np.ndarray[float]:
        if not self.smoothing_strategy:
            raise ValueError("Smoothing strategy not set")
        return self.smoothing_strategy.smooth(data)

    def interpolate(self, x, y, point):
        if not self.interpolation_strategy:
            raise ValueError("Interpolation strategy not set")
        return self.interpolation_strategy.interpolate(x, y, point)

    def extrapolate(self, x, y, point):
        if not self.interpolation_strategy:
            raise ValueError("Interpolation strategy not set")
        return self.interpolation_strategy.extrapolate(x, y, point)

    def smooth(self, data):
        if not self.smoothing_strategy:
            raise ValueError("Smoothing strategy not set")
        return self.smoothing_strategy.smooth(data)

    def calculate_bulk(self, data):
        if not self.bulk_calculation_strategy:
            raise ValueError("Bulk Calculation strategy not set")
        return self.bulk_calculation_strategy.calculate(data)

    def calculate_mass(self, data):
        if not self.mass_calculation_strategy:
            raise ValueError("Mass Calculation strategy not set")
        return self.mass_calculation_strategy.calculate(data)

    def calculate_curie(self, temperatures, magnetization):
        if not self.curie_calculation_strategy:
            raise ValueError("Curie Calculation strategy not set")
        return self.curie_calculation_strategy.calculate(temperatures, magnetization)

    def calculate_second_derivative(self, x_values, y_values):
        if not self.second_derivative_strategy:
            raise ValueError("Second Derivative strategy not set")

        return self.second_derivative_strategy.calculate(x_values, y_values)

    def detect_outline_points(self, x_values, y_values):
        if not self.outline_detection_strategy:
            raise ValueError("Detect outline points strategy not set")

        return self.outline_detection_strategy.detect(x_values, y_values)
