from tma.core.service.sample.model.specimen_item import SpecimenItem


class FurnaceOperations:
    @staticmethod
    def get_empty_furnace_value(specimen_item: SpecimenItem) -> str:
        if specimen_item.empty_furnace_source.value:
            return specimen_item.empty_furnace_source.value.get_value()
        return "Empty Furnace not init"

    @staticmethod
    def is_furnace_file(specimen_item: SpecimenItem) -> bool:
        return FurnaceOperations.__get_empty_furnace_type(specimen_item) == "file"

    @staticmethod
    def is_furnace_constant(specimen_item: SpecimenItem) -> bool:
        return FurnaceOperations.__get_empty_furnace_type(specimen_item) == "constant"

    @staticmethod
    def __get_empty_furnace_type(specimen_item: SpecimenItem) -> str:
        if specimen_item.empty_furnace_source.value:
            return specimen_item.empty_furnace_source.value.type
        return "Тип не задан"
