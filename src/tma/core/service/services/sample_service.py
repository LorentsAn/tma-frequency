from tma.core.model.models.sample import Sample as SampleModel
from tma.core.model.repository.sample_repository import SampleRepository
from tma.core.service.sample.model.sample import Sample


class SampleService:
    def __init__(self, sample_repository: SampleRepository):
        self.sample_repository = sample_repository

    def get_sample_details(self, sample_id: int):
        return self.sample_repository.get_sample_by_id(sample_id)

    def get_sample_by_model(self, sample: SampleModel) -> Sample:
        return Sample(sample.sample_id, sample.x_column, sample.y_column, sample.name)

    def add_sample(self, user_id: int, x_column: int, y_column: int, selected_file_index: int, name: str = ''):
        return self.sample_repository.create_sample(user_id, x_column, y_column, selected_file_index, name)

    def update_sample_info(self, sample_id: int, **kwargs):
        return self.sample_repository.update_sample(sample_id, **kwargs)

    def remove_sample(self, sample_id: int):
        return self.sample_repository.delete_sample(sample_id)
