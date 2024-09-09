from typing import List
import solara as sol

from tma.core.service.entrypoit.file import File
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.measurement.model.measurement_manager import MeasurementManager
from tma.core.service.measurement.model.curie.cuie_point import CuriePoint
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.core.service.sample.utility.show_mode import ShowMode


class SpecimenItemFactory:
    @staticmethod
    def create_file_item(
        specimen_item_id: int,
        filename: str,
        uploaded: bool,
        file: File,
        measurement: MeasurementManager,
        is_empty_source_file: bool,
        curie_points: List[CuriePoint] = []
    ) -> SpecimenItem:
        return SpecimenItem(
            specimen_item_id=specimen_item_id,
            filename=sol.reactive(filename),
            uploaded=uploaded,
            file=file,
            show_mode=sol.Reactive(ShowMode.DEFAULT_MODE.value),
            measurement=sol.reactive(measurement),
            is_empty_source_file=is_empty_source_file,
            curie_points=curie_points
        )

    @staticmethod
    def load_from_file(input_file, uploaded, is_empty_source_file=False) -> SpecimenItem:
        file = File(input_file)
        measurement = MeasurementFactory.extract_values(1000, file.file_extension.value, input_file)
        return SpecimenItem(
            specimen_item_id=10000,
            filename=sol.reactive(input_file['name']),
            uploaded=uploaded,
            file=file,
            show_mode=sol.Reactive(ShowMode.DEFAULT_MODE.value),
            measurement=sol.reactive(measurement),
            is_empty_source_file=is_empty_source_file,
            curie_points=[]
        )
