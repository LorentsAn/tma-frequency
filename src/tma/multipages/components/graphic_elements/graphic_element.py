from abc import ABC, abstractmethod

from tma.multipages.components.graphic_elements.style import BaseType


class GraphicElement(ABC):
    def __init__(self, style: BaseType):
        self.style = style

    @abstractmethod
    def draw(self, fig):
        pass

    @staticmethod
    def create_element(x, y, style):
        pass
