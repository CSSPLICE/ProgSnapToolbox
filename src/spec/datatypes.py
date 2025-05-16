from datetime import datetime
from typing import Optional
from enum import Enum

TIMESTAMP_FORMAT_WITH_TIMEZONE    = "%Y-%m-%dT%H:%M:%S.%f%z"
TIMESTAMP_FORMAT_WITHOUT_TIMEZONE = "%Y-%m-%dT%H:%M:%S.%f"

def get_current_timestamp(time = None) -> str:
    """
    Get the current timestamp in the appropriate format.
    """
    if not time:
        time = datetime.now()
    return time.astimezone().strftime(TIMESTAMP_FORMAT_WITH_TIMEZONE)

def parse_timestamp(timestamp: str) -> datetime:
    """
    Parse a timestamp string. Throws an exception if the format is not valid.
    """
    for format in (TIMESTAMP_FORMAT_WITH_TIMEZONE, TIMESTAMP_FORMAT_WITHOUT_TIMEZONE):
        try:
            return datetime.strptime(timestamp, format)
        except ValueError:
            continue
    raise ValueError(f"Invalid timestamp format: {timestamp}. \
                     Expected formats: \
                     {TIMESTAMP_FORMAT_WITH_TIMEZONE}, {TIMESTAMP_FORMAT_WITHOUT_TIMEZONE}")

def timestamp_has_timezone(timestamp: str) -> bool:
    """
    Check if a timestamp string has a timezone.
    """
    try:
        datetime.strptime(timestamp, TIMESTAMP_FORMAT_WITH_TIMEZONE)
        return True
    except ValueError:
        return False


# TODO: Use config instead!
_SHORT_STRING_LENGTH = 255
_PATH_STRING_LENGTH = 2048
class PS2Datatype(Enum):

    ID = ("ID", str, "string", _SHORT_STRING_LENGTH)
    URL = ("URL", str, "string", _PATH_STRING_LENGTH)
    RelativePath = ("RelativePath", str, "string", _PATH_STRING_LENGTH)
    SourceLocation = ("SourceLocation", str, "string", _PATH_STRING_LENGTH)
    String = ("String", str, "string") # Not max length
    Integer = ("Integer", int, "number")
    Real = ("Real", float, "number")
    Boolean = ("Boolean", bool, "boolean")
    Timestamp = ("Timestamp", str, "string", _SHORT_STRING_LENGTH)
    # Typescript type for Enums should be custom, so we use None
    Enum = ("Enum", str, None, _SHORT_STRING_LENGTH)

    def __init__(self, label: str, python_type: type, typescript_type: str, max_str_length: Optional[int] = None):
        self.label = label
        self.python_type = python_type
        self.typescript_type = typescript_type
        self.max_str_length = max_str_length

    def validate_value(self, value) -> None:
        """
        Validate the datatype.
        """
        if not isinstance(value, self.python_type):
            raise ValueError(f"Expected {self.python_type}, got {type(value)}")
        if self == PS2Datatype.Timestamp:
            # Throws an exception if the format is not valid
            parse_timestamp(value)
            return True
        elif self == PS2Datatype.String:
            if self.max_str_length is not None and len(value) > self.max_str_length:
                raise ValueError(f"String length exceeds {self.max_str_length} characters")

    @classmethod
    def from_label(cls, label: str) -> "PS2Datatype":
        for member in cls:
            if member.label == label:
                return member
        raise ValueError(f"Unknown PS2Datatype label: {label}")
