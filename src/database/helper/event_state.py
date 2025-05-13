from dataclasses import dataclass
from spec.enums import EventTypes

# TODO: Autogenerate with optional fields
@dataclass
class EventState():
    SubjectID: str
    ToolInstances: str