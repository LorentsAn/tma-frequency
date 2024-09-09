from typing import List, Optional

import solara

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.sample.model.specimen_item import SpecimenItem


class Sample:
    def __init__(
        self,
        sample_id=1000,  # special id
        x_column=Parameter.TEMP.value,
        y_column=Parameter.TSUSC.value,
        name='',
    ):
        self.sample_id: int
        self.specimen_items: List[SpecimenItem] = []
        self.x_column: solara.Reactive[str] = solara.reactive(x_column)
        self.y_column: solara.Reactive[str] = solara.reactive(y_column)
        self.name: solara.Reactive[str] = solara.reactive(name)

        initial_selected_index = 0
        self.selected_file_index = initial_selected_index

    def add_specimen_items(self, specimen_items: List[SpecimenItem]):
        """
        Adds a list of SpecimenItem to the instance's pool.

        Args:
            specimen_items: The list of SpecimenItem to add.
        """
        self.specimen_items.extend(specimen_items)

    def update_x_column(self, x_column):
        self.x_column.set(x_column)

    def update_y_column(self, y_column):
        self.y_column.set(y_column)

    def update_sample_name(self, sample_name):
        self.name.set(sample_name)

    def remove_specimen_item(self, specimen_item):
        """
        Removes a SpecimenItem from the instance's pool.

        Args:
            specimen_item: The SpecimenItem to remove.
        """
        self.specimen_items.remove(specimen_item)

    def get_specimen_items(self) -> List[SpecimenItem]:
        """
        Returns all SpecimenItems in the instance's pool.

        Returns:
            A list of SpecimenItems.
        """
        return self.specimen_items

    def get_ap_specimen_items(self) -> List[SpecimenItem]:
        return [item for item in self.specimen_items if item.filename.value.startswith("AP")]

    def get_x_column(self) -> str:
        return self.x_column.value

    def get_y_column(self) -> str:
        return self.y_column.value

    def get_sample_name(self) -> str:
        return self.name.value

    def clear_pool(self):
        """
        Clears all SpecimenItems from the instance's pool and resets the name.
        """
        self.specimen_items = []
        self.name.set('')

    def get_specimen_item_by_filename(self, filename) -> Optional[SpecimenItem]:
        """
        Retrieves a SpecimenItem by its filename.

        Args:
            filename: The filename to search for.

        Returns:
            The SpecimenItem with the specified filename, or None if not found.
        """
        for specimen_item in self.specimen_items:
            if specimen_item.filename.value == filename:
                return specimen_item
        return None

    def get_index_specimen_item_by_filename(self, filename) -> Optional[int]:
        """
        Retrieves the index of a SpecimenItem by its filename.

        Args:
            filename: The filename to search for.

        Returns:
            The index of the SpecimenItem, or None if not found.
        """
        for index, specimen_item in enumerate(self.specimen_items):
            if specimen_item.filename.value == filename:
                return index
        return None

    def get_specimen_item_by_index(self, index):
        if 0 <= index < len(self.specimen_items):
            return self.specimen_items[index]
        return None

    def is_specimen_item_corrected(self, specimen_item_index) -> bool:
        item = self.get_specimen_item_by_index(specimen_item_index)
        if item is not None:
            return item.y_column == Parameter.CSUSC.value
        return False

    def is_sample_created(self) -> bool:
        """
        Checks if at least one SpecimenItem has been added to the pool.

        Returns:
            True if the pool is not empty, False otherwise.
        """
        return bool(self.specimen_items)

    def clear_fields(self):
        """
        Clears all fields of the instance, resetting it to default values.
        """

        self.specimen_items = []
        self.update_x_column(Parameter.TEMP.value)
        self.update_y_column(Parameter.NSUSC.value)
        self.name.set('')

    def is_furnace_file(self, specimen_item_index) -> bool:
        item = self.get_specimen_item_by_index(specimen_item_index)
        return item is not None and item.is_furnace_file()

    def is_furnace_constant(self, specimen_item_index) -> bool:
        item = self.get_specimen_item_by_index(specimen_item_index)
        return item is not None and item.is_furnace_constant()
