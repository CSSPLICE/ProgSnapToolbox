from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PS2Datatype:
    name: str
    python_type: type
    typescript_type: str
    max_str_length: Optional[int] = None

__short_string_length = 255
__path_string_length = 2048

__datatypes = [
    PS2Datatype("ID", str, "string", __short_string_length),
    PS2Datatype("URL", str, "string", __path_string_length),
    PS2Datatype("RelativePath", str, "string", __path_string_length),
    PS2Datatype("SourceLocation", str, "string", __path_string_length),
    PS2Datatype("String", str, "string"), # Not max length
    PS2Datatype("Integer", int, "number"),
    PS2Datatype("Real", float, "number"),
    PS2Datatype("Boolean", bool, "boolean"),
    PS2Datatype("Timestamp", datetime, "Date")
]

__datatype_map = { dt.name.lower(): dt for dt in __datatypes }

def is_datatype(name: str) -> bool:
    """
    Check if the given name is a recognized datatype.
    :param name: The name of the datatype.
    :return: True if the name is a recognized datatype, False otherwise.
    """
    return name.lower() in __datatype_map

def get_datatype(name: str) -> PS2Datatype:
    """
    Get the PS2Datatype object for a given name.
    :param name: The name of the datatype.
    :return: The PS2Datatype object.
    """
    if not is_datatype(name):
        raise ValueError(f"Unrecognized datatype: {name}")
    return __datatype_map[name.lower()]


