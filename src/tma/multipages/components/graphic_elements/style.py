import inspect


class BaseType:
    def __init__(self, name: str, color='black'):
        self.name = name
        self.color = color


class LineType(BaseType):
    def __init__(self, name: str, color: str, width: int, dash: str):
        super().__init__(name, color)
        self.width = width
        self.dash = dash


class LineTypes:
    BaseLine = LineType('Axis line', 'rgb(224, 224, 223)', 1, 'dash')
    MaxSecondDerivativeLine = LineType('Max Second Derivative Line', '#E69F00', 3, 'dot')
    InflectionPointLine = LineType('Inflection', '#009E73', 3, 'dot')
    StoredCurieLine = LineType('Stored Curie Line', '#CC79A7', 3, 'dash')
    MaxFirstDerivative = LineType('Max First Derivative', '#56B4E9', 3, 'dash')
    OutlineLine = LineType('Outline Point', '#009E73', 3, 'dash')


class PointType(BaseType):
    def __init__(self, name: str, color: str, size: int, symbol: str, marker_line_width: int = 0,
                 marker_line_color: str = "#000000", custom_name: str = ""):
        super().__init__(name, color)
        self.size = size
        self.symbol = symbol
        self.marker_line_width = marker_line_width
        self.marker_line_color = marker_line_color
        self.custom_name = custom_name

    def update(self, color: str = None, size: int = None, symbol: str = None, marker_line_width: int = None,
               marker_line_color: str = None, custom_name: str = None):
        if color is not None:
            self.color = color
        if size is not None:
            self.size = size
        if symbol is not None:
            self.symbol = symbol
        if marker_line_width is not None:
            self.marker_line_width = marker_line_width
        if marker_line_color is not None:
            self.marker_line_color = marker_line_color
        if custom_name is not None:
            self.custom_name = custom_name


class PointTypes:
    MaxSecondDerivative = PointType('Maximum values of the Second Derivative', '#E69F00', 8, 'circle')
    InflectionPoint = PointType('Inflection Point', '#009E73', 8, 'square')
    CurrentUserPoint = PointType('Current User Point', '#fa9856', 8, 'diamond')
    CurrentUserPointDerivative = PointType('Current User Derivative Point', '#fa9856', 8, 'diamond')
    StoredCuriePoints = PointType('Stored Curie Points', '#2269c4', 8, 'diamond', 0)
    MaxFirstDerivative = PointType('Maximum values of the First Derivative', '#56B4E9', 8, 'circle')
    OutlinePoint = PointType('Outline Point', '#009E73', 8, 'star-diamond')


class PointFactory:
    def __init__(self):
        self.point_types = self._initialize_point_types()

    def _initialize_point_types(self):
        point_types = {
            attr.name: attr for name, attr in inspect.getmembers(PointTypes) if isinstance(attr, PointType)
        }
        return point_types

    def create_point_type(self, key: str, name: str, color: str, size: int, symbol: str, marker_line_width: int = 0,
                          marker_line_color: str = "#000000", custom_name: str = ""):
        point_type = PointType(name, color, size, symbol, marker_line_width, marker_line_color, custom_name)
        self.point_types[key] = point_type
        return point_type

    def get_point_type(self, key: str) -> PointType:
        return self.point_types.get(key)

    def update_point_type(self, key: str, color: str = None, size: int = None, symbol: str = None,
                          marker_line_width: int = None, marker_line_color: str = None, custom_name: str = None):
        point_type = self.get_point_type(key)
        if point_type:
            point_type.update(color, size, symbol, marker_line_width, marker_line_color, custom_name)
