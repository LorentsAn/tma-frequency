from dataclasses import dataclass


@dataclass
class ProcessingError(ValueError):
    reason: str
