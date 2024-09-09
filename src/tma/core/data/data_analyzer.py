from typing import BinaryIO, Optional, Tuple, Dict, List

import numpy as np

from tma.core.data.parser.exceptions.parsing_error import ParsingError
from tma.core.data.parser.format.mfk_kly import CurClwParser
from tma.core.data.parser.model.measured_data import MeasuredData
from tma.core.data.parser.parser import Parser
from tma.core.data.parser.exceptions.invalid_file_error import InvalidFileError


class DataAnalyzer:
    """
    The DataAnalyzer class is designed to analyze data from a list of specified file paths.

    Attributes:
        file_path (BinaryIO): A file path containing data to be analyzed.
        data (MeasuredData): An instance to store MeasuredData objects parsed from the input file.
        parser (Parser): An instance of the Parser class to parse data from files.

    Methods:
        __init__(self, file_path: BinaryIO): Initializes the DataAnalyzer with a file path.
        __load_data(self): Private method to load and parse data from files.
        extract_values(self): Extracts and organizes data for analysis.
        classify_trends(self, x, y): Classifies trends in the data.
    """

    increasing = 'increasing'
    decreasing = 'decreasing'
    measured_data = 'measured_data'

    def __init__(self, file_path: BinaryIO):
        """
        Initializes the DataAnalyzer with a file path.

        Args:
            file_path (BinaryIO): A file path containing data to be analyzed.
        """
        self.file_path = file_path
        self.data: Optional[MeasuredData] = None
        self.parser = Parser(cur_clw_parser=CurClwParser())

    def __load_data(self):
        """
        Private method to load and parse data from files.

        Raises:
            ParsingError: If an error occurs while parsing the data.
        """
        try:
            self.data = self.parser.parse(self.file_path)
        except ParsingError as e:
            print(f"Error loading data: {str(e)}")

    def extract_values(self):
        """
        Extracts and organizes data for analysis.

        Returns:
            dict: A dictionary containing columns and values for temperature and nsusc data.
                - 'columns' (list): List of column names.
                - 'increasing' (dict): Dictionary containing increasing trend values.
                    - 'values' (tuple): Tuple containing sorted temperature and nsusc data for increasing trend.
                - 'decreasing' (dict): Dictionary containing decreasing trend values.
                    - 'values' (tuple): Tuple containing sorted temperature and nsusc data for decreasing trend.
                - 'values' (tuple): Tuple containing sorted temperature and nsusc data for general case.

        Raises:
            InvalidFileError: If there is no data in the file.
        """
        self.__load_data()

        if not self.data:
            raise InvalidFileError("There is no data in files.")

        all_temp = self.data.get_temp_data()
        parameters_data = {}
        parameters_names = []
        for parameter in self.data.get_parameters_from_columns():
            # if "TIME" in parameter.value:
            #     continue
            parameter_name = parameter.value
            parameter_data = self.data.get_measurement_data(parameter)
            if parameter_data:
                trends = DataAnalyzer.classify_trends((all_temp, parameter_data))
                parameters_data[parameter_name] = trends
                parameters_names.append(parameter_name)
        return {'columns': parameters_names, 'measured_data': parameters_data}

    @staticmethod
    def classify_trends(data: Tuple[List[float], List[float]]) -> Dict[str, np.ndarray]:
        """
        Classifies trends in the data.

        Args:
            data (Tuple[np.ndarray, np.ndarray]): Tuple containing X and Y data.

        Returns:
            dict: Dictionary containing trend values.
                - 'increasing' (tuple): Tuple containing sorted X and Y data for increasing trend.
                - 'decreasing' (tuple): Tuple containing sorted X and Y data for decreasing trend.
                - 'values' (tuple): Tuple containing sorted X and Y data for general case.
        """
        array_x, array_y = data
        array_x = np.array(array_x)
        array_y = np.array(array_y)
        index_max = np.argmax(array_x)

        if len(array_x[:index_max]) > 1 and len(array_y[index_max:]) > 1:
            return {
                'increasing': array_y[:index_max],
                'decreasing': array_y[index_max:]
            }
        return {'increasing': array_y}
        # return {'values': array_y}
