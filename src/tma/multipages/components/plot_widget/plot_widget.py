from typing import Optional

import solara

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.analysis.second_derivative import SecondDerivativeCalculation
from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.multipages.components.plot_widget.customization_settings import CustomizationSettings
import plotly.graph_objects as go

from tma.multipages.components.plot_widget.display_config import DisplayConfig
from tma.multipages.components.plot_widget.plot_renderer import PlotRenderer
from tma.multipages.components.graphic_elements.graphic_element import GraphicElement
from tma.multipages.components.graphic_elements.layout_settings import LayoutSettings
from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings


@solara.component
def PlotWidget(
    specimen_items: [SpecimenItem],
    sample_controller=SampleController(),
    default_y_column=Parameter.TSUSC.value,
    layout=None,
    display_config: Optional[DisplayConfig] = None,
    customizable=True,
    show_data_type='all',  # 'all', 'second_derivative'
    smoothness_degree=None,
    on_click=None,
    curve_configs: [PlotAppearanceSettings] = None,
    layout_config: [LayoutSettings] = None,
    add_axes_lines: bool = True,
):
    print(curve_configs)
    if display_config is None:
        display_config = DisplayConfig()
    # todo refactoring
    if layout is None:
        layout = {}

    data_preparation = DataPreparation(sample_controller)
    if show_data_type == 'second_derivative':
        data_preparation.process_only_second_derivative(specimen_items, display_config, smoothness_degree,
                                                        curve_configs)
    else:
        data_preparation.process(specimen_items, display_config, default_y_column, curve_configs)

    prepared_data, graphic_elements = data_preparation.combine_data()

    if customizable:
        if layout_config is None:
            layout_config = LayoutSettings()

        settings = CustomizationSettings()
        layout.update(layout_config.to_dict())
        updated_layout = {
            **layout,
            'xaxis_title': f"{sample_controller.get_x_column()} ({Parameter.get_units(sample_controller.get_x_column())})",
            'yaxis_title': f"{default_y_column} ({Parameter.get_units(default_y_column)})"
        }

        layout = settings.apply_customizations(updated_layout)

    PlotRenderer(data=prepared_data, graphic_elements=graphic_elements, layout=layout, on_click=on_click,
                 add_axes_lines=add_axes_lines)


class DataPreparation:
    def __init__(self, sample_controller=SampleController()):
        """
        Инициализирует объекты DataPreparation с данными для кривых и точек.

        Args:
        curves_data (list): Список данных для кривых, каждый элемент - это словарь аргументов для go.Scatter.
        points_data (list): Список данных для точек, каждый элемент - это словарь аргументов для go.Scatter.
        """
        self.sample_controller = sample_controller
        self.curves: [[go.Scatter]] = []
        self.graphic_elements: [GraphicElement] = []

    def process(
        self,
        specimen_items: [SpecimenItem],
        display_config: DisplayConfig,
        default_y_column=Parameter.TSUSC.value,
        curve_configs: [PlotAppearanceSettings] = None,
    ) -> [[go.Scatter]]:
        for index, item in enumerate(specimen_items):
            config = None
            if not item.value.uploaded:
                continue
            if curve_configs is not None and len(curve_configs) != 0:
                config = curve_configs[index]
            self.curves.append(item.value.measurement.value.plot_data(
                self.sample_controller.get_x_column(),
                default_y_column,
                item.value.filename.value,
                config,
            ))
            for element in item.value.displayed_elements.value:
                if display_config.is_displayed(element.style):
                    self.graphic_elements.append(element)

    def combine_data(self):

        return self.curves, self.graphic_elements

    def process_only_second_derivative(
        self,
        specimen_items: [SpecimenItem],
        display_config: DisplayConfig,
        smoothness_degree=2,
        curve_configs: [PlotAppearanceSettings] = None,
    ):
        data_calc = DataCalculation()
        data_calc.set_second_derivative_strategy(SecondDerivativeCalculation, sigma=smoothness_degree)
        x_column = self.sample_controller.get_x_column()
        y_column = self.sample_controller.get_y_column()

        for index, item in enumerate(specimen_items):
            config = None
            if curve_configs is not None and len(curve_configs) != 0:
                config = curve_configs[index]
            self.curves.append(
                item.value.measurement.value.plot_second_derivative(x_column, y_column, data_calc, config))
            for element in item.value.displayed_elements.value:
                if display_config.is_displayed(element.style):
                    self.graphic_elements.append(element)
