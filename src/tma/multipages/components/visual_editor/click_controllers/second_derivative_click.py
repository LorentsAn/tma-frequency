from typing import Optional, List

import pandas as pd
import solara

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.multipages.components.graphic_elements.style import PointTypes


class SecondDerivativeClickController:
    def __init__(self):
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

        x_value, y_value = self._get_click_coordinates(points)

        derivative_value = item.measurement.value.find_value_by_temp(
            temp_value=x_value,
            column_name=sample_controller.get_y_column(),
            derivative=True,
            id_plot=line_index % 2,
        )

        self._set_reactive_values(sample_controller, x_value, derivative_value, line_index)

    def _get_click_coordinates(self, points):
        x_value = points['xs'][0]
        y_value = points['ys'][0]
        return x_value, y_value

    def _set_reactive_values(self, sample_controller, x_value, y_value, line_index):
        self.edit_value.set(pd.DataFrame({
            sample_controller.get_x_column(): [x_value],
            sample_controller.get_y_column(): [y_value]
        }))
        self.id_plot_select.set(line_index // 2)
        self.is_cooling_plot.set(bool(line_index % 2))
        sample_controller.set_displayed_element(
            PointTypes.CurrentUserPointDerivative,
            [float(x_value)],
            [float(y_value)]
        )
