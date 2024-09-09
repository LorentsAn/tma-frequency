from io import BytesIO
from typing import List, Dict, Any, Union

from tma.core.data.data_analyzer import DataAnalyzer
from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.model.curve import Curve
from tma.core.service.measurement.model.measurement import Measurement
from tma.core.service.measurement.model.measurement_manager import MeasurementManager


class MeasurementFactory:
    _measurement_types_map = {
        'clw': 'clw',
        'cur': 'cur',
        '.clw': 'clw',
        '.cur': 'cur',
    }

    @classmethod
    def create_measurement(cls, measurement_id: int, file_extension: str, columns: List[str],
                           measured_data: Dict[str, Any]) -> 'MeasurementManager':
        measurement_type = cls._get_measurement_type(file_extension)
        measurement = Measurement(measurement_id, measurement_type, columns)

        measurement = cls._add_heating_and_cooling_data(measurement, measured_data)
        return MeasurementManager(measurement)

    @staticmethod
    def _get_measurement_type(file_extension: str) -> str:
        measurement_types_map = MeasurementFactory._measurement_types_map
        if file_extension in measurement_types_map:
            return measurement_types_map[file_extension]
        else:
            allowed_extensions = ', '.join(measurement_types_map.keys())
            raise ValueError(
                f"The extension {file_extension} is not allowed. Allowed extensions: {allowed_extensions}.")

    @staticmethod
    def _add_heating_and_cooling_data(measurement: 'Measurement', measured_data: Dict[str, Any]) -> 'Measurement':
        measurement = MeasurementFactory.add_heating_data(measurement, measured_data)
        measurement = MeasurementFactory.add_cooling_data(measurement, measured_data)
        if measurement.measurement_id == 10001:
            print(measurement.heating_curve[Parameter.TEMP.value].values)
            print(measurement.heating_curve[Parameter.CSUSC.value].values)
        return measurement

    @staticmethod
    def add_heating_data(measurement: Measurement, measured_data: dict):
        for column in measurement.columns:
            if 'increasing' not in measured_data[column].keys():
                return measurement
            temperature = measured_data[Parameter.TEMP.value]['increasing']
            values = measured_data[column]['increasing']
            measurement.add_heating_data(column, temperature, values)
        return measurement

    @staticmethod
    def add_cooling_data(measurement: Measurement, measured_data: dict):
        for column in measurement.columns:
            if 'decreasing' not in measured_data[column].keys():
                return measurement
            temperature = measured_data[Parameter.TEMP.value]['decreasing']
            values = measured_data[column]['decreasing']
            measurement.add_cooling_data(column, temperature, values)

        return measurement

    @staticmethod
    def extract_values(measurement_id: int, file_extension: str,
                       file_uploaded: Dict[str, Union[bytes, str]]) -> 'MeasurementManager':
        data_analyzer = DataAnalyzer(BytesIO(file_uploaded['data']))
        values = data_analyzer.extract_values()
        columns = values.get('columns')
        measured_data = values.get(data_analyzer.measured_data)

        if measured_data and columns:
            return MeasurementFactory.create_measurement(measurement_id, file_extension, columns, measured_data)
        else:
            raise Exception("There is no data")
