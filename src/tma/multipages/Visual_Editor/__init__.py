import copy
from dataclasses import dataclass
from typing import List, Dict, Any, Callable

import solara
import reacton.ipyvuetify as v

from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.model.displayed_elements import DisplayedElementsManager
from tma.multipages.components.plot_widget.display_config import DisplayConfig
from tma.multipages.components.plot_widget.plot_widget import PlotWidget
from tma.multipages.components.graphic_elements.layout_settings import LayoutSettings
from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings
from tma.multipages.components.graphic_elements.style import PointTypes, LineTypes, PointFactory
from tma.multipages.components.visual_editor.click_controllers.measurement__click import ClickController
from tma.multipages.components.visual_editor.click_controllers.second_derivative_click import \
    SecondDerivativeClickController
from tma.multipages.components.visual_editor.color_box import ColorBox
from tma.multipages.components.visual_editor.legend_box import LegendBox
from tma.multipages.components.visual_editor.line_box import LineBox
from tma.multipages.components.visual_editor.marker_box import MarkerBox
from tma.multipages.components.visual_editor.plot_settings_values import markers_styles, modes_with_markers
from tma.multipages.components.visual_editor.point_settings_modal import PointSettingsModal

curves_config: solara.Reactive[List[PlotAppearanceSettings]] = solara.reactive([])
second_derivative_curves_config: solara.Reactive[List[PlotAppearanceSettings]] = solara.reactive([])
layout_config: solara.Reactive[LayoutSettings] = solara.reactive(LayoutSettings())

click_controller = ClickController()
derivative_click_controller = SecondDerivativeClickController()
config = DisplayConfig(
    show_points=True,
    element_visibility={
        PointTypes.StoredCuriePoints.name: True,
        PointTypes.CurrentUserPoint.name: True,
    }
)

config_derivative = DisplayConfig(
    show_points=True,
    element_visibility={
        PointTypes.CurrentUserPointDerivative.name: True,
    }
)


@solara.component
def Page():
    sample_controller_model = SampleRepositoryController(session_id=solara.get_session_id())
    sample = sample_controller_model.get_sample()
    sample_controller = (SampleController(sample))
    render_trigger, set_render_trigger = solara.use_state(0)  # State to force re-render

    if not sample_controller.is_sample_created():
        solara.Info("No created samples, create one in home page")
        return

    def trigger_update():
        set_render_trigger(render_trigger + 1)

    info_message, set_info_message = solara.use_state('')
    current_config, set_current_config = solara.use_state(None)  # State to store the current configuration
    current_graph_plot_id, set_current_graph_plot_id = solara.use_state(0)
    current_graph_is_cooling, set_current_graph_is_cooling = solara.use_state(False)

    curie_points_calculated, set_curie_points_calculated = solara.use_state(False)

    def calculate_curie_points(specimen_item):
        sample_controller.calculate_curie_points(
            smoothness_degree,
            show_critical_points=False,
            specimen_item=specimen_item
        )

    @solara.use_effect
    def run_curie_points_calculation():
        if not curie_points_calculated:
            result = {}
            for index, item in enumerate(displayed_specimen_items):
                calculate_curie_points(item)
                curie_points_selected = item.get_curie_points(sample_controller.get_y_column())
                updated_item = sample_controller.set_displayed_element(
                    element_type=PointTypes.StoredCuriePoints,
                    x_values=curie_points_selected.get('x'),
                    y_values=curie_points_selected.get('y'),
                    update=True,
                    specimen_item=item
                )
                result[index] = copy.deepcopy(updated_item.displayed_elements.value)

            set_curie_points_calculated(True)

            new_displayed_specimen_items = [
                update_item_display_elements(item, result[index])
                for index, item in enumerate(displayed_specimen_items)
            ]

            set_displayed_specimen_items(new_displayed_specimen_items)

    def update_item_display_elements(item, updated_elements):
        item.displayed_elements.set(copy.deepcopy(updated_elements))
        return item

    def on_specimen_item_click(item, value):
        if value:
            item.uploaded = True
        else:
            item.uploaded = False

        # Создание нового списка с обновленными элементами
        new_displayed_specimen_items = []
        for i in displayed_specimen_items:
            if i.filename.value == item.filename.value:
                new_displayed_specimen_items.append(item)  # Обновленный элемент
            else:
                new_displayed_specimen_items.append(i)

        set_displayed_specimen_items(new_displayed_specimen_items)

    def on_second_derivative_item_click(item, value):
        if value:
            new_displayed_specimen_items = displayed_second_derivative_items + [item]
        else:
            new_displayed_specimen_items = [i for i in displayed_second_derivative_items if
                                            i.filename.value != item.filename.value]

        set_displayed_second_derivative_items(new_displayed_specimen_items)

    def change_sigma_value(sigma):
        if not 0 < sigma < 10:
            set_info_message('Smoothness degree must be greater than 0 and smaller than 10')
            return
        set_smoothness_degree(sigma)
        set_info_message('')

    if not sample_controller.is_sample_created():
        solara.Info("No created samples, create one in home page")
        return

    specimen_items = [item for item in sample_controller.sample.value.get_specimen_items() if
                      not item.is_empty_source_file]

    displayed_specimen_items, set_displayed_specimen_items = solara.use_state(specimen_items)
    displayed_second_derivative_items, set_displayed_second_derivative_items = solara.use_state(specimen_items)

    config_inited, set_config_inited = solara.use_state(False)
    solara.use_effect(lambda: None, [curves_config.value])
    solara.use_effect(lambda: None, [second_derivative_curves_config.value])

    @solara.use_effect
    def init_curves_config():
        if not config_inited:
            curves_config.set([PlotAppearanceSettings(item.filename.value) for item in displayed_specimen_items])
            second_derivative_curves_config.set(
                [PlotAppearanceSettings(item.filename.value) for item in displayed_specimen_items])

        set_config_inited(True)

    window_size_width, set_window_size_width = solara.use_state(None)
    window_size_height, set_window_size_height = solara.use_state(None)

    with solara.Sidebar():
        if len(specimen_items) > 0:

            with solara.Column():
                with solara.Card("Files"):
                    for index, file_item in enumerate(specimen_items):
                        with v.ListItem():
                            solara.Checkbox(
                                value=file_item.uploaded,
                                label=file_item.filename.value,
                                on_value=lambda value, item=file_item: on_specimen_item_click(item, value)
                            )
                with solara.Card("Second Derivative"):
                    show_second_derivative_plot, set_show_second_derivative_plot = solara.use_state(False)
                    smoothness_degree, set_smoothness_degree = solara.use_state(2)
                    second_derivative_title_text, set_second_derivative_title_text = solara.use_state(
                        "Second Derivative Plot")

                    with solara.Column():
                        solara.Switch(label='Add second derivative plot', value=show_second_derivative_plot,
                                      on_value=set_show_second_derivative_plot)
                        if show_second_derivative_plot:
                            solara.InputText(label='Plot Name', on_value=set_second_derivative_title_text,
                                             value=second_derivative_title_text)
                            solara.Text('Files', style={"flex": "1", "font-size": "20px", "font-weight": "bold", })
                            for index, file_item in enumerate(specimen_items):
                                with v.ListItem():
                                    solara.Checkbox(
                                        value=file_item.uploaded,
                                        label=file_item.filename.value,
                                        on_value=lambda value, item=file_item: on_second_derivative_item_click(item,
                                                                                                               value)
                                    )
                            solara.InputFloat(label='Degree of smoothness', value=smoothness_degree,
                                              on_value=change_sigma_value)
                            solara.Button(label='Smooth', on_click=lambda: change_sigma_value(smoothness_degree))

                with solara.Card('Display'):
                    solara.Checkbox(label='Lines')
                    solara.Checkbox(label='Symbols')
                    solara.Checkbox(label='Legend')
        else:
            solara.Info("No files, add some above")

    def handle_click(graph_type, click_data, set_current_graph_type, set_current_graph_name):
        if graph_type == 'curves':
            click_controller.handle_click(
                sample_controller=sample_controller,
                click_data=click_data,
                point_name=PointTypes.CurrentUserPointDerivative.name,
                specimen_items=displayed_specimen_items,
            )
            set_current_config(curves_config)
            set_current_graph_plot_id(click_controller.id_plot_select.value)
            set_current_graph_is_cooling(click_controller.is_cooling_plot.value)
            set_current_graph_name(displayed_specimen_items[current_graph_plot_id].filename.value +
                                   (' cooling ' if current_graph_is_cooling else ' heating ') + 'curve')
            set_current_graph_type('Measurements Curves')
        elif graph_type == 'second_derivative':
            derivative_click_controller.handle_click(
                sample_controller=sample_controller,
                click_data=click_data,
                point_name=PointTypes.CurrentUserPointDerivative.name,
                specimen_items=displayed_specimen_items,
            )
            set_current_config(second_derivative_curves_config)
            set_current_graph_plot_id(derivative_click_controller.id_plot_select.value)
            set_current_graph_is_cooling(derivative_click_controller.is_cooling_plot.value)
            set_current_graph_name(displayed_specimen_items[current_graph_plot_id].filename.value +
                                   (
                                       ' second derivative cooling ' if current_graph_is_cooling else ' heating ') + 'curve')
            set_current_graph_type('Second Derivative Curves')

    with solara.GridFixed(
        columns=3,  # 2 columns for the first component and 1 column for the second
        column_gap="10px",
        row_gap="10px",
        align_items="stretch",
        justify_items="stretch"
    ):
        with solara.Column(style={"grid-column": "span 2"}):
            show_dialog, set_show_dialog = solara.use_state(False)
            previous_state_config, set_previous_state_config = solara.use_state(None)
            current_graph_type, set_current_graph_type = solara.use_state('')
            current_graph_name, set_current_graph_name = solara.use_state('')

            def open_dialog():
                # Use deep copy to create an independent copy of the state
                set_previous_state_config(copy.deepcopy(current_config.value))
                set_show_dialog(True)

            def on_confirm():
                set_previous_state_config(None)
                set_show_dialog(False)

            def on_cancel():
                # Restore the previous state using deep copy to avoid reference issues
                config = copy.deepcopy(previous_state_config)
                if current_graph_name == 'Second Derivative Curves':
                    second_derivative_curves_config.set(config)
                else:
                    curves_config.set(config)
                set_current_config(curves_config)
                set_show_dialog(False)
                trigger_update()

            range_yaxis = sample_controller.get_measurements_range_of_values()
            with solara.Column():
                if curves_config.value:
                    PlotWidget(
                        [solara.reactive(item) for item in displayed_specimen_items],
                        sample_controller=sample_controller,
                        default_y_column=sample_controller.get_y_column(),
                        show_data_type='all',
                        on_click=lambda click_data: handle_click('curves', click_data, set_current_graph_type,
                                                                 set_current_graph_name),
                        layout={
                            'title_text': sample_controller.get_sample_name()
                            if sample_controller.get_sample_name() != '' else 'Thermomagnetic Plot',
                            'xaxis': dict(range=[-220, range_yaxis[1] + 20]),
                            **({'width': window_size_width} if window_size_width is not None else {}),
                            **({'height': window_size_height} if window_size_height is not None else {})
                        },
                        display_config=config,
                        curve_configs=curves_config.value,
                        layout_config=layout_config.value,
                    )

                if current_graph_type == '':
                    solara.Info('Please double click on the curve to select')
                else:
                    solara.Button(f"Edit: {current_graph_type}", icon_name="mdi-pencil", on_click=open_dialog, )

            solara.lab.ConfirmationDialog(
                open=show_dialog,
                title="Edit Curve",
                content=CurveSettingsModal(current_config, current_graph_plot_id, current_graph_is_cooling,
                                           trigger_update),
                on_ok=on_confirm,
                on_cancel=on_cancel
            )

            if show_second_derivative_plot:
                PlotWidget(
                    [solara.reactive(item) for item in displayed_second_derivative_items],
                    sample_controller=sample_controller,
                    default_y_column=sample_controller.get_y_column(),
                    on_click=lambda click_data: handle_click('second_derivative', click_data, set_current_graph_type,
                                                             set_current_graph_name),
                    show_data_type='second_derivative',
                    smoothness_degree=smoothness_degree,
                    layout={
                        'title_text': second_derivative_title_text,
                        **({'width': window_size_width} if window_size_width is not None else {}),
                        **({'height': window_size_height} if window_size_height is not None else {})
                    },
                    display_config=config_derivative,
                    curve_configs=second_derivative_curves_config.value,
                    layout_config=layout_config.value,
                )
        with solara.Column():
            MarkerStyleComponent(displayed_specimen_items, config, trigger_update)
            with solara.Card():
                LegendBox(current_config, layout_config, current_graph_plot_id, current_graph_is_cooling,
                          trigger_update)
            with solara.Card():
                solara.SliderInt(label="Window width", value=(window_size_width if window_size_width else 700),
                                 min=100, max=2000,
                                 on_value=set_window_size_width)
                solara.SliderInt(label="Window height", value=(window_size_height if window_size_height else 300),
                                 min=100, max=1200,
                                 on_value=set_window_size_height)


@solara.component
def CurveSettingsModal(current_config, current_graph_plot_id, current_graph_is_cooling, trigger_update):
    def on_color_click(color):
        if current_graph_is_cooling:
            current_config.value[current_graph_plot_id].update_cooling_settings(color=color)
        else:
            current_config.value[current_graph_plot_id].update_heating_settings(color=color)
        current_config.value = list(current_config.value)
        trigger_update()  # Trigger re-rendering

    with solara.Column():
        with solara.Card():
            solara.Checkbox(label='Heating curve')
            ColorBox(on_color_click)
    with solara.Column():
        with solara.Card("Line style"):
            LineBox(current_config, current_graph_plot_id, current_graph_is_cooling,
                    trigger_update)
        with solara.Card("Marker style"):
            MarkerBox(current_config, current_graph_plot_id, current_graph_is_cooling,
                      trigger_update)


@solara.component
def MarkerStyleComponent(displayed_specimen_items, config, trigger_update):
    show_mark_style_dialog, set_show_mark_style_dialog = solara.use_state(False)
    current_point_settings: Dict[str, Any]
    set_current_point_settings: Callable[[Dict[str, Any]], None]
    current_point_settings, set_current_point_settings = solara.use_state({})
    point_factory = PointFactory()

    def toggle_point_visibility(point_name):
        config.element_visibility[point_name] = not config.element_visibility.get(point_name, False)
        trigger_update()

    def open_mark_style_dialog(point_name):
        set_selected_point_name(point_name)
        point_type = point_factory.get_point_type(point_name)
        if point_type:
            set_current_point_settings({
                "color": point_type.color,
                "size": point_type.size,
                "symbol": point_type.symbol,
                "marker_line_width": point_type.marker_line_width,
                "marker_line_color": point_type.marker_line_color,
                "custom_name": point_type.custom_name,
            })
            set_show_mark_style_dialog(True)

    def on_mark_style_confirm():
        if selected_point_name and current_point_settings:
            # Обновить PointType в point_factory
            point_factory.update_point_type(
                key=selected_point_name,
                color=current_point_settings.get("color"),
                size=current_point_settings.get("size"),
                symbol=current_point_settings.get("symbol"),
                marker_line_width=current_point_settings.get("marker_line_width"),
                marker_line_color=current_point_settings.get("marker_line_color"),
                custom_name=current_point_settings.get("custom_name"),
            )

            # Обновить все точки в displayed_specimen_items с таким же именем
            for sublist in displayed_specimen_items:
                for element in sublist.displayed_elements.value:
                    if element.style.name == selected_point_name:
                        element.style.color = current_point_settings.get("color")
                        element.style.size = current_point_settings.get("size")
                        element.style.symbol = current_point_settings.get("symbol")
                        element.style.marker_line_width = current_point_settings.get("marker_line_width")
                        element.style.marker_line_color = current_point_settings.get("marker_line_color")
                        element.style.custom_name = current_point_settings.get("custom_name")
            trigger_update()

        set_show_mark_style_dialog(False)

    def on_mark_style_cancel():
        set_show_mark_style_dialog(False)

    selected_point_name, set_selected_point_name = solara.use_state(None)

    solara.lab.ConfirmationDialog(
        open=show_mark_style_dialog,
        title="Edit Point Style",
        content=PointSettingsModal(current_point_settings, set_current_point_settings),
        on_ok=on_mark_style_confirm,
        on_cancel=on_mark_style_cancel
    )

    with solara.Card('Points'):
        points_to_edit = DisplayedElementsManager.filter_displayed_elements(
            [element for sublist in displayed_specimen_items for element in
             sublist.displayed_elements.value],
            config)
        print([point.style.name for point in points_to_edit])
        for point_name in set([point.style.name for point in points_to_edit]):
            with v.ListItem():
                with v.ListItemContent():
                    with v.ListItemTitle():
                        with solara.Row():
                            # index + 1 because counting starts from zero
                            solara.Button(label=f"Edit {str(point_name)}", icon_name="mdi-pencil",
                                          on_click=lambda pn=point_name: open_mark_style_dialog(pn), )
                            solara.Button(
                                icon_name=("mdi-eye" if config.element_visibility[point_name] else "mdi-eye-off"),
                                on_click=lambda pn=point_name: toggle_point_visibility(pn), icon=True, )
