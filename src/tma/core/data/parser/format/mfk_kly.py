from dataclasses import dataclass
from typing import BinaryIO, Optional

from tma.core.data.parser.exceptions.parsing_error import ParsingError
from tma.core.data.parser.model.measured_data import MeasuredData
from tma.core.data.parser.model.parameter import Parameter


@dataclass
class DataTable:
    measured_data: dict[str, list[float]]
    time_data: Optional[list[list[str]]]
    table_columns: list[str]


@dataclass
class TableInformation:
    indexes: dict[str, list[int]]


class CurClwParser:
    def __init__(self):
        self.encoding = 'utf-8'

    def parse(self, source: BinaryIO) -> MeasuredData:
        table_info = self.__skip_titles(source)
        data_table = self.__parse_data_table(source, table_info)
        if len(data_table.measured_data) == 0:
            raise ParsingError('Cannot parse file: Data is empty')

        return MeasuredData(
            columns=list(table_info.indexes.keys()),
            measured_data=data_table.measured_data,
            time_data=data_table.time_data,
        )

    def __skip_titles(self, source: BinaryIO) -> TableInformation:
        line = self.__get_next_line(source)
        indexes = {}
        if line is None:
            raise ParsingError('Cannot parse file')

        for title_idx, title in enumerate(line.split()):
            if "TIME" in title or title == Parameter.EMPTY.value:
                # For now, it was said to ignore the time parameter
                continue
            indexes.update({str(title): [int(title_idx)]})
        return TableInformation(indexes)

    def __parse_data_table(self, source: BinaryIO, table_info: TableInformation) -> DataTable:
        def safe_float_convert(value):
            try:
                return float(value)
            except ValueError:
                return ''

        measured_data = {}
        time_data = None

        while True:
            line = self.__get_next_line(source)
            if line is None:
                return DataTable(measured_data, time_data, list(table_info.indexes.keys()))

            raw_data = line.split()
            for title in table_info.indexes:
                measured_data.setdefault(title, []).extend(
                    [safe_float_convert(raw_data[idx]) if len(raw_data) > idx else '' for idx in
                     table_info.indexes.get(title)])

    def __get_next_line(self, source: BinaryIO) -> Optional[str]:
        while True:
            raw_line = source.readline()
            if not isinstance(raw_line, str):
                raw_line = raw_line.decode(self.encoding, "ignore")

            if not raw_line:
                return None

            stripped_line = raw_line.strip()
            if stripped_line:
                return stripped_line
