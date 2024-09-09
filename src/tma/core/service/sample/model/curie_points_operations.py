from typing import Dict, List, Tuple

from tma.core.service.measurement.model.curie.cuie_point import CuriePoint
from tma.core.service.sample.model.specimen_item import SpecimenItem


class CuriePointOperations:
    @staticmethod
    def add_curie_point(specimen_item: SpecimenItem, curie_point: CuriePoint):
        specimen_item.curie_points.append(curie_point)

    @staticmethod
    def delete_curie_point(specimen_item: SpecimenItem, curie_point: CuriePoint):
        specimen_item.curie_points.remove(curie_point)

    @staticmethod
    def get_sorted_curie_points(specimen_item: SpecimenItem) -> Dict[int, List[Tuple[float, float]]]:
        curie_dict = {}
        for curie_point in specimen_item.curie_points:
            if curie_point.id_plot_select not in curie_dict:
                curie_dict[curie_point.id_plot_select] = []
            curie_dict[curie_point.id_plot_select].append(
                (curie_point.temperature_value, curie_point.magnetization_value))
        return curie_dict

    @staticmethod
    def get_curie_points(specimen_item: SpecimenItem, y_column) -> Dict[str, List[float]]:
        curie_dict = {'x': [], 'y': []}
        for curie_point in specimen_item.curie_points:
            if curie_point.column_name == y_column:
                curie_dict['x'].append(curie_point.temperature_value)
                curie_dict['y'].append(curie_point.magnetization_value)
        return curie_dict
