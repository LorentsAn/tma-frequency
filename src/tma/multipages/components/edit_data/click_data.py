from typing import Dict

import pandas as pd
import solara

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.multipages.components.graphic_elements.style import PointTypes

"""
This module provides a controller class `EditController` for managing editing operations, and components
for displaying information and error messages.

Attributes:
    id_line_df_select (solara.Reactive): Reactive object representing the selected line index in the DataFrame.
    id_line_raw_select (solara.Reactive): Reactive object representing the selected line index in the raw data.
    id_plot_select (solara.Reactive): Reactive object representing the selected plot index.
    edit_value (solara.Reactive): Reactive object representing the edited value.
    click_data (solara.Reactive): Reactive object representing the click data.

"""

specimen_name_error_message = solara.reactive("")
data_info_message = solara.reactive('')


class EditController:
    """
    Controller class for managing editing operations.

    Methods:
        set_specimen_name_error_message(error_message=''): Set the error message for specimen name.
        handle_click(click_data): Handle the click event.
        handle_add(): Handle the addition operation.
        handle_update(values: Dict[str, float]): Handle the update operation.
        handle_delete(): Handle the deletion operation.
    """

    id_line_df_select = solara.reactive(-1)
    id_line_raw_select = solara.reactive(-1)
    id_plot_select = solara.reactive(0)
    edit_value: solara.Reactive[pd.DataFrame] = solara.reactive(None)
    click_data = solara.reactive(None)

    @staticmethod
    def set_specimen_name_error_message(error_message=''):
        specimen_name_error_message.set(error_message)

    @staticmethod
    def handle_click(sample_controller, click_data, point_name):
        EditController.click_data.set(click_data)
        item: SpecimenItem = sample_controller.get_selected_specimen_item()
        cur_df = item.create_dataframe_for_all_columns()
        points = EditController.click_data.value['points']
        x_value = points['xs'][0]
        y_value = points['ys'][0]

        filtered_df = cur_df[(cur_df[sample_controller.get_x_column()] == x_value) &
                             (cur_df[sample_controller.get_y_column()] == y_value)]
        data_info_message.set('')
        if len(filtered_df) == 0:
            return
        if len(filtered_df) != 1:
            data_info_message.set('More than one entry found. Editing the last one.')
            filtered_df = filtered_df.iloc[[-1]]
        index = filtered_df.index.item()

        EditController.edit_value.set(cur_df.iloc[index].to_frame().T)
        EditController.id_plot_select.set(points['trace_indexes'][0])
        EditController.id_line_raw_select.set(
            sample_controller.find_line_by_xy(sample_controller.get_x_column(), sample_controller.get_y_column(),
                                              x_value, y_value))
        EditController.id_line_df_select.set(index)
        sample_controller.set_displayed_element(PointTypes.CurrentUserPoint, [float(x_value)], [float(y_value)])

    @staticmethod
    def handle_add():
        pass

    @staticmethod
    def handle_update(sample_controller: SampleController, values: Dict[str, float]):
        select_index_raw = EditController.id_line_raw_select.value
        sample_controller.update_point(values, select_index_raw, EditController.id_plot_select.value)

    @staticmethod
    def handle_delete(sample_controller: SampleController):
        select_index_df = EditController.id_line_df_select.value
        select_index_raw = EditController.id_line_raw_select.value
        sample_controller.delete_point(select_index_df, select_index_raw, EditController.id_plot_select.value)


class DerivativeClickController:
    id_line_df_select = solara.reactive(-1)
    id_line_raw_select = solara.reactive(-1)
    id_plot_select = solara.reactive(0)
    edit_value: solara.Reactive[pd.DataFrame] = solara.reactive(None)
    click_data = solara.reactive(None)

    @staticmethod
    def find_true_index(specimen_items, line_index):
        true_index = -1
        iterator = -1

        for item in specimen_items:
            has_cooling_curve = item.measurement.value.measurement.has_cooling_curve[Parameter.TEMP.value]
            has_heating_curve = item.measurement.value.measurement.has_heating_curve[Parameter.TEMP.value]

            if has_cooling_curve:
                true_index += 1
                if item.uploaded:
                    iterator += 1
                if line_index == iterator:
                    return true_index

            if has_heating_curve:
                true_index += 1
                if item.uploaded:
                    iterator += 1
                if line_index == iterator:
                    return true_index

    @staticmethod
    def set_specimen_name_error_message(error_message=''):
        specimen_name_error_message.set(error_message)

    @staticmethod
    def handle_click(sample_controller: SampleController, click_data, point_name):
        # Set click data and handle the case where it is None
        DerivativeClickController.click_data.set(click_data)

        if DerivativeClickController.click_data.value is None:
            return

        item: SpecimenItem = sample_controller.get_selected_specimen_item()
        if not item:
            data_info_message.set('No specimen item selected.')
            return

        points = DerivativeClickController.click_data.value['points']

        # Safe access to dictionary keys
        try:
            x_value = points['xs'][0]
            # y_value = points['ys'][0]
            id_plot_select = DerivativeClickController.find_true_index(sample_controller.sample.value.specimen_items,
                                                                       points['trace_indexes'][0])
        except (IndexError, KeyError) as e:
            data_info_message.set('Invalid data point format.')
            return

        # Filter DataFrame by selected x value
        x_column_name = sample_controller.get_x_column()

        main_curve_y_value = item.measurement.value.find_value_by_temp(
            temp_value=x_value,
            column_name=sample_controller.get_y_column(),
            derivative=False,
            id_plot=id_plot_select,
        )

        derivative_value = item.measurement.value.find_value_by_temp(
            temp_value=x_value,
            column_name=sample_controller.get_y_column(),
            derivative=True,
            id_plot=id_plot_select,
        )

        DerivativeClickController.edit_value.set(pd.DataFrame({
            x_column_name: [x_value],
            sample_controller.get_y_column(): [main_curve_y_value]
        }))
        DerivativeClickController.id_plot_select.set(id_plot_select)
        DerivativeClickController.id_line_raw_select.set(
            sample_controller.find_line_by_xy(x_column_name, sample_controller.get_y_column(), x_value,
                                              main_curve_y_value)
        )

        sample_controller.set_displayed_element(
            PointTypes.CurrentUserPoint,
            [float(x_value)],
            [float(main_curve_y_value)]
        )
        sample_controller.set_displayed_element(PointTypes.CurrentUserPointDerivative, [float(x_value)],
                                                [float(derivative_value)])


@solara.component
def InfoMessage():
    if data_info_message.value != '':
        solara.Info(label=data_info_message.value)


@solara.component
def ErrorMessage():
    if specimen_name_error_message.value != '':
        solara.Error(label=specimen_name_error_message.value)
