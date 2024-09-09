from typing import List, Union, Optional, Dict, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.model.measurement import Measurement
from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings


class MeasurementManager:
    def __init__(self, measurement):
        self.measurement: Measurement = measurement
        self.second_derivative: Optional[Measurement] = None
        self.has_second_derivatives = False

    def get_measurement_type(self):
        return self.measurement.measurement_type

    def get_measurement_columns(self):
        return self.measurement.columns

    def get_measurement_id(self):
        return self.measurement.measurement_id

    def get_curves(self, column):
        curves = []
        if self.measurement.has_heating_curve[column]:
            curves.append(self.measurement.heating_curve[column])
        if self.measurement.has_cooling_curve[column]:
            curves.append(self.measurement.cooling_curve[column])
        return curves

    def calculate_second_derivative(self, column_name: str, data_calc: DataCalculation):
        self.second_derivative = Measurement(self.measurement.measurement_id, self.measurement.measurement_type,
                                             self.measurement.columns)
        if self.measurement.has_heating_curve[Parameter.TEMP.value]:
            self.second_derivative.add_heating_data(Parameter.TEMP.value,
                                                    self.measurement.heating_curve[column_name].temperature,
                                                    self.measurement.heating_curve[column_name].temperature)
        if self.measurement.has_cooling_curve[Parameter.TEMP.value]:
            self.second_derivative.add_cooling_data(Parameter.TEMP.value,
                                                    self.measurement.cooling_curve[column_name].temperature,
                                                    self.measurement.cooling_curve[column_name].temperature)

        if self.measurement.has_heating_curve[column_name]:
            self.measurement.add_column_if_not_exist(column_name)
            temp_derivative, magnet_derivative = data_calc.calculate_second_derivative(
                self.measurement.heating_curve[column_name].temperature,
                self.measurement.heating_curve[column_name].values
            )
            self.second_derivative.add_heating_data(column_name, temp_derivative, magnet_derivative)
        if self.measurement.has_cooling_curve[column_name]:
            self.measurement.add_column_if_not_exist(column_name)
            temp_derivative, magnet_derivative = data_calc.calculate_second_derivative(
                self.measurement.cooling_curve[column_name].temperature,
                self.measurement.cooling_curve[column_name].values
            )
            self.second_derivative.add_cooling_data(column_name, temp_derivative, magnet_derivative)

        self.has_second_derivatives = True
        return self.second_derivative

    @staticmethod
    def create_plot(measurement: Measurement, x_column, y_column, title_suffix,
                    appearance_settings: PlotAppearanceSettings = None):
        """
        Helper method to create plots based on the direction of data change.
        """
        if appearance_settings is None:
            appearance_settings = PlotAppearanceSettings(title_suffix)

        plots = []

        def create_scatter(curve_data, curve_settings, name):
            data = {
                str(x_column): curve_data[x_column].temperature,
                str(y_column): curve_data[y_column].values
            }
            df = pd.DataFrame(data)
            print(measurement.measurement_id)
            if measurement.measurement_id == 10001:
                print('df')
                print(df)
            plot_dict = curve_settings.to_dict(
                x=df[str(x_column)],
                y=df[str(y_column)],
                name=name
            )
            return go.Scatter(**plot_dict)

        if measurement.has_heating_curve[y_column]:
            heating_scatter = create_scatter(
                measurement.heating_curve,
                appearance_settings.heating_settings,
                f'{title_suffix} Heating'
            )
            plots.append(heating_scatter)
        if measurement.has_cooling_curve[y_column]:
            cooling_scatter = create_scatter(
                measurement.cooling_curve,
                appearance_settings.cooling_settings,
                f'{title_suffix} Cooling'
            )
            plots.append(cooling_scatter)
        return plots

        # fig = go.Figure(plots)
        # fig.update_layout(
        #     title=f'{y_column} vs {x_column} {title_suffix}',
        #     xaxis_title=x_column,
        #     yaxis_title=y_column,
        #     template='plotly_white'
        # )
        # fig.show()

    def plot_data(self, x_column, y_column, filename, appearance_settings: PlotAppearanceSettings = None):
        """
        Generate plots based on the input columns and mode, ensuring mode is allowed.
        """
        return self.create_plot(self.measurement, x_column, y_column, filename, appearance_settings)

    def plot_second_derivative(self, x_column, y_column, data_calc, appearance_settings: PlotAppearanceSettings = None):
        """
        Generate plots for the second derivative of the data.
        """
        second_derivative = self.calculate_second_derivative(y_column, data_calc)
        return self.create_plot(second_derivative, x_column, y_column, 'Second derivative', appearance_settings)

    def find_value_by_temp(self, temp_value: float, column_name: str, id_plot: Union[int, None] = 0,
                           derivative: bool = False) -> float:
        if column_name not in self.measurement.columns:
            raise KeyError(f"Column '{column_name}' not found in measurement.")

        measurement = self.second_derivative if derivative else self.measurement

        heating_curve = measurement.heating_curve[column_name]
        cooling_curve = measurement.cooling_curve[column_name]

        if id_plot == 0:
            index = heating_curve.get_closest_index(temp_value)
            return float(heating_curve.values[index])
        elif id_plot == 1:
            index = cooling_curve.get_closest_index(temp_value)
            return float(cooling_curve.values[index])
        else:
            heating_index = heating_curve.get_closest_index(temp_value) if measurement.has_heating_curve[
                column_name] else None
            cooling_index = cooling_curve.get_closest_index(temp_value) if measurement.has_cooling_curve[
                column_name] else None

            if heating_index is None and cooling_index is None:
                raise ValueError("No heating or cooling data available for this column.")

            if heating_index is None:
                return float(cooling_curve.values[cooling_index])
            if cooling_index is None:
                return float(heating_curve.values[heating_index])

            diff_heating = abs(heating_curve.temperature[heating_index] - temp_value)
            diff_cooling = abs(cooling_curve.temperature[cooling_index] - temp_value)

            return float(heating_curve.values[heating_index] if diff_heating < diff_cooling else cooling_curve.values[
                cooling_index])

    @staticmethod
    def align_and_sum(arr1: Union[np.ndarray, None], arr2: Union[np.ndarray, None]) -> Union[np.ndarray, None]:
        if arr1 is None:
            return arr2
        if arr2 is None:
            return arr1
        return np.concatenate((arr1, arr2)) if len(arr1) > len(arr2) else np.concatenate((arr2, arr1))

    def create_dataframe_by_column(self, column_name: str) -> Union[pd.DataFrame, None]:
        heating_curve = self.measurement.heating_curve[column_name] if self.measurement.has_heating_curve[
            column_name] else None
        cooling_curve = self.measurement.cooling_curve[column_name] if self.measurement.has_heating_curve[
            column_name] else None

        heating_values = np.array(heating_curve.values) if heating_curve else None
        cooling_values = np.array(cooling_curve.values) if cooling_curve else None

        aligned_values = self.align_and_sum(heating_values, cooling_values)
        return pd.DataFrame({column_name: aligned_values}) if aligned_values is not None else None

    def __validate_line_index(self, line_index: int, direction: str) -> bool:
        last_column = self.measurement.columns[-1]
        curve = self.measurement.heating_curve[last_column] if direction == 'increasing' \
            else self.measurement.cooling_curve[last_column]
        return curve.is_valid_index(line_index)

    def delete_points(self, line_index: int, plot_index: Union[int, None] = 0):
        direction = 'decreasing' if plot_index == 1 else 'increasing'
        if self.__validate_line_index(line_index, direction):
            for column_name in self.measurement.columns:
                curve = self.measurement.heating_curve[column_name] \
                    if direction == 'increasing' and self.measurement.has_heating_curve[column_name] \
                    else self.measurement.cooling_curve[column_name]
                curve.delete_point(line_index)

    def update_points(self, values: Dict[str, float], line_index: int, plot_index: Union[int, None] = 0):
        direction = 'decreasing' if plot_index == 1 else 'increasing'
        if self.__validate_line_index(line_index, direction):
            for column_name, new_value in values.items():
                curve = self.measurement.heating_curve[column_name] \
                    if direction == 'increasing' and self.measurement.has_heating_curve[column_name] \
                    else self.measurement.cooling_curve[column_name]
                curve.update_point(line_index, new_value)

    def find_row_index_by_value(self, column_name: str, y: float) -> List[int]:
        indices = []
        if self.measurement.has_heating_curve[column_name]:
            indices.extend(self.measurement.cooling_curve[column_name].find_indices_by_value(y))
        if self.measurement.has_cooling_curve[column_name]:
            indices.extend(self.measurement.cooling_curve[column_name].find_indices_by_value(y))
        return indices

    def _sum_values_to_column(self, column_name: str, direction: str, values_y: List[float]) -> List[float]:
        curve = self.measurement.heating_curve[column_name] if direction == 'increasing' else \
        self.measurement.cooling_curve[column_name]
        return curve.update_values(values_y)

    def correct_heating_data(self, values: List[float]):
        if self.measurement.has_heating_curve[Parameter.CSUSC.value]:
            direction = 'increasing'
            corrected_values = self._sum_values_to_column(Parameter.TSUSC.value, direction, values)
            self.measurement.heating_curve[Parameter.CSUSC.value].values = corrected_values

    def correct_cooling_data(self, values: List[float]):
        if self.measurement.has_cooling_curve[Parameter.CSUSC.value]:
            direction = 'decreasing'
            corrected_values = self._sum_values_to_column(Parameter.TSUSC.value, direction, values)
            self.measurement.cooling_curve[Parameter.CSUSC.value].values = corrected_values

    def correct_by_file(self, file_measurement: 'Measurement', data_calc: DataCalculation):
        def compare_length(array1: List[float], array2: List[float]) -> int:
            len1, len2 = len(array1), len(array2)
            return -1 if len1 < len2 else (1 if len1 > len2 else 0)

        def process_phase(curve, combined_temp: List[float], combined_tsusc: List[float]):
            phase_size = len(combined_temp)
            combined_phase_tsusc = combined_tsusc
            comparison_result = compare_length(combined_phase_tsusc, curve.values)

            if comparison_result == -1:
                interpolated_values = np.array(curve.interpolate(
                    data_calc,
                    combined_temp[:phase_size],
                    combined_tsusc[:phase_size],
                    curve.temperature[phase_size:]
                ))
                return np.concatenate((np.array(combined_phase_tsusc), interpolated_values))
            else:
                return combined_phase_tsusc

        if self.measurement.has_heating_curve[Parameter.TSUSC.value]:
            corrected_array = process_phase(
                self.measurement.heating_curve[Parameter.TSUSC.value],
                file_measurement.heating_curve[Parameter.TEMP.value].values,
                file_measurement.heating_curve[Parameter.TSUSC.value].values
            )
            self.correct_heating_data(corrected_array)

        if self.measurement.has_cooling_curve[Parameter.TSUSC.value]:
            corrected_array = process_phase(
                self.measurement.cooling_curve[Parameter.TSUSC.value],
                file_measurement.cooling_curve[Parameter.TEMP.value].values,
                file_measurement.cooling_curve[Parameter.TSUSC.value].values
            )
            self.correct_cooling_data(corrected_array)

    def correct_by_constant(self, constant: float):
        if self.measurement.has_heating_curve[Parameter.CSUSC.value]:
            self.measurement.heating_curve[Parameter.CSUSC.value].values = (
                self.measurement.heating_curve[Parameter.TSUSC.value].apply_constant_correction(constant))

        if self.measurement.has_cooling_curve[Parameter.CSUSC.value]:
            self.measurement.cooling_curve[Parameter.CSUSC.value].values = (
                self.measurement.cooling_curve[Parameter.TSUSC.value].apply_constant_correction(constant))

    def smooth(self, data_calc):
        def smooth_and_adjust(curve):
            curve.values = curve.smooth(data_calc.smooth)
            curve.adjust_length()

        for column_name in self.measurement.columns:
            if column_name == Parameter.TEMP.value:
                continue

            if self.measurement.has_heating_curve[column_name]:
                smooth_and_adjust(self.measurement.heating_curve[column_name])

            if self.measurement.has_cooling_curve[column_name]:
                smooth_and_adjust(self.measurement.cooling_curve[column_name])

    def calculate_data(self, parameter, calculation_method):
        if self.measurement.has_heating_curve[Parameter.CSUSC.value]:
            raw_data = self.measurement.heating_curve[Parameter.CSUSC.value].values
            if parameter not in self.measurement.heating_curve.keys():
                self.measurement.add_heating_data(parameter,
                                                  self.measurement.heating_curve[Parameter.CSUSC.value].temperature,
                                                  calculation_method(raw_data))
            else:
                self.measurement.heating_curve[parameter].values = calculation_method(raw_data)

        if self.measurement.has_cooling_curve[Parameter.CSUSC.value]:
            raw_data = self.measurement.cooling_curve[Parameter.CSUSC.value].values
            if parameter not in self.measurement.cooling_curve.keys():
                self.measurement.add_cooling_data(parameter,
                                                  self.measurement.cooling_curve[Parameter.CSUSC.value].temperature,
                                                  calculation_method(raw_data))
            else:
                self.measurement.cooling_curve[parameter].values = calculation_method(raw_data)

    def calculate_bulk(self, data_calc: DataCalculation):
        self.measurement.add_column_if_not_exist(Parameter.BSUSC.value)
        self.calculate_data(Parameter.BSUSC.value, data_calc.calculate_bulk)

    def calculate_mass(self, data_calc: DataCalculation):
        self.measurement.add_column_if_not_exist(Parameter.MSUSC.value)
        self.calculate_data(Parameter.MSUSC.value, data_calc.calculate_mass)

    def process_second_derivative_calculation(self, data_calc, y_column: str, function_name: str) -> Union[
        Tuple[List[float], List[float]], None]:
        if y_column not in self.measurement.columns:
            return None

        result_temp, result_values = [], []

        def call_data_calc_function(temp_data: List[float], values_data: List[float], reverse: bool = False):
            if reverse:
                temp_data = np.flip(temp_data)
                values_data = np.flip(values_data)

            func = getattr(data_calc, function_name)
            temp, values = func(temp_data, values_data)
            result_temp.extend(temp)
            result_values.extend(values)

        if self.measurement.has_heating_curve[y_column]:
            heating_curve = self.measurement.heating_curve[y_column]
            if heating_curve.temperature and heating_curve.values:
                call_data_calc_function(heating_curve.temperature, heating_curve.values)

        if self.measurement.has_cooling_curve[y_column]:
            cooling_curve = self.measurement.cooling_curve[y_column]
            if cooling_curve.temperature and cooling_curve.values:
                call_data_calc_function(cooling_curve.temperature, cooling_curve.values, reverse=True)

        sorted_results = sorted(zip(result_temp, result_values), key=lambda x: x[0])
        result_temp, result_values = [res[0] for res in sorted_results], [res[1] for res in sorted_results]

        return list(result_temp), list(result_values)

    def calculate_curie(self, data_calc, y_column: str) -> Union[Tuple[List[float], List[float]], None]:
        return self.process_second_derivative_calculation(data_calc, y_column, 'calculate_curie')

    def detect_outline_points(self, data_calc, y_column: str) -> Union[Tuple[List[float], List[float]], None]:
        return self.process_second_derivative_calculation(data_calc, y_column, 'detect_outline_points')

    def get_measured_data(self):
        result = {}

        if self.measurement.has_heating_curve[Parameter.TEMP.value]:
            for key, curve in self.measurement.heating_curve.items():
                added_values = result.get(key)
                if not added_values:
                    added_values = {}
                added_values.update({'increasing': np.array(curve.values)})
                result.update({key: added_values})

        if self.measurement.has_cooling_curve[Parameter.TEMP.value]:
            for key, curve in self.measurement.cooling_curve.items():
                added_values = result.get(key)
                if not added_values:
                    added_values = {}
                added_values.update({'decreasing': np.array(curve.values)})
                result.update({key: added_values})

        return result
