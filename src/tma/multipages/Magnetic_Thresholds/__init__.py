from typing import Dict, List, Tuple, Callable

import solara
import reacton.ipyvuetify as v
from solara import Reactive

from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.multipages.components.plot_widget.display_config import DisplayConfig
from tma.multipages.components.plot_widget.plot_widget import PlotWidget
from tma.multipages.components.edit_data.click_data import DerivativeClickController
from tma.multipages.components.graphic_elements.point import Point
from tma.multipages.components.graphic_elements.style import PointTypes, LineTypes


@solara.component
def InputField(
    sample_controller: SampleController,
    curie_points_current: Reactive[Dict[int, List[Tuple[float, float]]]],
):
    info_message, set_info_message = solara.use_state('')

    def get_temperature():
        point = sample_controller.get_displayed_element(PointTypes.CurrentUserPointDerivative.name)
        if point is None:
            return 0.0
        return point.x[0]

    def save_curie_point():
        if DerivativeClickController.click_data.value is None:
            set_info_message('Select a point on the graph')
            return

        error_message = sample_controller.create_curie_point(
            column_name=sample_controller.get_y_column(),
            id_plot_select=DerivativeClickController.id_plot_select.value,
            temperature_value=DerivativeClickController.edit_value.value.iloc[-1][sample_controller.get_x_column()],
            magnetization_value=DerivativeClickController.edit_value.value.iloc[-1][sample_controller.get_y_column()]
        )
        if error_message is not None:
            set_info_message(error_message)
            return
        curie_points_current.set(sample_controller.get_selected_specimen_item().get_sorted_curie_points())
        set_info_message('')

    if info_message != '':
        solara.Info(label=info_message)
    with solara.Column():
        solara.HTML(unsafe_innerHTML=f"""
    <div style="color: black; font-size: 16px; border-bottom: 1px dashed #000;">
        <p>Curie point</p>
        <h2 style="margin-top: 0;">
        {get_temperature()}
        </h2>
    </div>
        """)
        solara.Button(label='save', color="primary", on_click=save_curie_point)


@solara.component
def CuriePointField(
    index: int, curie_point: Tuple[float, float], color: str, on_delete=Callable[[float], None]):
    with v.ListItem():
        with v.ListItemContent():
            with v.ListItemTitle():
                # index + 1 because counting starts from zero
                solara.HTML(tag="span", unsafe_innerHTML=f"{index + 1}) Temp: {str(curie_point[0])}°C",
                            style=f"font-weight: bold; color: {color};")
                solara.Button(icon_name="mdi-delete", icon=True,
                              on_click=lambda: on_delete(curie_point[0])
                              )
    # with v.ListItem():
    #     solara.Checkbox(value=solara.reactive(False), label=str(curie_point[0]))
    #     solara.Button(icon_name="mdi-delete", icon=True,
    #                   # on_click=lambda: on_delete(item.value)
    #                   )


@solara.component
def HeatingCuriePointList(curie_points: List[Tuple[float, float]], on_delete=Callable[[float], None]):
    with solara.Card(title="Heating curve"):
        for index, point in enumerate(curie_points):
            CuriePointField(index, point, '#f23557', on_delete)


@solara.component
def CoolingCuriePointList(curie_points: List[Tuple[float, float]], on_delete=Callable[[float], None]):
    with solara.Card(title="Cooling curve"):
        for index, point in enumerate(curie_points):
            CuriePointField(index, point, 'rgb(57, 116, 203)', on_delete)


@solara.component
def Page():
    sample_controller_model = SampleRepositoryController(session_id=solara.get_session_id())
    sample = sample_controller_model.get_sample()
    sample_controller = (SampleController(sample))
    info_message, set_info_message = solara.use_state('')

    if not sample_controller.is_sample_created():
        solara.Info("No created samples, create one in home page")
        return

    curie_points_calculated, set_curie_points_calculated = solara.use_state(False)
    smoothness_degree, set_smoothness_degree = solara.use_state(2)
    show_smoothness_degree, set_show_smoothness_degree = solara.use_state(2)
    threshold_of_inflection_point, set_threshold_of_inflection_point = solara.use_state(0)
    threshold_of_maximum_values_first_derivative, set_threshold_of_maximum_values_first_derivative = solara.use_state(0)
    threshold_of_maximum_values_second_derivative, set_threshold_of_maximum_values_second_derivative = solara.use_state(
        0)

    def on_delete(temperature: float):
        curie_points_selected = sample_controller.get_selected_specimen_item().get_curie_points(
            sample_controller.get_y_column())
        try:
            value_index = curie_points_selected.get('x').index(temperature)
        except ValueError:
            return
        sample_controller.delete_curie_point(temperature, curie_points_selected.get('y')[value_index])
        curie_points_current.set(sample_controller.get_selected_specimen_item().get_sorted_curie_points())

    def calculate_curie_points():
        sample_controller.calculate_curie_points(
            smoothness_degree,
            threshold_of_inflection_point,
            threshold_of_maximum_values_second_derivative,
            threshold_of_maximum_values_first_derivative
        )

    @solara.use_effect
    def run_curie_points_calculation():
        if not curie_points_calculated:
            curie_points_selected = sample_controller.get_selected_specimen_item().get_curie_points(
                sample_controller.get_y_column())
            sample_controller.reset_show_point(name=PointTypes.StoredCuriePoints.name)
            calculate_curie_points()
            sample_controller.set_displayed_element(element_type=PointTypes.StoredCuriePoints,
                                                    x_values=curie_points_selected.get('x'),
                                                    y_values=curie_points_selected.get('y'))
            sample_controller.set_displayed_element(element_type=LineTypes.StoredCurieLine,
                                                    x_values=curie_points_selected.get('x'))
            sample_controller.set_displayed_element(element_type=LineTypes.BaseLine, y_values=[0])
            set_curie_points_calculated(True)

    def change_selected_item(filename_value):
        index = sample_controller.on_file_item_select(filename_value)
        sample_controller_model.update_sample(selected_file_index=index)
        file_reference.set(sample_controller.get_selected_specimen_item())
        set_curie_points_calculated(False)

    def change_sigma_value(sigma):
        if not 0 < sigma < 10:
            set_info_message('Smoothness degree must be greater than 0 and smaller than 10')
            return
        set_smoothness_degree(sigma)
        set_curie_points_calculated(False)
        set_info_message('')

    def change_threshold():
        if threshold_of_inflection_point < 0:
            set_info_message('the threshold value must be at least zero')
            return
        calculate_curie_points()
        set_info_message('')

    curie_points_current = solara.reactive(sample_controller.get_selected_specimen_item().get_sorted_curie_points())

    if sample_controller.get_selected_file_index() is not None:
        file_reference = solara.reactive(sample_controller.get_selected_specimen_item())

        show_inflection_point, set_show_inflection_point = solara.use_state(True)
        show_max_second_derivative_point, set_show_max_second_derivative_point = solara.use_state(True)
        show_max_first_derivative_point, set_show_max_first_derivative_point = solara.use_state(True)
        show_stored_curie_point, set_show_stored_curie_point = solara.use_state(True)

        with solara.Sidebar():
            with solara.Card("List of specimens"):
                uploaded_files = sample_controller.get_filenames_list(include_empty_source=False)
                selected_item = sample_controller.get_selected_specimen_item()
                solara.Select("File", values=uploaded_files, value=selected_item.filename.value,
                              on_value=change_selected_item)
            if info_message != '':
                solara.Warning(label=info_message)
            with solara.Card(subtitle='The degree of smoothness of the second derivative graph'):
                with solara.Column():
                    solara.InputFloat(label='Degree of smoothness', value=show_smoothness_degree,
                                      on_value=set_show_smoothness_degree)
                    solara.Button(label='Calculate', on_click=lambda: change_sigma_value(show_smoothness_degree))
            with solara.Card(subtitle='Threshold for determining inflection points'):
                with solara.Column():
                    solara.InputFloat(label='Threshold', value=threshold_of_inflection_point,
                                      on_value=set_threshold_of_inflection_point)
                    solara.Button(label='Detect', on_click=change_threshold)
            with solara.Card(subtitle='Threshold for determining maximum values of the first derivative'):
                with solara.Column():
                    solara.InputFloat(label='Threshold', value=threshold_of_maximum_values_first_derivative,
                                      on_value=set_threshold_of_maximum_values_first_derivative)
                    solara.Button(label='Detect', on_click=change_threshold)
            with solara.Card(subtitle='Threshold for determining maximum values of the second derivative'):
                with solara.Column():
                    solara.InputFloat(label='Threshold', value=threshold_of_maximum_values_second_derivative,
                                      on_value=set_threshold_of_maximum_values_second_derivative)
                    solara.Button(label='Detect', on_click=change_threshold)
            with solara.Card('Display points'):
                solara.Checkbox(label=PointTypes.InflectionPoint.name, value=show_inflection_point,
                                on_value=set_show_inflection_point)
                solara.Checkbox(label=PointTypes.MaxFirstDerivative.name, value=show_max_first_derivative_point,
                                on_value=set_show_max_first_derivative_point)
                solara.Checkbox(label=PointTypes.MaxSecondDerivative.name, value=show_max_second_derivative_point,
                                on_value=set_show_max_second_derivative_point)
                solara.Checkbox(label=PointTypes.StoredCuriePoints.name, value=show_stored_curie_point,
                                on_value=set_show_stored_curie_point)

        if file_reference.value is not None:
            with solara.Card():
                config = DisplayConfig(
                    show_points=True,
                    element_visibility={
                        PointTypes.MaxSecondDerivative.name: show_max_second_derivative_point,
                        PointTypes.InflectionPoint.name: show_inflection_point,
                        PointTypes.StoredCuriePoints.name: show_stored_curie_point,
                        PointTypes.MaxFirstDerivative.name: show_max_first_derivative_point,
                        PointTypes.CurrentUserPoint.name: True,
                    }
                )

                range_yaxis = sample_controller.get_measurements_range_of_values()
                PlotWidget(
                    [solara.use_reactive(sample_controller.get_selected_specimen_item())],
                    sample_controller=sample_controller,
                    default_y_column=sample_controller.get_y_column(),
                    on_click=lambda click_data: DerivativeClickController.handle_click(
                        sample_controller=sample_controller,
                        click_data=click_data,
                        point_name=PointTypes.CurrentUserPoint.name),
                    show_data_type='all',
                    layout={
                        'title_text': sample_controller.get_sample_name()
                        if sample_controller.get_sample_name() != '' else 'Thermomagnetic Plot',
                        'xaxis': dict(range=[range_yaxis[0] - 20, range_yaxis[1] + 20]),
                        'width': 1400,
                        'height': 600
                    },
                    display_config=config,
                )

            with solara.Card():
                config = DisplayConfig(
                    show_points=True,
                    show_lines=True,
                    element_visibility={
                        LineTypes.MaxSecondDerivativeLine.name: show_max_second_derivative_point,
                        LineTypes.InflectionPointLine.name: show_inflection_point,
                        LineTypes.StoredCurieLine.name: show_stored_curie_point,
                        LineTypes.MaxFirstDerivative.name: show_max_first_derivative_point,
                        PointTypes.CurrentUserPointDerivative.name: True,
                    }
                )

                PlotWidget(
                    [solara.use_reactive(sample_controller.get_selected_specimen_item())],
                    sample_controller=sample_controller,
                    default_y_column=sample_controller.get_y_column(),
                    on_click=lambda click_data: DerivativeClickController.handle_click(
                        sample_controller=sample_controller,
                        click_data=click_data,
                        point_name=PointTypes.CurrentUserPointDerivative.name),
                    show_data_type='second_derivative',
                    smoothness_degree=smoothness_degree,
                    layout={
                        'title_text': 'Second Derivative Plot',
                        'width': 1300,
                        'height': 500},
                    display_config=config,
                )

            with solara.VBox():
                with solara.GridFixed(columns=3):
                    InputField(sample_controller, curie_points_current)
                    heating_plot_index = 0
                    cooling_plot_index = 1
                    for key, curie_point in curie_points_current.value.items():
                        if key % 2 == heating_plot_index:
                            HeatingCuriePointList(curie_point, on_delete)
                        if key % 2 == cooling_plot_index:
                            CoolingCuriePointList(curie_point, on_delete)
