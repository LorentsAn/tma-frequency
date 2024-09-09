from dataclasses import dataclass, field


@dataclass
class PointType:
    name: str
    color: str
    size: int
    symbol: str


class PointTypes:
    MaxSecondDerivative = PointType('Max Second Derivative', '#22559c', 8, 'circle')
    InflectionPoint = PointType('Inflection Point', '#900c3f', 8, 'square')
    CurrentUserPoint = PointType('Current User Point', '#fa9856', 8, 'diamond')
    CurrentUserPointDerivative = PointType('Current User Derivative Point', '#fa9856', 8, 'diamond')
    StoredCuriePoints = PointType('Stored Curie Points', '#2eb872', 8, 'x')

    @staticmethod
    def get_style(point_type: PointType):
        return {'color': point_type.color, 'size': point_type.size, 'symbol': point_type.symbol}

    @classmethod
    def get_style_by_name(cls, point_name: str):
        for point_type in cls.__dict__.values():
            if isinstance(point_type, PointType) and point_type.name == point_name:
                return {'color': point_type.color, 'size': point_type.size, 'symbol': point_type.symbol}
        raise ValueError(f"Point with name '{point_name}' not found.")
