from typing import List

from tma.multipages.components.graphic_elements.graphic_element import GraphicElement
from tma.multipages.components.graphic_elements.style import PointType
import plotly.graph_objects as go


class Point(GraphicElement):
    def __init__(self, x, y, style: PointType):
        super().__init__(style)
        self.x = x
        self.y = y

    def draw(self, fig):
        showlegend = True
        for trace in fig.data:
            if trace.name == self.style.name:
                showlegend = False
                break

        fig.add_trace(go.Scatter(
            x=self.x, y=self.y,
            mode='markers',
            marker=dict(
                color=self.style.color,
                size=self.style.size,
                symbol=self.style.symbol,
                line=dict(width=self.style.marker_line_width, color=self.style.marker_line_color)
            ),
            name=(self.style.custom_name if self.style.custom_name != "" else self.style.name),
            showlegend=showlegend
        ))
        return fig

    def get_values(self):
        return self.x, self.y

    @staticmethod
    def create_element(x: List[float], y: List[float], style):
        if x is not None and y is not None:
            return Point(x, y, style)
        else:
            raise ValueError("Point requires both x and y coordinates.")
