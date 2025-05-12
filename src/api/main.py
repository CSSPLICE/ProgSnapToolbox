# server/main.py
from enum import Enum
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Type

from api.config import load_api_config
from api.events import TempCodeState, DataModelGenerator
from database.writer.db_writer import DBWriter
from database.writer.db_writer_factory import DBWriterFactory
from spec.spec_definition import ProgSnap2Spec

spec = ProgSnap2Spec.from_yaml("progsnap2/spec/progsnap2.yaml")

data_model_gen = DataModelGenerator(spec)
MainTableEvent = data_model_gen.MainTableEvent
AnyAdditionalColumns = data_model_gen.AnyAdditionalColumns


api_config = load_api_config("progsnap2/api/api_config.yaml", spec)

db_writer_factory = DBWriterFactory.create_db_writer_factory(api_config)

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
def add_events(events: List[MainTableEvent], writer: DBWriter = Depends(db_writer_factory)):
    pass

@app.post("/code_states", operation_id="addCodeStates")
def add_code_states(code_states: List[TempCodeState]):
    pass

@app.post("/events_with_code_states", operation_id="addEventsWithCodeStates")
def add_events_with_code_states(events: List[MainTableEvent], code_states: List[TempCodeState]):
    """
    Add events and code states to the database at the same time to ensure consistency.
    """
    pass