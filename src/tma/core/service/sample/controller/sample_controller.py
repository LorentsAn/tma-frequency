from typing import List, Optional, Callable

from pandas import DataFrame

from tma.core.data.parser.model.parameter import Parameter

from tma.core.service.measurement.model.curie.cuie_point import CuriePoint
from tma.core.service.sample.controller.repository_controllers.curie_controller import CuriePointsRepositoryController
from tma.core.service.sample.controller.repository_controllers.measured_data_controller import \
    MeasuredDataRepositoryController
from tma.core.service.sample.controller.repository_controllers.specimen_item_controller import \
    SpecialItemRepositoryController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.model.sample import Sample
from tma.core.service.sample.utility.show_mode import ShowMode
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.core.service.measurement.analysis.data_calculation import DataCalculation

import solara

from tma.multipages.components.graphic_elements.graphic_element import GraphicElement
from tma.multipages.components.graphic_elements.graphic_element_factory import GraphicElementFactory
from tma.multipages.components.graphic_elements.style import BaseType, PointTypes, LineTypes


class SampleController:
    """
    Controller class for managing samples and specimen items.
    """
    # Class attribute
    sample: solara.Reactive[Optional[Sample]]

    def __init__(self, sample=None):
        if sample is None:
            self.sample = solara.reactive(Sample())
        else:
            self.sample = solara.reactive(sample)
            self.init_specimen_items_df()

    def init_specimen_items_df(self):
        specimen_items = self.sample.value.specimen_items
        for item in specimen_items:
            item.df.set(item.create_dataframe_for_all_columns())

    def check_specimen_item_has_column(self, include_empty_source=True):
        y_column = self.get_y_column()
        for item in self.sample.value.specimen_items:
            if (
                include_empty_source or not item.is_empty_source_file) and y_column not in item.measurement.value.get_measurement_columns():
                return False
        return True

    def get_measurements_range_of_values(self):
        specimen_item = self.get_selected_specimen_item()
        return [-220, 720]

    def add_specimen_items(self, specimen_items: List[SpecimenItem]):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())
        specimen_repository_controller = SpecialItemRepositoryController(sample_controller_new.sample_model)
        self.sample.value.add_specimen_items(specimen_items)
        specimen_repository_controller.create_specimen_items(specimen_items)

    def update_sample_name(self, new_sample_name: str) -> str:
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())
        if not self.is_valid_sample_name(new_sample_name):
            return "Invalid sample name. Name must contain up to 30 characters and not contain spaces, commas, or semicolons."
        sample_controller_new.update_sample(name=new_sample_name)
        self.sample.value.update_sample_name(new_sample_name)
        return ''

    def is_valid_sample_name(self, file_name: str) -> bool:
        return len(file_name) <= 30 and all(char not in ' ,;' for char in file_name)

    def get_x_column(self) -> str:
        return self.sample.value.get_x_column()

    # def get_y_column(self) -> str:
    #     if self.sample.value.get_y_column() in self.get_intersect_get_columns():
    #         return self.sample.value.get_y_column()
    #     else:
    #         return Parameter.TSUSC.value
    #     return self.sample.value.get_y_column()

    def get_y_column(self) -> str:
        if not self.sample.value.specimen_items:
            return Parameter.TSUSC.value

        if self.sample.value.get_y_column() in self.get_selected_specimen_item().measurement.value.get_measurement_columns():
            return self.sample.value.get_y_column()
        else:
            return Parameter.TSUSC.value

    def column_exist(self, column):
        specimen_item = self.get_selected_specimen_item()
        return column in specimen_item.measurement.value.get_measurement_columns()

    def is_furnace_file(self) -> bool:
        return self.sample.value.is_furnace_file(self.selected_file_index)

    def get_intersect_get_columns(self, hidden_value: str = '') -> List[str]:
        if not self.sample.value.specimen_items:
            return []

        intersection = set(self.sample.value.specimen_items[0].measurement.value.get_measurement_columns())
        for item in self.sample.value.specimen_items[1:]:
            intersection &= set(item.measurement.value.get_measurement_columns())
        if hidden_value in intersection:
            intersection.remove(hidden_value)
        return list(intersection)

    def get_filenames_list(self, include_empty_source=True, additional_filter: Callable = None) -> List[str]:
        items = self.sample.value.specimen_items
        filtered_items = []
        for item in items:
            if item.uploaded and (include_empty_source or not item.is_empty_source_file):
                if additional_filter is None or additional_filter(item):
                    filtered_items.append(item.filename.value)
        return filtered_items

    def get_empty_source_file_items_plain_list(self) -> List[str]:
        return [item.filename.value for item in self.sample.value.specimen_items if item.is_empty_source_file]

    def is_sample_created(self) -> bool:
        return bool(self.sample.value.specimen_items)

    def get_selected_specimen_item(self) -> SpecimenItem:
        return self.sample.value.specimen_items[self.get_selected_file_index()]

    def save_df(self, df_new: DataFrame):
        item = self.get_selected_specimen_item()
        item.df.set(df_new)

    def get_selected_file_index(self):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())
        return sample_controller_new.sample_model.selected_file_index

    def on_file_item_select(self, filename_value: str):
        index = self.sample.value.get_index_specimen_item_by_filename(filename_value)
        if index is not None:
            self.sample.value.selected_file_index = index
            specimen_item = self.get_selected_specimen_item()
            specimen_item.df.set(specimen_item.create_dataframe_for_all_columns())
            return index
        return None

    def get_sample_name(self) -> str:
        return self.sample.value.get_sample_name()

    def change_show_mode(self, mode):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())

        index = self.get_selected_file_index()
        if mode in ShowMode.get_enum_values() and 0 <= index < len(self.sample.value.specimen_items):
            file = self.sample.value.specimen_items[index]
            file.show_mode.set(mode)
            # sample_controller_new.update_sample(x_column=column_name)

    def change_column(self, axis, column_name):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())

        if axis not in ['x_column', 'y_column']:
            return
        if axis == 'x_column':
            self.sample.value.update_x_column(column_name)
            sample_controller_new.update_sample(x_column=column_name)
        if axis == 'y_column':
            self.sample.value.update_y_column(column_name)
            sample_controller_new.update_sample(y_column=column_name)

    def remove_sample(self):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())

        self.sample.value.clear_fields()

        sample_controller_new.delete_sample(self.sample.value)

    def delete_point(self, line_df_index, line_raw_index, plot_index):
        file = self.get_selected_specimen_item()
        file.delete_point(line_raw_index, plot_index)

    def find_line_by_xy(self, x_column, y_column, x_value, y_value):
        specimen_item = self.get_selected_specimen_item()
        return specimen_item.find_line_by_xy(x_column, y_column, x_value, y_value)

    @staticmethod
    def set_interpolate_method(selected_item: SpecimenItem, method: str):
        selected_item.interpolate_method.set(method)

    def smooth_specimen_item(self, window_size):
        measured_data_repository_controller = MeasuredDataRepositoryController()

        current_specimen_item = self.get_selected_specimen_item()
        if current_specimen_item.is_empty_furnace_or_cryostat_file():
            current_specimen_item.smooth(window_size)
            measured_data_repository_controller.update_measured_data(
                self.sample.value,
                current_specimen_item.filename.value,
                current_specimen_item.measurement.value.get_measured_data()
            )

    @staticmethod
    def get_interpolation_methods():
        return DataCalculation.get_available_interpolation_methods()

    def calculate_curie_points(self, smoothness_degree, inflection_point_threshold=0, second_derivative_threshold=0,
                               first_derivative_threshold=0, show_critical_points=True,
                               specimen_item: SpecimenItem = None):
        if specimen_item is None:
            specimen_item = self.get_selected_specimen_item()
        y_column = self.get_y_column()

        temperature_values_inflection_points, magnetization_values_inflection_points = (
            specimen_item.calculate_curie_by_inflection_point(y_column, smoothness_degree, inflection_point_threshold))
        temperature_values_max_second_derivative, magnetization_values_max_second_derivative = (
            specimen_item.calculate_curie_by_max_second_derivative_point(smoothness_degree, y_column,
                                                                         second_derivative_threshold))
        temperature_values_max_first_derivative, magnetization_values_max_first_derivative = (
            specimen_item.calculate_curie_by_max_first_derivative_point(smoothness_degree, y_column,
                                                                        first_derivative_threshold))

        if not show_critical_points:
            return

        self.set_displayed_element(element_type=PointTypes.InflectionPoint,
                                   x_values=temperature_values_inflection_points,
                                   y_values=magnetization_values_inflection_points)
        self.set_displayed_element(element_type=PointTypes.MaxSecondDerivative,
                                   x_values=temperature_values_max_second_derivative,
                                   y_values=magnetization_values_max_second_derivative)
        self.set_displayed_element(element_type=PointTypes.MaxFirstDerivative,
                                   x_values=temperature_values_max_first_derivative,
                                   y_values=magnetization_values_max_first_derivative)

        self.set_displayed_element(element_type=LineTypes.InflectionPointLine,
                                   x_values=temperature_values_inflection_points)
        self.set_displayed_element(element_type=LineTypes.MaxSecondDerivativeLine,
                                   x_values=temperature_values_max_second_derivative)
        self.set_displayed_element(element_type=LineTypes.MaxFirstDerivative,
                                   x_values=temperature_values_max_first_derivative)

    def set_displayed_element(self, element_type: 'BaseType', x_values: Optional[List[float]] = None,
                              y_values: Optional[List[float]] = None, update: bool = False,
                              specimen_item: Optional['SpecimenItem'] = None) -> Optional['SpecimenItem']:
        specimen_item = specimen_item or self.get_selected_specimen_item()
        old_element = self.get_displayed_element(element_type.name, specimen_item)

        if update and old_element:
            old_x_values, old_y_values = GraphicElementFactory.get_graphic_element_values(old_element)
            x_values = (x_values or []) + old_x_values
            y_values = (y_values or []) + old_y_values

        try:
            self.reset_show_point(name=element_type.name, specimen_item=specimen_item)
            new_element = GraphicElementFactory.create_graphic_element(element_type, x_values, y_values)
            specimen_item.displayed_elements.value.append(new_element)
        except ValueError as e:
            return e

        return specimen_item

    def reset_show_point(self, name: str = 'all', specimen_item: Optional['SpecimenItem'] = None) -> None:
        specimen_item = specimen_item or self.get_selected_specimen_item()

        if name == 'all':
            specimen_item.displayed_elements.set([])
        else:
            elements = specimen_item.displayed_elements.value
            filtered_elements = [element for element in elements if element.style.name != name]
            specimen_item.displayed_elements.set(filtered_elements)

    @staticmethod
    def _get_displayed_elements_names(item: 'SpecimenItem') -> List[str]:
        return [element.style.name for element in item.displayed_elements.value]

    def get_displayed_element(self, name: str, specimen_item: Optional['SpecimenItem'] = None) -> Optional[
        GraphicElement]:
        specimen_item = specimen_item or self.get_selected_specimen_item()
        elements = specimen_item.displayed_elements.value

        for element in elements:
            if element.style.name == name:
                return element
        return None

    def update_point(self, values, line_raw_index, plot_index):
        measured_data_repository_controller = MeasuredDataRepositoryController()

        file: SpecimenItem = self.get_selected_specimen_item()
        file.update_point(values, line_raw_index, plot_index)
        measured_data_repository_controller.update_measured_data(
            self.sample.value,
            file.filename.value,
            file.measurement.value.get_measured_data()
        )

    def create_curie_point(self, column_name: str, id_plot_select: int, temperature_value: float,
                           magnetization_value: float):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())

        file: SpecimenItem = self.get_selected_specimen_item()
        specimen_repository_controller = SpecialItemRepositoryController(sample_controller_new.sample_model)
        curie_point_repository_controller = CuriePointsRepositoryController(
            specimen_repository_controller.get_specimen_item(file.filename.value))
        try:
            existed_curie_point = CuriePoint.find_by_values(file.curie_points, temperature_value, magnetization_value)
            if existed_curie_point is not None:
                return 'Such a point already exists'

            curie_point = curie_point_repository_controller.add_curie_point(
                filename=file.filename.value,
                column_name=column_name,
                id_plot_select=id_plot_select,
                temperature_value=temperature_value,
                magnetization_value=magnetization_value
            )
            file.add_curie_point(curie_point)
            self.set_displayed_element(element_type=PointTypes.StoredCuriePoints,
                                       x_values=[curie_point.temperature_value],
                                       y_values=[curie_point.magnetization_value], update=True)
            self.set_displayed_element(element_type=LineTypes.StoredCurieLine, x_values=[curie_point.temperature_value],
                                       update=True)
        except Exception:
            return "Unknown error, try again"

    def delete_curie_point(self, temperature_value: float, magnetization_value: float):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())

        file: SpecimenItem = self.get_selected_specimen_item()
        specimen_repository_controller = SpecialItemRepositoryController(sample_controller_new.sample_model)
        curie_point_repository_controller = CuriePointsRepositoryController(
            specimen_repository_controller.get_specimen_item(file.filename.value))

        curie_point = CuriePoint.find_by_values(file.curie_points, temperature_value, magnetization_value)
        curie_point_repository_controller.delete_curie_point(curie_point)
        file.delete_curie_point(curie_point)

        temperatures = [point.temperature_value for point in file.curie_points]
        magnetization = [point.magnetization_value for point in file.curie_points]
        self.set_displayed_element(PointTypes.StoredCuriePoints, temperatures, magnetization)
        self.set_displayed_element(LineTypes.StoredCurieLine, temperatures, magnetization)

    def detect_outline_points(self, threshold: float):
        current_specimen_item = self.get_selected_specimen_item()
        y_column = self.get_y_column()
        temperature_values_outline_points, magnetization_values_outline_points = (
            current_specimen_item.detect_outline_points(y_column, threshold))
        if len(temperature_values_outline_points) == 0 and len(magnetization_values_outline_points) == 0:
            return "No points found with this deviation"
        self.set_displayed_element(element_type=PointTypes.OutlinePoint,
                                   x_values=temperature_values_outline_points,
                                   y_values=magnetization_values_outline_points)
