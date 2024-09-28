from enum import Enum


class LogState(Enum):
    START = "start"
    END = "end"


class LogType(Enum):
    BACKGROUND = "background"


class LogLevels(Enum):
    """
    Custom log levels for Informed in addition to the standard ones.
    """

    DIAGNOSTIC = 27  # Log level between severity of success and warning
