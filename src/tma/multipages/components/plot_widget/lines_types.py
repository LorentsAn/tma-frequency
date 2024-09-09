from dataclasses import dataclass, field


@dataclass
class LineType:
    name: str
    color: str
    width: int
    dash: str


class LinesTypes:
    BaseLine = LineType('Axis line', 'rgb(115,115,115)', 2, 'dash')

    MaxSecondDerivativeLine = LineType('Max Second Derivative', '#22559c', 4, 'dot')
    InflectionPointLine = LineType('Inflection', '#900c3f', 4, 'dot')
    StoredCuriePointLine = LineType('Stored Curie Points', '#2eb872', 4, 'dash')

    @classmethod
    def get_style_by_name(cls, line_name: str):
        for line_type in cls.__dict__.values():
            if isinstance(line_type, LineType) and line_type.name == line_name:
                return {'name': line_type.name,
                        'line': {'color': line_type.color, 'width': line_type.width, 'dash': line_type.dash}}
        raise ValueError(f"Point with name '{line_name}' not found.")
