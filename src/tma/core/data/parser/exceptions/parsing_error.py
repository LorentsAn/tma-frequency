from dataclasses import dataclass


@dataclass
class ParsingError(ValueError):
    reason: str
