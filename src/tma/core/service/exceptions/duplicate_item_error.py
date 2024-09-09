from dataclasses import dataclass


@dataclass
class DuplicateItemError(ValueError):
    reason: str = "Duplicate item already exists in the database"
