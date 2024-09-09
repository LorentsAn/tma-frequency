import solara
import reacton.ipyvuetify as v

from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.multipages.components.plot_widget.plot_widget import PlotWidget


@solara.component
def FileListItem(item: solara.Reactive[SpecimenItem]):
    """
    A Solitude component for displaying an item in the file list.

    Attributes:
        item (sol.Reactive[FileItem]): Reactive element representing the FileItem instance.

    Methods:
        __init__(file_item, on_delete): Initializes the FileListItem component with a file item and deletion callback.
    """
    with v.ListItem():
        solara.Checkbox(value=item.value.uploaded, label=item.value.filename.value)


@solara.component
def Page():
    def on_click(item, value):
        if value:
            new_displayed_specimen_items = displayed_specimen_items + [item]
        else:
            new_displayed_specimen_items = [i for i in displayed_specimen_items if
                                            i.filename.value != item.filename.value]

        set_displayed_specimen_items(new_displayed_specimen_items)

    sample_controller_model = SampleRepositoryController(session_id=solara.get_session_id())
    sample = sample_controller_model.get_sample()
    sample_controller = SampleController(sample)

    if not sample_controller.is_sample_created():
        solara.Info("No created samples, create one in home page")
        return

    specimen_items = [item for item in sample_controller.sample.value.get_specimen_items() if
                      not item.is_empty_source_file]
    displayed_specimen_items, set_displayed_specimen_items = solara.use_state(specimen_items)

    if not sample_controller.check_specimen_item_has_column(include_empty_source=False):
        solara.Warning(label=f"Now you have set {sample_controller.get_y_column()} to be the y-axis value, "
                             f"but not all files have these values. Calculate them and return to the page")
        return

    if sample_controller.get_selected_file_index() is not None:
        with solara.Sidebar():
            if len(specimen_items) > 0:
                for index, file_item in enumerate(specimen_items):
                    with v.ListItem():
                        solara.Checkbox(
                            value=file_item.uploaded,
                            label=file_item.filename.value,
                            on_value=lambda value, item=file_item: on_click(item, value)
                        )
            else:
                solara.Info("No files, add some above")
        with solara.Card():
            PlotWidget(
                [solara.reactive(item) for item in displayed_specimen_items],
                sample_controller=sample_controller,
                default_y_column=sample_controller.get_y_column(),
                layout={
                    'xaxis': dict(range=[-220, 720])
                },
            )
