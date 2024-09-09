from typing import List

from tma.core.model.repository import specimen_item_repo, measurement_repo, measured_data_repo, curie_point_repo
from tma.core.service.entrypoit.file import File
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.core.service.services.curie_point_service import CuriePointService
from tma.core.service.services.measured_data_service import MeasuredDataService
from tma.core.service.services.measurement_service import MeasurementService
from tma.core.service.services.specimen_item_service import SpecimenItemService


class SpecialItemRepositoryController:
    """
    Controller class for managing specimen items and their measurements.
    """

    def __init__(self, sample_model):
        self.sample_model = sample_model

    def create_specimen_items(self, specimen_items: List[SpecimenItem]):
        specimen_item_service = SpecimenItemService(specimen_item_repository=specimen_item_repo)
        measurement_service = MeasurementService(measurement_repository=measurement_repo)
        measured_data_service = MeasuredDataService(measured_data_repository=measured_data_repo)

        for item in specimen_items:
            specimen_item_model = specimen_item_service.add_specimen_item_by_model(self.sample_model.sample_id, item)
            if specimen_item_model is None:
                return
            measurement_model = measurement_service.add_measurement_by_model(specimen_item_model.specimen_item_id,
                                                                             item.measurement.value.measurement)
            measured_data_service.add_measured_data_by_model(
                measurement_model.measurement_id,
                specimen_item_model.specimen_item_id,
                item.measurement.value.get_measured_data()
            )

    def get_specimen_item(self, filename):
        specimen_item_service = SpecimenItemService(specimen_item_repository=specimen_item_repo)

        specimen_item = specimen_item_service.get_specimen_item_by_sample_id_and_filename(
            sample_id=self.sample_model.sample_id,
            filename=filename
        )
        return specimen_item

    def get_specimen_items_list(self):
        specimen_item_service = SpecimenItemService(specimen_item_repository=specimen_item_repo)
        measurement_service = MeasurementService(measurement_repository=measurement_repo)
        measurement_data_service = MeasuredDataService(measured_data_repository=measured_data_repo)
        curie_point_service = CuriePointService(curie_point_repository=curie_point_repo)

        specimen_items_model = specimen_item_service.get_specimen_items_by_sample_id(
            sample_id=self.sample_model.sample_id)
        result = []

        for item_model in specimen_items_model:
            file = File({'name': item_model.filename})
            measurement_model = measurement_service.get_measurement_by_specimen_item_id(item_model.specimen_item_id)
            measured_data = measurement_data_service.get_data_by_measurement_id(
                measurement_model.measurement_id)
            curie_points = curie_point_service.get_curie_points_models_by_specimen_item_id(item_model.specimen_item_id)
            result.append(SpecimenItem.create_file_item(
                specimen_item_id=item_model.specimen_item_id,
                filename=item_model.filename,
                uploaded=item_model.uploaded,
                file=file,
                measurement=MeasurementFactory.create_measurement(
                    measurement_model.measurement_id,
                    measurement_model.measurement_type,
                    eval(measurement_model.columns),
                    measured_data
                ),
                is_empty_source_file=item_model.is_empty_source,
                curie_points=curie_points
            ))

        return result
