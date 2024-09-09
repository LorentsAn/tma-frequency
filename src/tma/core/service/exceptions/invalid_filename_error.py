from dataclasses import dataclass


@dataclass
class InvalidFilenameError(ValueError):
    reason: str
