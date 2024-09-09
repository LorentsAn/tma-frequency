from typing import List

from tma.multipages.components.graphic_elements.graphic_element import GraphicElement


class DisplayedElementsManager:
    @staticmethod
    def filter_displayed_elements(displayed_elements, config) -> List[GraphicElement]:
        if not config.show_points:
            return []

        all_elements = []
        for element in displayed_elements:
            if isinstance(element, GraphicElement):
                all_elements.append(element)
        return all_elements
