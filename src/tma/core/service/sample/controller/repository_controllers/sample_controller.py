from tma.core.model.repository import user_repo, sample_repo, specimen_item_repo, measurement_repo, measured_data_repo
from tma.core.service.sample.controller.repository_controllers.specimen_item_controller import \
    SpecialItemRepositoryController
from tma.core.service.sample.model.sample import Sample
from tma.core.service.services.measured_data_service import MeasuredDataService
from tma.core.service.services.measurement_service import MeasurementService
from tma.core.service.services.sample_service import SampleService
from tma.core.service.services.specimen_item_service import SpecimenItemService
from tma.core.model.models.sample import Sample as Sample_model


class SampleRepositoryController:
    """
    Controller class for managing samples and specimen items.
    """

    def __init__(self, session_id):
        user = user_repo.get_user_by_session_id(session_id)

        sample_model = sample_repo.get_sample_by_user_id(user.user_id)
        if sample_model is None:
            sample = Sample()
            sample_model = sample_repo.create_sample(
                user_id=user.user_id,
                x_column=sample.x_column.value,
                y_column=sample.y_column.value,
                name=sample.name.value,
                selected_file_index=sample.selected_file_index
            )
        self.sample_model: Sample_model = sample_model

    def is_sample_created(self):
        specimen_item = specimen_item_repo.get_first_by_sample_id(sample_id=self.sample_model.sample_id)

        return specimen_item is not None

    def get_sample(self):
        sample_service = SampleService(sample_repository=sample_repo)
        sample = sample_service.get_sample_by_model(self.sample_model)
        specimen_repository_controller = SpecialItemRepositoryController(self.sample_model)
        sample.add_specimen_items(specimen_repository_controller.get_specimen_items_list())
        return sample

    def delete_sample(self, sample: Sample):
        sample_service = SampleService(sample_repository=sample_repo)
        specimen_item_service = SpecimenItemService(specimen_item_repository=specimen_item_repo)
        measurement_service = MeasurementService(measurement_repository=measurement_repo)
        measurement_data_service = MeasuredDataService(measured_data_repository=measured_data_repo)

        for item in sample.specimen_items:
            measurement_id = item.measurement.value.get_measurement_id()

            measurement_data_service.remove_measured_data_by_measurement_id(measurement_id)
            measurement_service.remove_measurement(measurement_id)

        specimen_item_service.remove_specimen_items_by_sample_id(self.sample_model.sample_id)
        sample_service.remove_sample(self.sample_model.sample_id)

    def update_sample(self, **kwargs):
        sample_service = SampleService(sample_repository=sample_repo)
        sample_service.update_sample_info(self.sample_model.sample_id, **kwargs)
        self.sample_model = sample_service.get_sample_details(self.sample_model.sample_id)
