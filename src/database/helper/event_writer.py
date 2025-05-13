
from dataclasses import dataclass, fields
import uuid
from database.codestate.codestate_writer import ContextualCodeStateEntry
from database.helper.event_state import EventState
from database.writer.sql_writer import SQLWriter
from spec.enums import EventTypes, MainTableColumns as Cols

CODESTATE = "CodeState"

class EventWriterBase():
    # TODO: Change to DBWriter
    def __init__(self, writer: SQLWriter, event_state: EventState):
        self.writer = writer
        self.event_state = event_state

    def update_event_state(self, event_state: dict[str, str]) -> None:
        """
        Update the event state with the new event state.
        """
        for key, value in event_state.items():
            if hasattr(self.event_state, key):
                setattr(self.event_state, key, value)
            else:
                raise ValueError(f"Invalid event state key: {key}")

    def generate_uuid(self) -> str:
        """
        Generate a new UUID.
        """
        # Could make configurable (e.g. sequential IDs)
        return str(uuid.uuid4())

    def write_event(self, event_type: EventTypes, column_map: dict[str, any]) -> None:
        """
        Write the event to the database.
        """

        for field in fields(self.event_state):
            # Column map can override event state
            if field.name not in column_map:
                column_map[field.name] = getattr(self.event_state, field.name)
            else:
                # TODO: Should probably add this to validation errors somewhere...
                print("Warning: Column map overrides event state for field:", field.name)

        column_map[Cols.EventType] = event_type

        if Cols.EventID not in column_map:
            column_map[Cols.EventID] = self.generate_uuid()

        codestates = {}
        if CODESTATE in column_map:
            if Cols.CodeStateID in column_map:
                raise ValueError(f"Cannot have both {CODESTATE} and {Cols.CodeStateID} in fields.")

            code = column_map[CODESTATE]
            # TODO: Maybe need validation somewhere depending on codestatewriter...
            codestate = ContextualCodeStateEntry.from_code(code, column_map.get(Cols.SubjectID), column_map.get(Cols.ProjectID))
            codestates["temp"] = codestate
            column_map[Cols.CodeStateID] = "temp"

            del column_map[CODESTATE]

        self.writer.add_events_with_codestates([column_map], codestates)


