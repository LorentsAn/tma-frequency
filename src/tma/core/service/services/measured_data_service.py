import json

import numpy as np

from tma.core.model.repository.measurement_data_repository import MeasuredDataRepository


class MeasuredDataService:
    def __init__(self, measured_data_repository: MeasuredDataRepository):
        self.measured_data_repository = measured_data_repository

    def get_measured_data_by_specimen_item_id(self, specimen_item_id: int):
        return self.measured_data_repository.get_measured_data(specimen_item_id=specimen_item_id)

    def get_data_by_specimen_item_id_column_name(self, specimen_item_id: int, column_name: str):
        return self.measured_data_repository.get_measured_data(specimen_item_id=specimen_item_id,
                                                               column_name=column_name).first()

    def get_data_by_measurement_id(self, measurement_id: int):
        return self.get_data_by_filter(measurement_id=measurement_id)

    def get_data_by_specimen_item_id(self, specimen_item_id: int):
        return self.get_data_by_filter(specimen_item_id=specimen_item_id)

    def get_data_by_filter(self, **filter_criteria):
        measured_data_items = self.measured_data_repository.get_measured_data(**filter_criteria)

        result = {}
        for data_item_model in measured_data_items:
            data_converted = {key: np.array(value) for key, value in json.loads(data_item_model.data).items()}
            result.update({data_item_model.column_name: data_converted})

        return result

    def add_measured_data(self, measurement_id: int, specimen_item_id: int, column_name: str, data):
        return self.measured_data_repository.create_measured_data(measurement_id, specimen_item_id, column_name, data)

    def add_measured_data_by_model(self, measurement_id: int, specimen_item_id: int, measured_data: dict):
        results = []
        for column, value in measured_data.items():
            data_converted = {key: value.tolist() for key, value in value.items()}
            results.append(self.add_measured_data(measurement_id, specimen_item_id, column, json.dumps(data_converted)))
        return results

    def update_measured_data_details(self, measurement_data_id: int, data=None, **kwargs):
        if data is not None:
            data_converted = {key: value.tolist() for key, value in data.items()}
            kwargs['data'] = json.dumps(data_converted)

        return self.measured_data_repository.update_measured_data(measurement_data_id, **kwargs)

    def remove_measured_data_by_measurement_id(self, measurement_id: int):
        return self.measured_data_repository.delete_measured_data_by_measurement_id(measurement_id)
