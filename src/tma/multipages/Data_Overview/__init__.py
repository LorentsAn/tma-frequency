import solara
from solara import FileDrop
from solara.lab.toestand import Ref

from tma.core.data.parser.exceptions.invalid_file_error import InvalidFileError
from tma.multipages.components.plot_widget.data_state import State, FileListItem
from tma.core.service.sample.model.specimen_item import SpecimenItem

from enum import Enum

from tma.multipages.components.plot_widget.plot_widget import PlotWidget


class SampleStatus(Enum):
    NOT_CREATED = "Not created"
    CREATED = "Created"
    RECREATED = "Recreated"

    def next_status(self):
        cls = self.__class__
        members = list(cls)
        index = members.index(self) + 1
        return members[index % len(members)]


@solara.component
def Page():
    is_sample_created, set_status = solara.use_state(SampleStatus.NOT_CREATED)
    state = State()

    def set_sample_status():
        set_status(is_sample_created.next_status())

    def create_sample():
        state.remove_sample()
        state.create_sample()
        set_sample_status()

    with solara.Sidebar():
        with solara.lab.Tabs():
            with solara.lab.Tab("File"):
                FileControls(state)
    SampleCreationControls(is_sample_created, create_sample, state)


@solara.component
def FileControls(state: State):
    error_message, set_error_message = solara.use_state('')

    def create_new_item(new_filename_value):
        try:
            if new_filename_value:
                new_item = SpecimenItem.load_from_file(new_filename_value, False)
                state.on_new(new_item)
                set_error_message('')
        except InvalidFileError as e:
            set_error_message(e.reason)
        except:
            set_error_message(
                "An error occurred, please try again later. Make sure that the files you are uploading are in a valid format.")

    with solara.Card("Controls", margin=0, elevation=0):
        solara.Button("Clear dataset", color="primary", text=True, outlined=True, on_click=state.reset)
        if error_message != '':
            solara.Error(label=error_message)
        FileDrop(on_file=create_new_item, on_total_progress=lambda *args: None, label="Drag file here", lazy=False)
        if state.files.value:
            for index, file_item in enumerate(state.files.value):
                file_ref = Ref(state.files.fields[index])
                FileListItem(file_ref, on_delete=state.on_delete)
        else:
            solara.Info("No files, add some above")


@solara.component
def SampleCreationControls(is_sample_created, create_sample, state: State):
    if state.has_uploaded_files():
        with solara.Sidebar():
            with solara.Column():
                solara.Button("Create a sample", color="primary", on_click=create_sample)
                if is_sample_created != SampleStatus.NOT_CREATED:
                    message = (
                        "You have created a sample. Upon re-pressing, your sample settings will be overwritten."
                        if is_sample_created == SampleStatus.CREATED
                        else "You recreated the sample. Old settings have been removed."
                    )
                    solara.Info(label=message, text=True, dense=False, outlined=True, icon=True)
        with solara.Card():
            PlotWidget([solara.reactive(item) for item in state.get_uploaded_file_items()])
