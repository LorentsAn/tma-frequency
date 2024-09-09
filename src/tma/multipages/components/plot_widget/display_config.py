from tma.multipages.components.graphic_elements.style import LineType, PointType


class DisplayConfig:
    def __init__(self, show_lines=False, show_points=False, element_visibility=None):
        self.show_lines = show_lines
        self.show_points = show_points
        self.element_visibility = element_visibility if element_visibility is not None else {}

    def is_displayed(self, element_type: LineType):
        if isinstance(element_type, LineType) and not self.show_lines:
            return False
        if isinstance(element_type, PointType) and not self.show_points:
            return False
        return self.element_visibility.get(element_type.name, False)
