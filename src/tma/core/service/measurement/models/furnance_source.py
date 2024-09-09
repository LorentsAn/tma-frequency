from abc import ABC, abstractmethod


class FurnaceSource(ABC):
    @abstractmethod
    def get_value(self) -> str:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass


class ConstantFurnaceValue(FurnaceSource):
    def __init__(self, value: str):
        self.value = value

    def get_value(self) -> str:
        return self.value

    @property
    def type(self) -> str:
        return "constant"


class FileFurnaceValue(FurnaceSource):
    def __init__(self, filename: str):
        self.filename = filename

    def get_value(self) -> str:
        return self.filename

    @property
    def type(self) -> str:
        return "file"
