

from typing import Optional
from pydantic import BaseModel, create_model

from ..spec.spec_definition import Metadata

class PS2DataConfig(BaseModel):
    root_path: str

class PS2CSVConfig(PS2DataConfig):
    csv_path: str

class PS2DatabaseConfig(PS2DataConfig):
    sqlalchemy_url: str
    id_str_length: int = 255
    enum_str_length: int = 255
    path_str_length: int = 2048
    echo: bool = False

def create_metadata_values_model(metadata_spec: Metadata) -> type[BaseModel]:
    fields = {}
    for property in metadata_spec.properties:
        fields[property.name] = (property.datatype.python_type, ...)
    return create_model("MetadataValues", **fields)