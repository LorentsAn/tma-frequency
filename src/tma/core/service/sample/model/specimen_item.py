import dataclasses
from typing import Optional, Dict, List, Tuple

import numpy as np
import pandas as pd
import solara as sol
from pandas import DataFrame

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.entrypoit.file import File
from tma.core.service.exceptions.invalid_filename_error import InvalidFilenameError
from tma.core.service.exceptions.parameter_error import ParameterError
from tma.core.service.measurement.analysis.curie_calculation import InflectionPointCalculation, \
    MaxSecondDerivativePointCalculation, MaxFirstDerivativePointCalculation
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.analysis.mass_calculation import MassCalculation
from tma.core.service.measurement.analysis.outlier_detection import MeanOutlierDetection
from tma.core.service.measurement.analysis.smoothing import MovingAverageSmoothing
from tma.core.service.measurement.model.curie.cuie_point import CuriePoint
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.measurement.model.measurement_manager import MeasurementManager
from tma.core.service.measurement.models.furnance_source import FurnaceSource
from tma.core.service.sample.utility.show_mode import ShowMode
from tma.multipages.components.graphic_elements.graphic_element import GraphicElement


@dataclasses.dataclass(frozen=False)
class SpecimenItem:
    specimen_item_id: int
    filename: sol.Reactive[str]
    uploaded: bool
    show_mode: sol.Reactive[ShowMode]
    file: File
    measurement: sol.Reactive[MeasurementManager]
    curie_points: List[CuriePoint]

    df: sol.Reactive[Optional[DataFrame]] = sol.reactive(None)

    is_empty_source_file: bool = False
    empty_furnace_source: sol.Reactive[FurnaceSource] = sol.reactive(None)

    interpolate_method: sol.Reactive[Optional[str]] = sol.reactive(None)

    # displayed_elements: sol.Reactive[Optional[Dict[str, Dict[str, List[float]]]]] = sol.reactive({})
    displayed_elements: sol.Reactive[List[GraphicElement]] = sol.reactive([])

    @staticmethod
    def create_file_item(
        specimen_item_id: int,
        filename: str,
        uploaded: bool,
        file: File,
        measurement: MeasurementManager,
        is_empty_source_file: bool,
        curie_points: [CuriePoint] = []
    ) -> "SpecimenItem":
        return SpecimenItem(
            specimen_item_id=specimen_item_id,
            filename=sol.reactive(filename),
            uploaded=uploaded,
            file=file,
            # x_column=sol.Reactive(str(file.columns[0])),
            # y_column=sol.Reactive(str(file.columns[1])),
            show_mode=sol.Reactive(ShowMode.DEFAULT_MODE.value),
            measurement=sol.reactive(measurement),
            is_empty_source_file=is_empty_source_file,
            curie_points=curie_points
        )

    @staticmethod
    def load_from_file(input_file, uploaded, is_empty_source_file=False):
        """
        Loads a File instance from the input file and creates a corresponding FileItem.

        Args:
            input_file: The input file.
            uploaded (bool): Indicates whether the file is loaded for display.

        Returns:
            # Tuple[SpecimenItem, SpecimenItem|None]: A tuple containing two FileItem instances (for increasing and decreasing trends)
            #                        or a single FileItem instance for the general case.
            :param is_empty_source_file:
        """
        file = File(input_file)
        # special id for specimen item not in db
        measurement = MeasurementFactory.extract_values(1000, file.file_extension.value, input_file)
        return SpecimenItem(
            specimen_item_id=10000,  # special id for specimen item not in db
            filename=sol.reactive(input_file['name']),
            uploaded=uploaded,
            file=file,
            show_mode=sol.Reactive(ShowMode.DEFAULT_MODE.value),
            measurement=sol.reactive(measurement),
            is_empty_source_file=is_empty_source_file,
            curie_points=[]
        )

    @staticmethod
    def align_and_sum(arr1, arr2):
        """
        Aligns and sums two arrays.

        Args:
            arr1: First array.
            arr2: Second array.

        Returns:
            np.ndarray: Concatenated and summed array.
        """
        return np.concatenate((arr1, arr2)) if len(arr1) > len(arr2) else np.concatenate((arr2, arr1))

    @staticmethod
    def getDF(file_item, x_column: str, y_column: str):
        """
        Retrieves a DataFrame from a FileItem instance.

        Args:
            file_item (SpecimenItem): The FileItem instance.

        Returns:
            pd.DataFrame: A DataFrame containing data from the FileItem.
        """
        df_x = file_item.measurement.value.create_dataframe_by_column(x_column)
        df_y = file_item.measurement.value.create_dataframe_by_column(y_column)

        return pd.concat([df_x, df_y], axis=1)

    def create_dataframe_for_all_columns(self):
        df_result: DataFrame = DataFrame()
        for column in self.measurement.value.get_measurement_columns():
            df = self.measurement.value.create_dataframe_by_column(column)
            df_result = pd.concat([df_result, df], axis=1)
        return df_result

    def find_line_by_xy(self, x_column, y_column, x_value, y_value):
        x_indexes = self.measurement.value.find_row_index_by_value(x_column, x_value)
        y_indexes = self.measurement.value.find_row_index_by_value(y_column, y_value)
        intersect = np.intersect1d(x_indexes, y_indexes)
        return np.intersect1d(x_indexes, y_indexes)[0] if len(intersect) > 0 else []

    def get_empty_furnace_value(self) -> str:
        if self.empty_furnace_source.value:
            return self.empty_furnace_source.value.get_value()
        return "Источник значения Empty Furnace не задан"

    def __get_empty_furnace_type(self) -> str:
        if self.empty_furnace_source.value:
            return self.empty_furnace_source.value.type
        return "Тип не задан"

    def is_furnace_file(self) -> bool:
        return self.__get_empty_furnace_type() == "file"

    def is_furnace_constant(self) -> bool:
        return self.__get_empty_furnace_type() == "constant"

    def has_abbreviations_in_filename(self, *abbreviations) -> bool:
        lower_filename = self.filename.value.lower()
        for abbreviation in abbreviations:
            if abbreviation.lower() in lower_filename:
                return True
        return False

    def is_empty_furnace_or_cryostat_file(self) -> bool:
        return self.is_empty_source_file

    def delete_point(self, line_index, plot_index):
        self.measurement.value.delete_points(line_index, plot_index)
        self.df.set(self.create_dataframe_for_all_columns())

    def update_point(self, values: Dict[str, float], line_index, plot_index):
        if Parameter.TEMP.value in values.keys():
            raise ParameterError('Temperature value cannot be changed')
        self.measurement.value.update_points(values, line_index, plot_index)
        # print(self.measurement.value.measured_data)
        self.df.set(self.create_dataframe_for_all_columns())

    def correct_by_constant(self, constant):
        """
        Corrects the measured data by subtracting a constant from each value in the specified column.

        Args:
            constant: The constant value to subtract from the data.
        """
        self.measurement.value.correct_by_constant(constant)
        self.empty_furnace_source.set(ConstantFurnaceValue(constant))
        self.df.set(self.create_dataframe_for_all_columns())

    def correct_by_file(self, specimen_item: 'SpecimenItem'):
        """
        Corrects the measured data by subtracting a constant from each value in the specified column.

        Args:
            filename: The constant value to subtract from the data.
            :param specimen_item:
        """
        if specimen_item.measurement.value.get_measurement_type() != self.measurement.value.get_measurement_type():
            raise InvalidFilenameError('Mismatched data types for subtraction. '
                                       'Please ensure that you are subtracting files with matching data types '
                                       '(e.g., oven subtracted from empty oven, '
                                       'rheostat subtracted from empty rheostat).')

        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy(specimen_item.interpolate_method.value)
        self.measurement.value.correct_by_file(specimen_item.measurement.value.measurement, data_calc)
        self.empty_furnace_source.set(FileFurnaceValue(specimen_item.filename.value))
        self.df.set(self.create_dataframe_for_all_columns())

    def smooth(self, window_size=5):
        if not self.is_empty_furnace_or_cryostat_file():
            return
        data_calc = DataCalculation()
        data_calc.set_smoothing_strategy(MovingAverageSmoothing, window_size=window_size)
        self.measurement.value.smooth(data_calc)
        self.df.set(self.create_dataframe_for_all_columns())

    def calculate_bulk(self, method, **config):
        if self.is_empty_furnace_or_cryostat_file():
            return
        data_calc = DataCalculation()
        if method in data_calc.get_available_bulk_methods():
            data_calc.set_bulk_calculation_strategy(method, **config)
            self.measurement.value.calculate_bulk(data_calc)
            self.df.set(self.create_dataframe_for_all_columns())
        else:
            raise NotImplementedError('No such method')

    def calculate_mass(self, mass):
        if self.is_empty_furnace_or_cryostat_file():
            return
        data_calc = DataCalculation()
        data_calc.set_mass_calculation_strategy(MassCalculation, mass=mass)
        self.measurement.value.calculate_mass(data_calc)
        self.df.set(self.create_dataframe_for_all_columns())

    def calculate_curie_by_inflection_point(self, y_column, smoothness_degree, threshold: float):
        data_calc = DataCalculation()
        data_calc.set_curie_calculation_strategy(
            InflectionPointCalculation,
            smoothness_degree=smoothness_degree,
            threshold=threshold)
        return self.measurement.value.calculate_curie(data_calc, y_column)

    def detect_outline_points(self, y_column: str, threshold: float):
        data_calc = DataCalculation()
        data_calc.set_outline_detection_strategy(MeanOutlierDetection, threshold=threshold)
        return self.measurement.value.detect_outline_points(data_calc, y_column)

    def calculate_curie_by_max_second_derivative_point(self, smoothness_degree, y_column, threshold):
        data_calc = DataCalculation()
        data_calc.set_curie_calculation_strategy(
            MaxSecondDerivativePointCalculation, smoothness_degree=smoothness_degree, threshold=threshold)
        return self.measurement.value.calculate_curie(data_calc, y_column)

    def calculate_curie_by_max_first_derivative_point(self, smoothness_degree, y_column, threshold):
        data_calc = DataCalculation()
        data_calc.set_curie_calculation_strategy(
            MaxFirstDerivativePointCalculation, smoothness_degree=smoothness_degree, threshold=threshold)
        return self.measurement.value.calculate_curie(data_calc, y_column)

    def transform_specimen_item_to_dict(self):
        return {
            'filename': self.filename.value,
            'file_name': self.filename.value,  # Assuming you need the filename here as well
            'file_extension': self.file.file_extension.value,  # You need to define how to get this
            'is_empty_source': self.is_empty_source_file
        }

    def add_curie_point(self, curie_point: CuriePoint):
        self.curie_points.append(curie_point)

    def delete_curie_point(self, curie_point: CuriePoint):
        self.curie_points.remove(curie_point)

    def get_sorted_curie_points(self) -> Dict[int, List[Tuple[float, float]]]:
        """
        Returns a dictionary of Curie points sorted by id_plot_select.
        The dictionary keys are id_plot_select values, and the values are lists of (temperature, magnetization) tuples.
        """
        curie_dict = {}
        for curie_point in self.curie_points:
            if curie_point.id_plot_select not in curie_dict:
                curie_dict[curie_point.id_plot_select] = []
            curie_dict[curie_point.id_plot_select].append(
                (curie_point.temperature_value, curie_point.magnetization_value))

        return curie_dict

    def get_curie_points(self, y_column) -> Dict[str, List[float]]:
        # Initialize the dictionary with 'x' and 'y' keys and empty lists
        curie_dict = {'x': [], 'y': []}

        # Populate the lists with temperature and magnetization values
        for curie_point in self.curie_points:
            if curie_point.column_name == y_column:
                curie_dict['x'].append(curie_point.temperature_value)
                curie_dict['y'].append(curie_point.magnetization_value)

        return curie_dict
