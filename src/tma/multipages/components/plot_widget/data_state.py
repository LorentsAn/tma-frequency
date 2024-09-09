from typing import List, Callable

import solara
import solara as sol
import reacton.ipyvuetify as v
from solara.lab.toestand import Ref

from tma.core.service.sample.controller.repository_controllers.specimen_item_controller import \
    SpecialItemRepositoryController
from tma.core.service.sample.controller.repository_controllers.sample_controller import SampleRepositoryController
from tma.core.service.sample.model import specimen_item


@sol.component
def FileListItem(item: sol.Reactive[specimen_item.SpecimenItem], on_delete: Callable[[
    specimen_item.SpecimenItem], None]):
    """
    A Solitude component for displaying an item in the file list.

    Attributes:
        item (sol.Reactive[FileItem]): Reactive element representing the FileItem instance.
        on_delete (Callable[[FileItem], None]): Callback function for handling file item deletion.

    Methods:
        __init__(file_item, on_delete): Initializes the FileListItem component with a file item and deletion callback.
    """
    with v.ListItem():
        sol.Checkbox(value=Ref(item.fields.uploaded), label=item.value.filename.value)
        sol.Button(icon_name="mdi-delete", icon=True, on_click=lambda: on_delete(item.value))


class State:
    """
    The State class manages the application states, including the list of uploaded files.

    Attributes:
        initial_files (List[FileItem]): Initial list of uploaded files.
        files (sol.reactive): Reactive element representing the list of uploaded files.

    Methods:
        on_new(file_item: FileItem): Adds a new file item to the list.
        on_delete(file_item: FileItem): Removes a file item from the list.
        reset(): Resets the list of uploaded files to the initial state.
        has_uploaded_files() -> bool: Checks if there are any uploaded files.
        get_uploaded_file_items() -> List[FileItem]: Returns a list of uploaded file items.
        get_uploaded_file_items_plain_list() -> List[str]: Returns a list of names of uploaded files.
        find_file_item_by_name(filename) -> FileItem or None: Finds a file item by its filename.
    """

    def __init__(self):
        self.sample_controller = SampleRepositoryController(solara.get_session_id())
        specimen_repository_controller = SpecialItemRepositoryController(self.sample_controller.sample_model)
        self.initial_files = specimen_repository_controller.get_specimen_items_list()
        initial_selected_index = -1
        self.files: [specimen_item.SpecimenItem] = sol.reactive(self.initial_files)
        self.selected_file_index = sol.reactive(initial_selected_index)

    def on_new(self, item: specimen_item.SpecimenItem):
        self.files.set([item] + self.files.value)
        if len(self.files.value) == 1:
            self.selected_file_index.value = 0

    def on_delete(self, item: specimen_item.SpecimenItem):
        new_files = list(self.files.value)
        new_files.remove(item)
        self.files.value = new_files

    def on_select(self, filename_value: str):
        index_by_filename = self.find_file_item_by_name(filename_value)
        if index_by_filename < len(self.files.value):
            self.selected_file_index.set(index_by_filename)

    def reset(self):
        self.files.value = []

    @staticmethod
    def remove_sample():
        sample_controller = SampleRepositoryController(solara.get_session_id())
        sample_controller.delete_sample(sample_controller.get_sample())

    def create_sample(self):
        selected_files = self.get_uploaded_file_items()
        sample_controller = SampleRepositoryController(solara.get_session_id())
        specimen_item_repository_controller = SpecialItemRepositoryController(sample_controller.sample_model)
        specimen_item_repository_controller.create_specimen_items(selected_files)

    def has_uploaded_files(self):
        return any(item for item in self.files.value if item.uploaded)

    def get_uploaded_file_items(self) -> List[specimen_item.SpecimenItem]:
        return [item for item in self.files.value if item.uploaded]

    def get_uploaded_file_items_plain_list(self) -> List[str]:
        return [item.filename.value for item in self.files.value if item.uploaded]

    def find_file_item_by_name(self, filename):
        files = self.find_file_items_by_names([filename])
        return files[0] if len(files) > 0 else None

    def find_file_items_by_names(self, names: [str]):
        indices = []
        if self.files.value:
            for index, item in enumerate(self.files.value):
                if item.file.file_name in names:
                    indices.append(index)
        return indices
