from dataclasses import dataclass

import pytest
from api.events import DataModelGenerator
from spec.spec_definition import ProgSnap2Spec

@dataclass
class SpecConfig:
    spec: ProgSnap2Spec
    MainTableEvent: type

@pytest.fixture(scope="session")
def config():
    spec_path = "src/spec/progsnap2.yaml"
    spec = ProgSnap2Spec.from_yaml(spec_path)
    data_model_gen = DataModelGenerator(spec)
    MainTableEvent = data_model_gen.MainTableEvent

    return SpecConfig(spec=spec, MainTableEvent=MainTableEvent)