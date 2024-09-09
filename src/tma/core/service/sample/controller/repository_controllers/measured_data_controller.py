import json

from tma.core.model.models.sample import Sample
from tma.core.model.repository import measured_data_repo, measurement_repo
from tma.core.service.services.measured_data_service import MeasuredDataService
from tma.core.service.services.measurement_service import MeasurementService


class MeasuredDataRepositoryController:
    def update_existing_data(self, measured_data, existing_columns, measured_data_model, measured_data_service):
        for data_item in measured_data_model:
            if data_item.column_name in measured_data:
                measured_data_service.update_measured_data_details(
                    measurement_data_id=data_item.measurement_data_id,
                    data=measured_data[data_item.column_name]
                )
                measured_data.pop(data_item.column_name)

    def update_measured_data(self, sample: Sample, filename, measured_data: dict):
        measured_data_service = MeasuredDataService(measured_data_repository=measured_data_repo)
        measurement_service = MeasurementService(measurement_repository=measurement_repo)

        specimen_item = sample.get_specimen_item_by_filename(filename)
        measured_data_model = measured_data_service.get_measured_data_by_specimen_item_id(
            specimen_item.specimen_item_id)

        existing_columns = {data_item.column_name for data_item in measured_data_model}

        if len(existing_columns) != len(measured_data.keys()):
            measurement_service.update_measurement_details(
                measured_data_model.first().measurement_id, columns=json.dumps(list(measured_data.keys())))

        all_measured_data = measured_data.copy()
        self.update_existing_data(all_measured_data, existing_columns, measured_data_model, measured_data_service)
        self.add_new_columns_with_measured_data(
            measurement_id=measured_data_model.first().measurement_id,
            measured_data=all_measured_data,
            existing_columns=existing_columns,
            specimen_item=specimen_item,
            measured_data_service=measured_data_service
        )

    def add_new_columns_with_measured_data(
        self, measurement_id: int, measured_data, existing_columns, specimen_item, measured_data_service):

        for column_name, data in measured_data.items():
            if column_name not in existing_columns:
                prepared_data = json.dumps({key: value.tolist() for key, value in data.items()})
                measured_data_service.add_measured_data(
                    measurement_id=measurement_id,
                    specimen_item_id=specimen_item.specimen_item_id,
                    column_name=column_name,
                    data=prepared_data
                )
