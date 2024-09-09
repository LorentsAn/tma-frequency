from typing import BinaryIO

from tma.core.data.parser.format.mfk_kly import CurClwParser
from tma.core.data.parser.model.measured_data import MeasuredData


class Parser:
    def __init__(self,
                 cur_clw_parser: CurClwParser):
        self.mfk_kly_clw = cur_clw_parser

    def parse(self, source: BinaryIO) -> MeasuredData:
        return self.mfk_kly_clw.parse(source)
