import json

from tma.core.model.repository.measurement_repository import MeasurementRepository
from tma.core.service.measurement.model.measurement import Measurement


class MeasurementService:
    def __init__(self, measurement_repository: MeasurementRepository):
        self.measurement_repository = measurement_repository

    def get_measurement(self, measurement_id: int):
        return self.measurement_repository.get_measurement_by_id(measurement_id)

    def get_measurement_by_specimen_item_id(self, specimen_item_id: int):
        return self.measurement_repository.get_measurement_by_specimen_item_id(specimen_item_id)

    def add_measurement(self, specimen_item_id: int, measurement_type: int, columns):
        return self.measurement_repository.create_measurement(specimen_item_id, measurement_type, columns)

    def add_measurement_by_model(self, specimen_item_id: int, measurement: Measurement):
        return self.measurement_repository.create_measurement(specimen_item_id, measurement.measurement_type,
                                                              json.dumps(measurement.columns))

    def update_measurement_details(self, measurement_id: int, **kwargs):
        return self.measurement_repository.update_measurement(measurement_id, **kwargs)

    def remove_measurement(self, measurement_id: int):
        return self.measurement_repository.delete_measurement(measurement_id)
