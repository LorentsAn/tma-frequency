from tma.core.model.repository.specimen_item_repository import SpecimenItemRepository
from tma.core.service.sample.model.specimen_item import SpecimenItem


class SpecimenItemService:
    def __init__(self, specimen_item_repository: SpecimenItemRepository):
        self.specimen_item_repository = specimen_item_repository

    def get_specimen_item_model(self, specimen_item_id: int):
        return self.specimen_item_repository.get_by_id(specimen_item_id)

    def get_specimen_items_by_sample_id(self, sample_id: int):
        return self.specimen_item_repository.get_items_by_sample_id(sample_id=sample_id)

    def get_first_specimen_item_by_sample_id(self, sample_id: int):
        return self.specimen_item_repository.get_first_by_sample_id(sample_id)

    def get_specimen_item_by_sample_id_and_filename(self, sample_id: int, filename: str):
        return self.specimen_item_repository.get_by_sample_id_and_filename(sample_id, filename)

    def add_specimen_item(self, sample_id: int, filename: str, file_extension: str, is_empty_source: bool):
        return self.specimen_item_repository.create_specimen_item(
            sample_id, filename, file_extension, is_empty_source
        )

    def add_specimen_item_by_model(self, sample_id: int, specimen_item: SpecimenItem):
        return self.add_specimen_item(
            sample_id, specimen_item.filename.value, specimen_item.file.file_extension.value,
            specimen_item.is_empty_source_file
        )

    def add_list_specimen_items(self, specimen_items: list):
        results = []
        for item in specimen_items:
            result = self.add_specimen_item(
                item['sample_id'],
                item['filename'],
                item['file_name'],
                item['file_extension'],
                item['is_empty_source']
            )
            if result is not None:
                results.append(result)
        return results

    def update_specimen_item_details(self, specimen_item_id: int, **kwargs):
        return self.specimen_item_repository.update_specimen_item(specimen_item_id, **kwargs)

    def remove_specimen_items_by_sample_id(self, sample_id: int):
        return self.specimen_item_repository.delete_specimen_item_by_sample_id(sample_id)
