# server/main.py
from enum import Enum
from fastapi import FastAPI
from typing import List, Type

from progsnap2.api.events import CodeState, DataModelGenerator
from progsnap2.spec.spec_definition import load_spec

spec = load_spec("progsnap2/spec/progsnap2.yaml")

data_model_gen = DataModelGenerator(spec)
MainTableEvent = data_model_gen.MainTableEvent

app = FastAPI()

@app.post("/events", operation_id="addEvents")
def add_events(events: List[MainTableEvent]):
    pass

@app.post("/code_states", operation_id="addCodeStates")
def add_code_states(code_states: List[CodeState]):
    pass

@app.post("/events_with_code_states", operation_id="addEventsWithCodeStates")
def add_events_with_code_states(events: List[MainTableEvent], code_states: List[CodeState]):
    """
    Add events and code states to the database at the same time to ensure consistency.
    """
    pass