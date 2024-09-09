from tma.core.model.repository import curie_point_repo
from tma.core.service.services.curie_point_service import CuriePointService
from tma.core.service.measurement.model.curie.cuie_point import CuriePoint


class CuriePointsRepositoryController:
    def __init__(self, specimen_item):
        self.specimen_item = specimen_item

    def add_curie_point(self, filename: str, column_name: str, id_plot_select: int, temperature_value: float,
                        magnetization_value: float):
        curie_point_service = CuriePointService(curie_point_repository=curie_point_repo)

        curie_point_model = curie_point_service.add_curie_point(
            specimen_item_id=self.specimen_item.specimen_item_id,
            id_plot_select=id_plot_select,
            column_name=column_name,
            temperature_value=temperature_value,
            magnetization_value=magnetization_value,
        )
        return CuriePoint(
            id_curie_point=curie_point_model.curie_point_id,
            id_plot_select=curie_point_model.id_plot_selected,
            column_name=curie_point_model.column_name,
            temperature_value=curie_point_model.temperature_value,
            magnetization_value=curie_point_model.magnetization_value,
        )

    def delete_curie_point(self, curie_point: CuriePoint):
        curie_point_service = CuriePointService(curie_point_repository=curie_point_repo)
        curie_point_service.delete_curie_point(curie_point_id=curie_point.id_curie_point)
