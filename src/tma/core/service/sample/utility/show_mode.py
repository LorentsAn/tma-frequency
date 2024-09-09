from enum import Enum


class ShowMode(Enum):
    """Enum for different show modes in a plot."""

    LINES = 'lines'
    LINES_AND_MARKERS = 'lines+markers'
    MARKERS = 'markers'
    DEFAULT_MODE = LINES

    @classmethod
    def get_enum_values(cls):
        """Return a list of all enum values."""
        return [member.value for member in cls]
