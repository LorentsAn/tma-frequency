from typing import List, Optional

import solara

from tma.core.service.measurement.model.curie.cuie_point import CuriePoint
from tma.core.service.sample.controller.repository_controllers.curie_controller import CuriePointsRepositoryController
from tma.core.service.sample.controller.repository_controllers.measured_data_controller import \
    MeasuredDataRepositoryController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.controller.repository_controllers.specimen_item_controller import \
    SpecialItemRepositoryController
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.multipages.components.graphic_elements.graphic_element_factory import GraphicElementFactory
from tma.multipages.components.graphic_elements.style import PointTypes, LineTypes, BaseType


class SpecimenItemController:
    def __init__(self, sample):
        self.sample = sample

    def init_specimen_items_df(self):
        specimen_items = self.sample.value.specimen_items
        for item in specimen_items:
            item.df.set(item.create_dataframe_for_all_columns())

    def add_specimen_items(self, specimen_items: List[SpecimenItem]):
        sample_controller_new = SampleRepositoryController(session_id=solara.get_session_id())
        specimen_repository_controller = SpecialItemRepositoryController(sample_controller_new.sample_model)
        self.sample.value.add_specimen_items(specimen_items)
        specimen_repository_controller.create_specimen_items(specimen_items)

    def check_specimen_item_has_column(self, include_empty_source=True):
        y_column = self.sample.get_y_column()
        for item in self.sample.value.specimen_items:
            if (
                include_empty_source or not item.is_empty_source_file) and y_column not in item.measurement.value.get_measurement_columns():
                return False
        return True

    def get_measurements_range_of_values(self):
        specimen_item = self.get_selected_specimen_item()
        return [-220, 720]

    def column_exist(self, column):
        specimen_item = self.get_selected_specimen_item()
        return column in specimen_item.measurement.value.get_measurement_columns()

    def get_selected_specimen_item(self) -> SpecimenItem:
        return self.sample.value.specimen_items[self.get_selected_file_index()]

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

    def calculate_curie_points(self, smoothness_degree, threshold=0):
        current_specimen_item = self.get_selected_specimen_item()
        y_column = self.sample.get_y_column()

        temperature_values_inflection_points, magnetization_values_inflection_points = (
            current_specimen_item.calculate_curie_by_inflection_point(y_column, smoothness_degree, threshold))
        temperature_values_max_second_derivative, magnetization_values_max_second_derivative = (
            current_specimen_item.calculate_curie_by_max_second_derivative_point(smoothness_degree, y_column,
                                                                                 threshold))
        temperature_values_max_first_derivative, magnetization_values_max_first_derivative = (
            current_specimen_item.calculate_curie_by_max_first_derivative_point(smoothness_degree, y_column, threshold))

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

    def set_displayed_element(self, element_type: BaseType, x_values: Optional[List[float]] = None,
                              y_values: Optional[List[float]] = None, update: bool = False):
        current_specimen_item = self.get_selected_specimen_item()
        # if element_type.name in self.__get_displayed_elements_names(current_specimen_item):
        #     return

        old_element = self.get_displayed_elements(element_type.name)

        old_x_values, old_y_values = [], []
        if update and old_element is not None:
            old_x_values, old_y_values = GraphicElementFactory.get_graphic_element_values(old_element)

        if x_values is not None:
            x_values.extend(old_x_values)
        if y_values is not None:
            y_values.extend(old_y_values)
        try:
            self.reset_show_point(name=element_type.name)
            displayed_elements = current_specimen_item.displayed_elements.value
            displayed_elements.append(GraphicElementFactory.create_graphic_element(element_type, x_values, y_values))
        except ValueError as e:
            return e
        current_specimen_item.displayed_elements.set(displayed_elements)

    def reset_show_point(self, name='all'):
        specimen = self.get_selected_specimen_item()

        if name == 'all':
            specimen.displayed_elements.set([])
        else:
            if name in self.__get_displayed_elements_names(specimen):
                elements = specimen.displayed_elements.value
                filtered_elements = [element for element in elements if element.style.name != name]
                specimen.displayed_elements.set(filtered_elements)

    @staticmethod
    def __get_displayed_elements_names(item: SpecimenItem):
        elements = item.displayed_elements.value
        return [element.style.name for element in elements]

    def get_displayed_elements(self, name: str):
        current_specimen_item = self.get_selected_specimen_item()
        elements = current_specimen_item.displayed_elements.value

        if name not in self.__get_displayed_elements_names(current_specimen_item):
            return None

        for element in elements:
            if element.style.name == name:
                return element

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
        y_column = self.sample.get_y_column()
        temperature_values_outline_points, magnetization_values_outline_points = (
            current_specimen_item.detect_outline_points(y_column, threshold))
        if len(temperature_values_outline_points) == 0 and len(magnetization_values_outline_points) == 0:
            return "No points found with this deviation"
        self.set_displayed_element(element_type=PointTypes.OutlinePoint,
                                   x_values=temperature_values_outline_points,
                                   y_values=magnetization_values_outline_points)
