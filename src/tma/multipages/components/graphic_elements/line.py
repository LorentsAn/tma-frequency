from abc import ABC
from typing import Optional

from tma.multipages.components.graphic_elements.graphic_element import GraphicElement
from tma.multipages.components.graphic_elements.style import LineType


class Line(GraphicElement, ABC):
    def __init__(self, style: LineType):
        super().__init__(style)

    @staticmethod
    def create_element(x=None, y=None, style=None):
        if x is not None:
            return VerticalLine(x, style)
        elif y is not None:
            return HorizontalLine(y, style)
        else:
            raise ValueError("Line requires either x or y coordinate.")

    def get_values(self):
        pass


class HorizontalLine(Line):
    def __init__(self, y, style):
        super().__init__(style)
        self.y = y

    def draw(self, fig):
        for y in self.y:
            fig.add_hline(y=y, line_dash=self.style.dash, line_color=self.style.color, line_width=self.style.width)
        return fig

    def get_values(self):
        return None, self.y


class VerticalLine(Line):
    def __init__(self, x, style):
        super().__init__(style)
        self.x = x

    def draw(self, fig):
        for x in self.x:
            fig.add_vline(x=x, line_dash=self.style.dash, line_color=self.style.color, line_width=self.style.width)
        return fig

    def get_values(self):
        return self.x, None
