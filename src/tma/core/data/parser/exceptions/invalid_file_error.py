from dataclasses import dataclass


@dataclass
class InvalidFileError(ValueError):
    reason: str
