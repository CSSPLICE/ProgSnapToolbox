from dataclasses import dataclass

import pytest
from api.event_validator import ErrorType, EventValidator
from api.events import DataModelGenerator
from spec.spec_definition import ProgSnap2Spec, load_spec
from spec.enums import EventTypes

@dataclass
class SpecConfig:
    spec: ProgSnap2Spec
    MainTableEvent: type

@pytest.fixture(scope="session")
def config():
    spec_path = "src/spec/progsnap2.yaml"
    spec = load_spec(spec_path)
    data_model_gen = DataModelGenerator(spec)
    MainTableEvent = data_model_gen.MainTableEvent

    return SpecConfig(spec=spec, MainTableEvent=MainTableEvent)

def create_valid_event(config: SpecConfig):
    event = config.MainTableEvent(
        EventType=str(EventTypes.SessionStart),
        EventID="test",
        # TODO: Resolve this :((
        # TempCodeStateID="test",
        CodeStateID="test",
        SubjectID="test",
        ToolInstances="test",
        SessionID="test",
    )
    return event

def test_valid_event(config: SpecConfig):
    # Create an instance of EventValidator
    event_validator = EventValidator(config.spec)

    # Create a sample event
    event = create_valid_event(config)

    # Validate the event
    errors = event_validator.validate_event(event)

    # Check that there are no validation errors
    assert len(errors) == 0, f"Validation errors: {errors}"

def test_invalid_event_type(config):
    # Create an instance of EventValidator
    event_validator = EventValidator(config.spec)

    # Create a sample event
    event = create_valid_event(config)
    event.EventType = "InvalidEventType"  # Set an invalid event type

    errors = event_validator.validate_event(event)

    type_errors = [error for error in errors if error.type == ErrorType.InvalidEventType]
    assert len(type_errors) == 1, f"Expected one InvalidEventType error, got: {type_errors}"

def test_missing_required_column(config):
    # Create an instance of EventValidator
    event_validator = EventValidator(config.spec)

    # Create a sample event
    event = create_valid_event(config)
    event.SessionID = None  # Set a required column to None

    errors = event_validator.validate_event(event)

    type_errors = [error for error in errors if error.type == ErrorType.MissingRequiredColumn]
    assert len(type_errors) == 1, f"Expected one MissingRequiredColumn error, got: {type_errors}"


def test_unexpected_column(config):
    # Create an instance of EventValidator
    event_validator = EventValidator(config.spec)

    # Create a sample event
    event = create_valid_event(config)
    event.EditType = "test"  # Add an unexpected column

    errors = event_validator.validate_event(event)

    type_errors = [error for error in errors if error.type == ErrorType.UnexpectedColumn]
    assert len(type_errors) == 1, f"Expected one UnexpectedColumn error, got: {type_errors}"
