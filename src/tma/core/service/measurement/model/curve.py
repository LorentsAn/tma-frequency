from typing import List, Optional

import numpy as np

from tma.core.service.measurement.analysis.data_calculation import DataCalculation


class Curve:
    def __init__(self, temperature: List[float], values: List[float]):
        self.temperature = temperature
        self.values = values

    def get_closest_index(self, target_temp: float) -> int:
        return min(range(len(self.temperature)), key=lambda i: abs(self.temperature[i] - target_temp))

    def find_indices_by_value(self, value: float) -> List[int]:
        return np.where(np.array(self.values) == value)[0].tolist()

    def get_length(self) -> int:
        return len(self.values)

    def delete_point(self, index: int):
        self.temperature = np.delete(self.temperature, index).tolist()
        self.values = np.delete(self.values, index).tolist()

    def update_point(self, index: int, new_value: float):
        self.values[index] = new_value

    def is_valid_index(self, index: int) -> bool:
        return 0 <= index < self.get_length()

    def update_values(self, values_to_subtract: List[float]) -> List[float]:
        updated_values = []
        for index, temp_point in enumerate(self.values):
            closest_index = self.get_closest_index(temp_point)
            updated_value = round(self.values[index] - values_to_subtract[closest_index], 3)
            updated_values.append(updated_value)
        return updated_values

    def apply_constant_correction(self, constant: float) -> List[float]:
        return [round(value - constant, 3) for value in self.values]

    @staticmethod
    def interpolate(data_calc: DataCalculation, array_x, array_y, target_array_x):
        return [data_calc.extrapolate(array_x, array_y, point) for point in target_array_x]

    def smooth(self, smoother) -> List[float]:
        return smoother(self.values) if self.values else []

    def adjust_length(self):
        min_length = min(len(self.temperature), len(self.values))
        self.temperature = self.temperature[:min_length]
        self.values = self.values[:min_length]
