from typing import Dict

import solara
from solara import DataFrame

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.controller.sample_controller import SampleController
from tma.multipages.components.plot_widget.display_config import DisplayConfig
from tma.multipages.components.plot_widget.plot_widget import PlotWidget
from tma.multipages.components.edit_data.click_data import EditController, InfoMessage, ErrorMessage
from tma.multipages.components.edit_data.specimen_edit import SpecimenEditBar
from tma.multipages.components.edit_data.susceptibility import ExclusiveCheckboxes
from tma.multipages.components.graphic_elements.style import PointTypes

new_values: solara.Reactive[Dict[str, float]] = solara.reactive({})


@solara.component
def EditMeasurementBar(sample_controller: SampleController, is_selected_points_bar_shows):
    if not is_selected_points_bar_shows:
        return
    with solara.Card("Selected point"):
        with solara.Column():
            units = list(EditController.edit_value.value.columns)
            for i in range(0, len(units), 3):
                with solara.Row():
                    for column in units[i:i + 3]:
                        value_str = EditController.edit_value.value.loc[:, column].to_string(
                            index=False) if EditController.edit_value.value is not None else ''
                        disabled = False if column != Parameter.TEMP.value else True
                        solara.InputFloat(
                            label=column,
                            value=value_str,
                            disabled=disabled,
                            continuous_update=True,
                        )
        InfoMessage()
        with solara.Column():
            solara.Button(
                label="Update",
                color='warning',
                outlined=True,
                on_click=lambda: EditController.handle_update(sample_controller, new_values.value)
            )
            solara.Button(label="Delete", color='error', outlined=True,
                          on_click=lambda: EditController.handle_delete(sample_controller))


@solara.component
def EmptyEquipmentEditPanel(sample_controller: SampleController, set_show_outline_points):
    def select_interpolate_method(method):
        SampleController.set_interpolate_method(sample_controller.get_selected_specimen_item(), method)

    def smooth():
        sample_controller.smooth_specimen_item(smoothing_window_size)

    def add_outline_points():
        try:
            set_show_outline_points(False)
            error_message = sample_controller.detect_outline_points(threshold)
            if error_message is not None:
                set_info_message(error_message)
                return
            set_show_outline_points(True)
            set_info_message('')
        except:
            set_info_message('Unknown error')

    smoothing_window_size, set_smoothing_window_size = solara.use_state(5)
    threshold, set_threshold = solara.use_state(42.5)
    info_message, set_info_message = solara.use_state('')

    with solara.Card('Mark outlying measurements'):
        with solara.Column():
            if info_message != '':
                solara.Info(label=info_message)
            solara.InputFloat("Enter a float number", value=threshold, on_value=set_threshold)
            solara.Button("Mark", on_click=add_outline_points)
    with solara.Card('Smoothing curve'):
        with solara.Column():
            solara.InputInt("Enter a int number", value=smoothing_window_size, on_value=set_smoothing_window_size)
            solara.Button("Smooth", on_click=smooth)
    with solara.Card('Interpolation curve'):
        with solara.Column():
            solara.Select('Select interpolation', values=SampleController.get_interpolation_methods(),
                          value=sample_controller.get_selected_specimen_item().interpolate_method.value,
                          on_value=select_interpolate_method)


@solara.component
def DataFrameSpecimen(sample_controller: SampleController):
    def on_action_cell(column, cell_value):
        item = sample_controller.get_selected_specimen_item()
        cur_df = item.create_dataframe_for_all_columns()
        EditController.id_line_df_select.set(cell_value)
        edit_value = cur_df.iloc[cell_value].to_frame().T
        x_column = sample_controller.get_x_column()
        y_column = sample_controller.get_y_column()
        EditController.id_line_raw_select.set(
            sample_controller.find_line_by_xy(x_column, y_column, edit_value[x_column].iloc[0],
                                              edit_value[y_column].iloc[0]))

        EditController.edit_value.set(edit_value)
        EditController.click_data.set(None)

    cell_actions = [solara.CellAction(icon="mdi-pencil", name='Edit Point', on_click=on_action_cell)]

    item = sample_controller.get_selected_specimen_item()

    if item.df.value is not None:
        with solara.Card("Data table"):
            DataFrame(item.create_dataframe_for_all_columns(), items_per_page=10, cell_actions=cell_actions,
                      scrollable=True)
    else:
        solara.Text("No data to display")


@solara.component
def Page():
    sample_controller_model = SampleRepositoryController(session_id=solara.get_session_id())
    sample = sample_controller_model.get_sample()
    sample_controller = SampleController(sample)

    show_outline_points, set_show_outline_points = solara.use_state(False)

    def show_data(filename_value):
        index = sample_controller.on_file_item_select(filename_value)
        sample_controller_model.update_sample(selected_file_index=index)
        file_reference.set(sample_controller.get_selected_specimen_item())
        set_selected_points_bar_shows(False)
        sample_controller.reset_show_point(PointTypes.OutlinePoint.name)
        sample_controller.reset_show_point(PointTypes.CurrentUserPoint.name)

    def handle_click(click_data):
        if click_data is not None:
            EditController.handle_click(
                sample_controller=sample_controller,
                click_data=click_data,
                point_name=PointTypes.CurrentUserPoint.name,
            )
            set_selected_points_bar_shows(True)

    def update_specimen_name():
        EditController.set_specimen_name_error_message(sample_controller.update_sample_name(specimen_name.value))

    def reset_specimen_name():
        specimen_name.set(sample_controller.get_sample_name())

    def remove_sample():
        sample_controller.remove_sample()

    if not sample_controller.is_sample_created():
        solara.Info("No created samples, create one in home page")
        return

    is_show_points_reset, set_show_points_reset = solara.use_state(False)
    is_selected_points_bar_shows, set_selected_points_bar_shows = solara.use_state(False)

    @solara.use_effect
    def reset_show_points():
        if not is_show_points_reset:
            sample_controller.reset_show_point()
            set_show_points_reset(True)

    specimen_name = solara.reactive(sample_controller.get_sample_name())

    if sample_controller.get_selected_file_index() is not None:
        file_reference = solara.reactive(sample_controller.get_selected_specimen_item())
        with solara.Sidebar():
            with solara.Card("List of specimens"):
                uploaded_files = sample_controller.get_filenames_list(include_empty_source=False)
                selected_item = sample_controller.get_selected_specimen_item()
                solara.Select("File", values=uploaded_files, value=selected_item.filename.value, on_value=show_data)
            with solara.Card("Sample Info"):
                with solara.Column():
                    solara.InputText("Name", value=specimen_name, continuous_update=True)
                    ErrorMessage()
                    with solara.Row():
                        solara.Button("Update", on_click=update_specimen_name)
                        solara.Button("Reset", on_click=reset_specimen_name)
            # todo delete debug mode
            # with solara.Card("Specimen Settings"):
            #     solara.Select(label='Mode', values=ShowMode.get_enum_values(),
            #                   value=file_reference.value.show_mode.value, on_value=change_mode)
            #     with solara.Row():
            #         solara.Select(label='X-axis',
            #                       values=sample_controller.get_intersect_get_columns(y_column.value),
            #                       value=x_column.value, on_value=change_x_column)
            #         solara.Select(label='Y-axis',
            #                       values=sample_controller.get_intersect_get_columns(x_column.value),
            #                       value=y_column.value, on_value=change_y_column)

            with solara.Column():
                solara.Button(label='Remove sample', color='error', on_click=remove_sample)

        # EditMeasurementBar()
        with solara.Column():
            if file_reference.value is not None:
                try:
                    with solara.Row():
                        with solara.Card():
                            if file_reference.value is not None:
                                config = DisplayConfig(
                                    show_points=True,
                                    element_visibility={
                                        PointTypes.CurrentUserPoint.name: True,
                                        PointTypes.OutlinePoint.name: show_outline_points,
                                    }
                                )

                                range_yaxis = sample_controller.get_measurements_range_of_values()
                                PlotWidget(
                                    [solara.use_reactive(sample_controller.get_selected_specimen_item())],
                                    on_click=handle_click,
                                    sample_controller=sample_controller,
                                    default_y_column=sample_controller.get_y_column(),
                                    display_config=config,
                                    layout={
                                        'title_text': sample_controller.get_sample_name()
                                        if sample_controller.get_sample_name() != '' else 'Thermomagnetic Plot',
                                        'xaxis': dict(range=[range_yaxis[0] - 20, range_yaxis[1] + 20])
                                    },
                                )
                            with solara.Row():
                                if file_reference.value is not None:
                                    DataFrameSpecimen(sample_controller)
                                    EditMeasurementBar(sample_controller, is_selected_points_bar_shows)
                        with solara.Column():
                            with solara.Card(title='Susceptibility'):
                                ExclusiveCheckboxes(sample_controller, file_reference)
                            if file_reference.value.is_empty_furnace_or_cryostat_file():
                                EmptyEquipmentEditPanel(sample_controller, set_show_outline_points)
                            else:
                                SpecimenEditBar(sample_controller, file_reference)
                except IndexError:
                    solara.Info("No files, add some above")

            else:
                solara.Info("No files, add some above")
