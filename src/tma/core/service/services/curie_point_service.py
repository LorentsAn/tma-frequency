from typing import List

from tma.core.model.repository.curie_point_repository import CuriePointRepository
from tma.core.service.measurement.model.curie.cuie_point import CuriePoint


class CuriePointService:
    def __init__(self, curie_point_repository: CuriePointRepository):
        self.curie_point_repository = curie_point_repository

    def get_curie_points_by_specimen_item_id(self, specimen_item_id: int):
        return self.curie_point_repository.get_curie_point(specimen_item_id=specimen_item_id)

    def get_curie_points_models_by_specimen_item_id(self, specimen_item_id: int) -> List[CuriePoint]:
        points = self.curie_point_repository.get_curie_point(specimen_item_id=specimen_item_id)
        result = []
        for point in points:
            result.append(CuriePoint(
                id_curie_point=point.curie_point_id,
                id_plot_select=point.id_plot_selected,
                column_name=point.column_name,
                temperature_value=point.temperature_value,
                magnetization_value=point.magnetization_value,
            ))
        return result

    def add_curie_point(
        self,
        specimen_item_id: int,
        column_name: str,
        id_plot_select: int,
        temperature_value: float,
        magnetization_value: float
    ):
        return self.curie_point_repository.add_curie_point(
            specimen_item_id=specimen_item_id,
            column_name=column_name,
            id_plot_selected=id_plot_select,
            temperature_value=temperature_value,
            magnetization_value=magnetization_value,
        )

    def delete_curie_point(self, curie_point_id: int):
        self.curie_point_repository.delete_curie_point(curie_point_id)
