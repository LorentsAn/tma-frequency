import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from tma.core.data.parser.exceptions.invalid_file_error import InvalidFileError


@dataclass
class Values:
    """
    Represents a container for X and Y values.

    Attributes:
        value_x (Optional[list[str]]): List of X values.
        value_y (Optional[list[str]]): List of Y values.
    """
    value_x: Optional[list[str]] = None
    value_y: Optional[list[str]] = None

    def __init__(self, values):
        """
        Initialize the Values instance with a tuple of X and Y values.

        Args:
            values (tuple(list[float], list[float])): A tuple containing X and Y values.

        Example:
            values_instance = Values((['1.0, 2.0, 3.0'], ['4.0, 5.0, 6.0']))
        """
        self.value_x = values[0]
        self.value_y = values[1]


class AllowedExtension(Enum):
    CUR = '.cur'
    CLW = '.clw'


@dataclass
class File:
    """
    Represents an abstraction over the physical file.
    Parses data, checks its correctness, and verifies the file extension.

    Attributes:
        file_name (str): Name of the file.
        file_extension (AllowedExtension): Extension of the file.

    Methods:
        __init__(file): Initializes the File instance with a file.
        is_valid_file_extension(file_extension): Checks if the file extension is valid.

    Raises:
        InvalidFileError: If the file extension does not match the allowed ones.
    """
    file_name: str
    file_extension: AllowedExtension

    def __init__(self, file):
        """
        Initialize the File instance with a file path.

        Parameters:
            file (FileInfo): The file.

        Raises:
            InvalidFileExtensionError: If the file extension does not match the allowed ones.
            ValueError: If there is no valid data in the file.
        """
        self.file_name = file['name']
        _, file_extension = os.path.splitext(self.file_name)

        self.is_valid_file_extension(file_extension)
        self.file_extension = AllowedExtension(file_extension.lower())

    @staticmethod
    def is_valid_file_extension(file_extension):
        """
        Checks if the file extension is valid.

        Parameters:
            file_extension (str): The file extension.

        Raises:
            InvalidFileError: If the file extension does not match the allowed ones.
        """
        if file_extension.lower() in [ext.value for ext in AllowedExtension]:
            return True
        raise InvalidFileError(
            f"The extension {file_extension} is not allowed. Allowed extensions: {', '.join(list(AllowedExtension))}.")
