from typing import Optional, List

import pandas as pd
import solara

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.multipages.components.graphic_elements.style import PointTypes
import pandas as pd
import solara

data_info_message = solara.reactive('')


class ClickController:
    def __init__(self):
        self.id_line_df_select = solara.reactive(-1)
        self.id_line_raw_select = solara.reactive(-1)
        self.id_plot_select = solara.reactive(0)
        self.is_cooling_plot: solara.Reactive[bool] = solara.reactive(False)
        self.edit_value: solara.Reactive[Optional[pd.DataFrame]] = solara.reactive(None)
        self.click_data = solara.reactive(None)

    def find_true_index(self, specimen_items, line_index):
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

        return true_index

    def handle_click(self, sample_controller, click_data, point_name, specimen_items: List[SpecimenItem]):
        self.click_data.set(click_data)
        points = self.click_data.value['points']
        line_index = points['trace_indexes'][0]
        line_index = self.find_true_index(specimen_items, line_index)

        if not 0 <= line_index // 2 < len(specimen_items):
            return

        item = specimen_items[
            line_index // 2]  # на каждое измерение приходится по 2 кривые 0 - increasong, 1 - decreasing
        cur_df = item.create_dataframe_for_all_columns()

        x_value, y_value = self._get_click_coordinates(points)
        filtered_df = self._filter_dataframe(cur_df, sample_controller, x_value, y_value)

        data_info_message.set('')
        if len(filtered_df) == 0:
            return

        if len(filtered_df) != 1:
            data_info_message.set('More than one entry found. Editing the last one.')
            filtered_df = filtered_df.iloc[[-1]]

        index = filtered_df.index.item()
        self._set_reactive_values(cur_df, index, points, sample_controller, x_value, y_value, line_index)

    def _get_click_coordinates(self, points):
        x_value = points['xs'][0]
        y_value = points['ys'][0]
        return x_value, y_value

    def _filter_dataframe(self, dataframe, sample_controller, x_value, y_value):
        x_column = sample_controller.get_x_column()
        y_column = sample_controller.get_y_column()
        return dataframe[(dataframe[x_column] == x_value) & (dataframe[y_column] == y_value)]

    def _set_reactive_values(self, dataframe, index, points, sample_controller, x_value, y_value, line_index):
        self.edit_value.set(dataframe.iloc[index].to_frame().T)
        self.id_plot_select.set(line_index // 2)
        self.is_cooling_plot.set(bool(line_index % 2))
        self.id_line_raw_select.set(
            sample_controller.find_line_by_xy(
                sample_controller.get_x_column(),
                sample_controller.get_y_column(),
                x_value,
                y_value
            )
        )
        self.id_line_df_select.set(index)
        sample_controller.set_displayed_element(
            PointTypes.CurrentUserPoint,
            [float(x_value)],
            [float(y_value)]
        )
