
import os
import pytest
import sqlite3

from database.writer.db_writer_factory import SQLWriterFactory
from database.writer.sql_writer import SQLWriter
from .conftest import cleanup_temp_dir
from .test_codestate_writers import CodestateGenerator
from .test_event_validator import create_valid_event
from spec.enums import MainTableColumns as MTC, EventTypes

def test_sqlite_writer_init(sqlite_writer_factory, sqlite_config):
    cleanup_temp_dir()
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
    cleanup_temp_dir()
    with sqlite_writer_factory.create() as writer:
        writer.initialize_database()

        codestate_gen = CodestateGenerator()
        codestate = codestate_gen.codestate1

        # TODO: Do we support dicts or the actual model?
        event = create_valid_event(config)
        event_data = event.model_dump()
        temp_codestate_id = "abc123"
        event_data[MTC.CodeStateID] = temp_codestate_id
        codestates_dict = {temp_codestate_id: codestate}

        writer.add_events_with_codestates([event_data], codestates_dict)

        # TODO: Do actualy checks (e.g. the CodeStateID is correct - it's not right now)