import pytest

from tma.core.model.repository.sample_repository import SampleRepository
from tma.core.service.services.sample_service import SampleService


@pytest.fixture
def sample_repository(mocker):
    return mocker.Mock(spec=SampleRepository)


@pytest.fixture
def sample_service(sample_repository):
    return SampleService(sample_repository)


def test_get_sample_details(sample_service, sample_repository):
    sample_repository.get_sample_by_id.return_value = "sample"
    assert sample_service.get_sample_details(1) == "sample"
    sample_repository.get_sample_by_id.assert_called_once_with(1)


def test_add_sample(sample_service, sample_repository):
    sample_repository.create_sample.return_value = "new_sample"
    assert sample_service.add_sample(1, 2, 3, 4, 'Test') == "new_sample"
    sample_repository.create_sample.assert_called_once_with(1, 2, 3, 'Test')


def test_update_sample_info(sample_service, sample_repository):
    sample_repository.update_sample.return_value = "updated_sample"
    assert sample_service.update_sample_info(1, name="New Name") == "updated_sample"
    sample_repository.update_sample.assert_called_once_with(1, name="New Name")


def test_remove_sample(sample_service, sample_repository):
    sample_repository.delete_sample.return_value = True
    assert sample_service.remove_sample(1) == True
    sample_repository.delete_sample.assert_called_once_with(1)
