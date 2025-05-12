
import os
import pytest
import sqlite3

from database.writer.db_writer_factory import SQLWriterFactory
from database.writer.sql_writer import SQLWriter
from .conftest import cleanup_temp_dir

@pytest.fixture(scope="session")
def sqlite_writer_factory(ps2_spec, sqlite_config):
    return SQLWriterFactory(ps2_spec, sqlite_config)

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
