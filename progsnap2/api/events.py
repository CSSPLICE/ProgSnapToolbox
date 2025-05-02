from typing import List, Literal, Optional, Union
from pydantic import BaseModel, create_model
from enum import Enum
from datetime import datetime

from progsnap2.spec import datatypes
from progsnap2.spec.spec_definition import EnumType, ProgSnap2Spec, Requirement

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
    main_event_subclasses: List[type[MainTableEventBase]] = []
    AnyMainTableEvent: type[MainTableEventBase]

    __enum_map = {}

    def __init__(self, ps2_spec: ProgSnap2Spec):
        self.ps2_spec = ps2_spec
        self.MainTableEvent = self.generate_main_table_event()
        self.main_event_subclasses = self.generate_main_table_event_subclasses()
        self.AnyMainTableEvent = Union[tuple([self.MainTableEvent] + self.main_event_subclasses)]

    def get_event_type_enum_type(self) -> Enum:
        """
        Generate the event type enum type.
        """
        event_type_name = "EventType"

        stored = self.__enum_map.get(event_type_name)

        if stored is None:
            stored = Enum(event_type_name, {
                v.name: v.name
                for v in self.ps2_spec.MainTable.event_types
            })
            self.__enum_map[event_type_name] = stored

        return stored

    def create_enum_from_list(self, enum_definition: EnumType):
        """
        Create an enum from a list of enum values.
        """

        stored = self.__enum_map.get(enum_definition.name)

        if stored is None:
            stored = Enum(enum_definition.name, {
                v.name: v.name
                for v in enum_definition.values
            })
            self.__enum_map[enum_definition.name] = stored

        return stored

    # TODO: Test adding back in type
    def generate_main_table_event(self, event_type = None) -> type[MainTableEventBase]:
        event_type_enum = self.get_event_type_enum_type()
        enum_types = self.ps2_spec.EnumTypes
        enum_type_map = {et.name: et for et in enum_types}
        fields = {}
        for col in self.ps2_spec.MainTable.columns:
            event_type_enum_value = None
            if col.name == "EventType":
                # Doesn't really work with the TY CodeGen - turns into a string...
                # if event_type:
                #     # If this is for a specific event type, it gets a special literal
                #     # type that can only hold the correct Enum value
                #     type = Literal[event_type_enum_value]
                # else:
                type = event_type_enum
            elif col.datatype == "Enum":
                type = self.create_enum_from_list(enum_type_map[col.name])
            else:
                type = datatypes.get_datatype(col.datatype).python_type

            if col.requirement == Requirement.EventSpecific and event_type:
                if not event_type.is_column_present(col.name):
                    continue

            required = col.requirement == Requirement.Required
            if event_type and event_type.is_column_required(col.name):
                required = True
            if not required:
                type = Optional[type]
                # Use a default value so the field can be omitted
                fields[col.name] = (type, None)
            elif event_type and col.name == "EventType":
                # If we have an event_type, we need to force the EventType property
                # to only have that specific EventType
                event_type_enum_value = next(e for e in event_type_enum if e.value == event_type.name)
                fields[col.name] = (type, event_type_enum_value)
            else:
                fields[col.name] = (type, ...)

        name = "Event" + event_type.name if event_type else "MainTableEvent"
        name = name.replace(".", "")
        return create_model(name, __base__=MainTableEventBase, **fields)

    def generate_main_table_event_subclasses(self) -> List[type[MainTableEventBase]]:
        """
        Generate subclasses of MainTableEvent for each event type.
        """
        subclasses = []
        for event_type in self.ps2_spec.MainTable.event_types:
            subclass = self.generate_main_table_event(event_type)
            subclasses.append(subclass)
        return subclasses
