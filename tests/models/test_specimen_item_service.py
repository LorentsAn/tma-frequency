import pytest

from tma.core.model.repository.specimen_item_repository import SpecimenItemRepository
from tma.core.service.services.specimen_item_service import SpecimenItemService


@pytest.fixture
def specimen_item_repository(mocker):
    return mocker.Mock(spec=SpecimenItemRepository)


@pytest.fixture
def specimen_item_service(specimen_item_repository):
    return SpecimenItemService(specimen_item_repository)


def test_get_specimen_item(specimen_item_service, specimen_item_repository):
    specimen_item_repository.get_by_id.return_value = "specimen_item"
    assert specimen_item_service.get_specimen_item_model(1) == "specimen_item"
    specimen_item_repository.get_by_id.assert_called_once_with(1)


def test_add_specimen_item(specimen_item_service, specimen_item_repository):
    specimen_item_repository.create_specimen_item.return_value = "new_specimen_item"
    assert specimen_item_service.add_specimen_item(1, 2, 'filename', 'file_name', 'file_extension',
                                                   False) == "new_specimen_item"
    specimen_item_repository.create_specimen_item.assert_called_once_with(1, 2, 'filename', 'file_name',
                                                                          'file_extension', False)


def test_update_specimen_item_details(specimen_item_service, specimen_item_repository):
    specimen_item_repository.update_specimen_item.return_value = "updated_specimen_item"
    assert specimen_item_service.update_specimen_item_details(1, filename="new_filename") == "updated_specimen_item"
    specimen_item_repository.update_specimen_item.assert_called_once_with(1, filename="new_filename")


def test_remove_specimen_item(specimen_item_service, specimen_item_repository):
    specimen_item_repository.delete_specimen_item.return_value = True
    assert specimen_item_service.remove_specimen_item(1) == True
    specimen_item_repository.delete_specimen_item.assert_called_once_with(1)
