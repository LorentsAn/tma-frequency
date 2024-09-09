from dataclasses import dataclass


@dataclass
class ParameterError(ValueError):
    reason: str
