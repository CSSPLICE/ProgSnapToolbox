# server/main.py
from enum import Enum
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Type

from fastapi.responses import PlainTextResponse

from api.config import PS2APIConfig
from database.writer.sql_writer import SQLWriter
from spec.events import TempCodeState, DataModelGenerator
from database.writer.db_writer import DBWriter
from database.writer.db_writer_factory import DBWriterFactory, SQLWriterFactory
from spec.spec_definition import ProgSnap2Spec
from spec.gen.gen_client import generate_ts_methods

spec = ProgSnap2Spec.from_yaml("spec/progsnap2.yaml")

data_model_gen = DataModelGenerator(spec)
MainTableEvent = data_model_gen.MainTableEvent
AnyAdditionalColumns = data_model_gen.AnyAdditionalColumns


api_config = PS2APIConfig.from_yaml("api/api_config.yaml", spec)

db_writer_factory: SQLWriterFactory = DBWriterFactory.create_factory(spec, api_config.database_config)

with db_writer_factory.create() as writer:
    # Create the tables in the database
    writer.initialize_database()

# For use in Depends
def create_writer():
    with db_writer_factory.create() as writer:
        yield writer



app = FastAPI()

cors_config = api_config.cors_config

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.allow_origins,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
)

@app.get("/placeholder")
def get_additional_column_types(additionalColumns: AnyAdditionalColumns):
    """
    Placeholder endpoint to get the additional column types.
    """
    pass


@app.post("/events", operation_id="addEvents")
def add_events(events: List[MainTableEvent], writer: SQLWriter = Depends(create_writer)):
    events = [event.dict() for event in events]
    writer.add_events_with_codestates(events, {})

@app.post("/code_states", operation_id="addCodeStates")
def add_code_states(code_states: List[TempCodeState]):
    pass

@app.post("/events_with_code_states", operation_id="addEventsWithCodeStates")
def add_events_with_code_states(events: List[MainTableEvent], code_states: List[TempCodeState]):
    """
    Add events and code states to the database at the same time to ensure consistency.
    """
    pass

@app.get("/generate_api_helper", operation_id="generateAPIHelper", response_class=PlainTextResponse)
def generate_api_helper() -> str:
    return generate_ts_methods(spec)