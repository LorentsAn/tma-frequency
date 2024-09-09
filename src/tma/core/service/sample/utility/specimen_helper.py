def extract_point_names(specimen_items: List[SpecimenItem]) -> List[str]:
    point_names = []
    for item in specimen_items:
        for elem in item.displayed_elements.value:
            if isinstance(elem.style, PointType):
                point_names.append(elem.style.name)
    return point_names


def print_point_names(specimen_items: List[SpecimenItem]):
    point_names = extract_point_names(specimen_items)
    print("Point names:", point_names)
