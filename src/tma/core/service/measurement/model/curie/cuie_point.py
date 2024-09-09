from typing import List


class CuriePoint:
    def __init__(self, id_curie_point: int, id_plot_select: int, column_name: str, temperature_value: float,
                 magnetization_value: float):
        self.id_curie_point = id_curie_point
        self.id_plot_select = id_plot_select
        self.column_name: str = column_name
        self.temperature_value: float = temperature_value
        self.magnetization_value: float = magnetization_value

    @staticmethod
    def find_by_values(curie_points: List['CuriePoint'], temperature_value: float,
                       magnetization_value: float) -> 'CuriePoint':
        for point in curie_points:
            if point.temperature_value == temperature_value and point.magnetization_value == magnetization_value:
                return point
        return None
