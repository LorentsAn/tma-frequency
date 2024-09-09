from typing import List, Dict, Tuple

import numpy as np

from tma.core.service.measurement.model.curve import Curve


class Measurement:
    def __init__(self, measurement_id: int, measurement_type: str, columns: List[str]):
        self.measurement_id = measurement_id
        self.columns = columns
        self.measurement_type = measurement_type
        self.heating_curve: Dict[str, Curve] = {col: Curve([], []) for col in columns}
        self.cooling_curve: Dict[str, Curve] = {col: Curve([], []) for col in columns}
        self.has_heating_curve = {col: False for col in columns}
        self.has_cooling_curve = {col: False for col in columns}

    def add_heating_data(self, column: str, temperature: List[float], value: List[float]):
        if column in self.heating_curve:
            self.heating_curve[column].temperature.extend(temperature)
            self.heating_curve[column].values.extend(value)
        else:
            self.heating_curve[column] = Curve(temperature, value)
        self.has_heating_curve[column] = True

    def add_cooling_data(self, column: str, temperature: List[float], value: List[float]):
        if column in self.cooling_curve:
            self.cooling_curve[column].temperature.extend(temperature)
            self.cooling_curve[column].values.extend(value)
        else:
            self.cooling_curve[column] = Curve(temperature, value)

        self.has_cooling_curve[column] = True

    def add_column_if_not_exist(self, column):
        if column not in self.columns:
            self.columns.append(column)
            self.heating_curve[column] = Curve([], [])
            self.cooling_curve[column] = Curve([], [])
        self.has_heating_curve[column] = True

    def get_heating_curve_values(self, column: str):
        return self.heating_curve[column].values if self.has_heating_curve[column] else []

    def get_cooling_curve_values(self, column: str):
        return self.heating_curve[column].values if self.has_heating_curve[column] else []

    def get_curve_length(self, column_name: str) -> int:
        length = 0
        if self.has_heating_curve[column_name]:
            length += self.heating_curve[column_name].get_length()

        if self.has_cooling_curve[column_name]:
            length += self.cooling_curve[column_name].get_length()
        return length

    def concatenate_heating_and_cooling(self, column_name: str) -> List[float]:
        heating_curve = self.heating_curve[column_name] if self.has_heating_curve[column_name] else Curve([], [])
        cooling_curve = self.cooling_curve[column_name] if self.has_cooling_curve[column_name] else Curve([], [])

        combined_values = heating_curve.values + cooling_curve.values

        return combined_values

    def get_measured_data(self):
        result = {}

        for key, curve in self.heating_curve.items():
            added_values = result.get(key)
            if not added_values:
                added_values = {}
            added_values.update({'increasing': np.array(curve.values)})
            result.update({key: added_values})

        for key, curve in self.cooling_curve.items():
            added_values = result.get(key)
            if not added_values:
                added_values = {}
            added_values.update({'decreasing': np.array(curve.values)})
            result.update({key: added_values})

        return result
