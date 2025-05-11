
from dataclasses import dataclass
from enum import Enum
from api.events import MainTableEventBase
from spec.spec_definition import ProgSnap2Spec, Requirement

class ErrorType(Enum):
    MissingRequiredColumn = "MissingRequiredColumn"
    UnexpectedColumn = "UnexpectedColumn"
    InvalidEventType = "InvalidEventType"

@dataclass
class ValidationError:
    column: str
    type: ErrorType

    def __str__(self):
        if self.type == ErrorType.MissingRequiredColumn:
            return f"Missing required column: {self.column}"
        elif self.type == ErrorType.UnexpectedColumn:
            return f"Unexpected column: {self.column}"
        elif self.type == ErrorType.InvalidEventType:
            return f"Invalid event type: {self.column}"
        else:
            return f"Unknown error: {self.column}"

class EventValidator():

    def __init__(self, spec: ProgSnap2Spec):
        self.spec = spec

    def validate_event(self, event: MainTableEventBase) -> list[ValidationError]:
        """
        Validate the event against the schema.
        """
        errors = []

        spec = self.spec

        # Get all columns that are not None
        # TODO: Could a required column be None? I think not.
        provided_columns = set([
            col for col in event.__dict__.keys() if event.__dict__[col] is not None
        ])

        required_column_names = [
            col.name for col in spec.MainTable.columns
            if col.requirement == Requirement.Required
        ]
        optional_column_names = [
            col.name for col in spec.MainTable.columns
            if col.requirement == Requirement.Optional
        ]

        event_type = spec.MainTable.get_event_type(event.EventType)
        if event_type is None:
            errors.append(ValidationError(column=event.EventType, type=ErrorType.InvalidEventType))
        else:
            required_column_names.extend(
                event_type.required_columns or []
            )
            optional_column_names.extend(
                event_type.optional_columns or []
            )


        # Check if all required fields are present
        for col in required_column_names:
            if col not in provided_columns:
                errors.append(ValidationError(column=col, type=ErrorType.MissingRequiredColumn))

        all_expected_columns = set(required_column_names + optional_column_names)
        for col in provided_columns:
            if col not in all_expected_columns:
                errors.append(ValidationError(column=col, type=ErrorType.UnexpectedColumn))

        return errors