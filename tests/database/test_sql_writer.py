
import os
import pytest
import sqlite3

from database.writer.db_writer import LogResult
from database.writer.db_writer_factory import SQLWriterFactory
from database.writer.sql_writer import SQLWriter
from spec.codestate import CodeStateEntry
from .conftest import cleanup_temp_dir
from .test_codestate_writers import CodestateGenerator
from .test_event_validator import create_valid_event
from spec.enums import MainTableColumns as MTC, EventType

def test_sqlite_writer_init(sqlite_writer_factory, sqlite_config):
    with sqlite_writer_factory.create() as writer:
        writer.initialize_database()

    db_path = sqlite_writer_factory.db_config.sqlalchemy_url.split(":///")[-1]
    assert os.path.exists(db_path), f"Database file {db_path} should exist after initialization"

    n_metadata_fields = len(sqlite_config.metadata.model_dump())

    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT property, value FROM Metadata;")
    metadata = cursor.fetchall()
    assert len(metadata) == n_metadata_fields, f"Metadata table should have {n_metadata_fields} field, not {len(metadata)}"

def test_sqlite_writer_add_events(sqlite_writer_factory, sqlite_config, config):
    with sqlite_writer_factory.create() as writer:
        writer.initialize_database()

        codestate_gen = CodestateGenerator()
        codestate = codestate_gen.codestate1

        event = create_valid_event(config)
        temp_codestate_id = "abc123"
        event[MTC.CodeStateID] = temp_codestate_id
        codestates_dict = {temp_codestate_id: codestate}

        writer.add_events_with_codestates([event], codestates_dict)

        # TODO: Do actualy checks (e.g. the CodeStateID is correct - it's not right now)


def test_add_context_git(sqlite_writer_factory, config):
    # Create a non-contextual codestate
    codestate = CodeStateEntry.from_code("test code!!")

    event = create_valid_event(config)
    temp_codestate_id = "abc123"
    event[MTC.CodeStateID] = temp_codestate_id
    event[MTC.ProjectID] = "test_project"
    codestates_dict = {temp_codestate_id: codestate}

    result = LogResult(True)

    with sqlite_writer_factory.create() as writer:
        writer._contextualize_codestates([event], codestates_dict, result)

    assert result.success, "Contextualization should succeed"
    assert result.warnings == [], "There should be no warnings"

    new_codestate = codestates_dict[temp_codestate_id]
    assert new_codestate != codestate, "Codestate should now be contextualized"
    assert new_codestate.grouping_id == event[MTC.SubjectID], "Grouping ID should match the event's SubjectID"
    assert new_codestate.ProjectID == event[MTC.ProjectID], "Project ID should match the event's ProjectID"


# TODO: Test warnings and errors if codestates are lacking