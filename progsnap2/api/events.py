from typing import List, Optional
from pydantic import BaseModel, create_model
from enum import Enum
from datetime import datetime

from progsnap2.spec import datatypes
from progsnap2.spec.spec_definition import EnumType, ProgSnap2Spec

class CodeStateSection(BaseModel):
    """
    A class representing the state of a file at a given time.
    """
    Code: str
    CodeStateSection: str

class CodeState(BaseModel):
    """
    A class representing the state of a whole project at a given time.
    """
    CodeStateID: str
    Sections: List[CodeStateSection]

# # TODO These really need to be auto-generated
# class EventType(str, Enum):
#     SessionStart = "Session.Start"
#     SessionEnd = "Session.End"
#     ProjectOpen = "Project.Open"
#     ProjectClose = "Project.Close"
#     FileCreate = "File.Create"

# # TODO: Figure out a consistent naming scheme here
# class EventInitiatorType(str, Enum):
#     UserDirectAction = "UserDirectAction"
#     UserIndirectAction = "UserIndirectAction"
#     ToolReaction = "ToolReaction"
#     ToolTimedEvent = "ToolTimedEvent"
#     InstructorDirectAction = "InstructorDirectAction"
#     InstructorIndirectAction = "InstructorIndirectAction"
#     TeamMemberDirectAction = "TeamMemberDirectAction"
#     TeamMemberIndirectAction = "TeamMemberIndirectAction"


class MainTableEventBase(BaseModel):
    """
    A class representing an event in the main table.
    """
    TempCodeStateID: str

    # EventType: EventType
    # EventID: str
    # SubjectID: str
    # ToolInstances: str
    # CodeStateID: str

    # Order: Optional[int] = None
    # ClientTimestamp: Optional[datetime] = None
    # # Add more optional columns

    # SessionID: Optional[str] = None
    # ProjectID: Optional[str] = None
    # CodeStateSection: Optional[str] = None
    # EventInitiator: Optional[EventInitiatorType] = None
    # Add more event-specific columns


# TODO: Explore if we can add documentation to fields or enum values
# TODO: Explore if it's worthwhile to add special MainTableEvent classes
# for each event type. This could in theory replace TS CodeGen and would support
# other languages too, but wouldn't have quite as good ergonomics IMO
class DataModelGenerator:
    """
    A class that generates the data model for the events.
    """

    MainTableEvent: type[MainTableEventBase]

    def __init__(self, ps2_spec: ProgSnap2Spec):
        self.ps2_spec = ps2_spec
        self.MainTableEvent = self.generate_main_table_event()

    def generate_event_type_enum_type(self) -> Enum:
        """
        Generate the event type enum type.
        """

        return Enum("EventType", {
            v.name: v.name
            for v in self.ps2_spec.MainTable.event_types
        })

    def create_enum_from_list(self, enum_definition: EnumType):
        """
        Create an enum from a list of enum values.
        """
        return Enum(enum_definition.name, {
            v.name: v.name
            for v in enum_definition.values
        })

    def generate_main_table_event(self) -> MainTableEventBase:
        event_type_enum = self.generate_event_type_enum_type()
        enum_types = self.ps2_spec.EnumTypes
        enum_type_map = {et.name: et for et in enum_types}
        fields = {}
        for col in self.ps2_spec.MainTable.columns:
            if col.name == "EventType":
                type = event_type_enum
            elif col.datatype == "Enum":
                type = self.create_enum_from_list(enum_type_map[col.name])
            else:
                type = datatypes.get_datatype(col.datatype).python_type

            if not col.required:
                type = Optional[type]
                # Use a default value so the field can be omitted
                fields[col.name] = (type, None)
            else:
                fields[col.name] = (type, ...)
        return create_model("MainTableEvent", __base__=MainTableEventBase, **fields)
