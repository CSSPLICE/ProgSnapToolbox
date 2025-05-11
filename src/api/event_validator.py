
from dataclasses import dataclass
from api.events import MainTableEventBase
from spec.spec_definition import ProgSnap2Spec, Requirement


@dataclass
class ValidationError:
    message: str
    column: str

class EventValidator():

    def __init__(self, spec: ProgSnap2Spec):
        self.spec = spec
        self.events

def validate_event(event: MainTableEventBase, spec: ProgSnap2Spec) -> list[ValidationError]:
    """
    Validate the event against the schema.
    """
    errors = []

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
        errors.append(ValidationError(f"Invalid event type: {event.EventType}", "EventType"))
    else:
        required_column_names.extend(
            event_type.required_columns or []
        )
        optional_column_names.extend(
            event_type.optional_columns or []
        )


    # Check if all required fields are present
    for col in required_column_names:
        if col not in event:
            errors.append(ValidationError(f"Missing required column: {col}", col))

    all_expected_columns = set(required_column_names + optional_column_names)
    for col in event:
        if col not in all_expected_columns:
            errors.append(ValidationError(f"Unexpected column: {col}", col))

    return errors