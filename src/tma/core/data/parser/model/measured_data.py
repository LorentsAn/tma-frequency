from dataclasses import dataclass
from typing import Optional, List, Dict

from tma.core.data.parser.exceptions.processing_error import ProcessingError
from tma.core.data.parser.model.parameter import Parameter


@dataclass
class MeasuredData:
    columns: List[str]
    measured_data: Dict[str, List[float]]
    time_data: Optional[List[List[str]]]

    def get_columns(self):
        return self.columns

    def get_parameters_from_columns(self) -> List[Parameter]:
        parameters = []
        for column in self.columns:
            param = Parameter.get_parameter(column)
            if param != '':
                parameters.append(param)
        return parameters

    def get_measurement_data(self, parameter: Parameter) -> List[float]:
        if parameter.value not in self.columns:
            raise ProcessingError(f'No {parameter.name} measurements')

        return self.measured_data.get(parameter.value)

    def get_temp_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.TEMP)

    def get_nsusc_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.NSUSC)

    def get_tsusc_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.TSUSC)

    def get_csusc_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.CSUSC)

    def get_bulks_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.BSUSC)

    def get_ferrt_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.FERRT)

    def get_ferrb_data(self) -> List[float]:
        return self.get_measurement_data(Parameter.FERRB)
