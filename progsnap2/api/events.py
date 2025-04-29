from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

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

# TODO These really need to be auto-generated
class EventType(str, Enum):
    SessionStart = "Session.Start"
    SessionEnd = "Session.End"
    ProjectOpen = "Project.Open"
    ProjectClose = "Project.Close"
    FileCreate = "File.Create"

# TODO: Figure out a consistent naming scheme here
class EventInitiatorType(str, Enum):
    UserDirectAction = "UserDirectAction"
    UserIndirectAction = "UserIndirectAction"
    ToolReaction = "ToolReaction"
    ToolTimedEvent = "ToolTimedEvent"
    InstructorDirectAction = "InstructorDirectAction"
    InstructorIndirectAction = "InstructorIndirectAction"
    TeamMemberDirectAction = "TeamMemberDirectAction"
    TeamMemberIndirectAction = "TeamMemberIndirectAction"


class MainTableEvent(BaseModel):
    """
    A class representing an event in the main table.
    """
    EventType: EventType
    EventID: str
    SubjectID: str
    ToolInstances: str
    CodeStateID: str

    Order: Optional[int] = None
    ClientTimestamp: Optional[datetime] = None
    # Add more optional columns

    SessionID: Optional[str] = None
    ProjectID: Optional[str] = None
    CodeStateSection: Optional[str] = None
    EventInitiator: Optional[EventInitiatorType] = None
    # Add more event-specific columns