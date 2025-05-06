from datetime import datetime
from typing import Optional
from enum import Enum

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
    Timestamp = ("Timestamp", datetime, "Date")
    # Typescript type for Enums should be custom, so we use None
    Enum = ("Enum", str, None, _SHORT_STRING_LENGTH)

    def __init__(self, label: str, python_type: type, typescript_type: str, max_str_length: Optional[int] = None):
        self.label = label
        self.python_type = python_type
        self.typescript_type = typescript_type
        self.max_str_length = max_str_length

    @classmethod
    def from_label(cls, label: str) -> "PS2Datatype":
        for member in cls:
            if member.label == label:
                return member
        raise ValueError(f"Unknown PS2Datatype label: {label}")
