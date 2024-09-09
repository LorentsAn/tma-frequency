from typing import Tuple, Optional

from tma.multipages.components.graphic_elements.graphic_element import GraphicElement
from tma.multipages.components.graphic_elements.line import Line
from tma.multipages.components.graphic_elements.point import Point
from tma.multipages.components.graphic_elements.style import BaseType, LineType, PointType


class GraphicElementFactory:
    @staticmethod
    def create_graphic_element(style: BaseType, x=None, y=None):
        if isinstance(style, LineType):
            return Line.create_element(x, y, style)
        elif isinstance(style, PointType):
            return Point.create_element(x, y, style)
        else:
            raise ValueError("Unsupported style type")

    @staticmethod
    def get_graphic_element_values(element: GraphicElement) -> Tuple[Optional[list], Optional[list]]:
        if isinstance(element, Line):
            return element.get_values()
        elif isinstance(element, Point):
            return element.get_values()
        else:
            raise ValueError("Unsupported style type")
