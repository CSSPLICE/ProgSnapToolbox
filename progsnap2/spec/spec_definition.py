from typing import List, Optional
from pydantic import BaseModel, field_validator, model_validator
from enum import Enum
import yaml

from progsnap2.spec.datatypes import PS2Datatype


class EnumValue(BaseModel):
    name: str
    description: Optional[str] = None


class EnumType(BaseModel):
    name: str
    values: List[EnumValue]

class Requirement(Enum):
    Required = "Required"
    Optional = "Optional"
    EventSpecific = "EventSpecific"

class Property(BaseModel):
    name: str
    datatype: PS2Datatype
    description: Optional[str] = None

    @field_validator("datatype", mode="before")
    def parse_datatype(cls, v):
        if isinstance(v, str):
            return PS2Datatype.from_label(v)
        return v

class Column(Property):
    requirement: Requirement

class Metadata(BaseModel):
    properties: List[Column]


class EventType(BaseModel):
    name: str
    description: Optional[str] = None
    required_columns: Optional[List[str]] = None
    optional_columns: Optional[List[str]] = None

    def is_column_specific_to_event(self, column_name: str) -> bool:
        return (self.required_columns and column_name in self.required_columns) or \
               (self.optional_columns and column_name in self.optional_columns)

    def is_column_required(self, column_name: str) -> bool:
        return self.required_columns and column_name in self.required_columns


class MainTable(BaseModel):
    columns: List[Column]
    event_types: List[EventType]

    @model_validator(mode="after")
    def validate_event_types(cls, values):
        # Check if all required columns are present in the main table
        required_columns = {col.name for col in values.columns}
        for event_type in values.event_types:
            named_columns = set()
            if event_type.required_columns:
                named_columns.update(event_type.required_columns)
            if event_type.optional_columns:
                named_columns.update(event_type.optional_columns)
            missing_columns = named_columns - required_columns
            if missing_columns:
                raise ValueError(f"Named columns in '{event_type.name}' not defined in MainTable: {missing_columns}")
        return values



class LinkTable(BaseModel):
    name: str
    id_column_names: List[str]
    additional_columns: List[Column]


class ProgSnap2Spec(BaseModel):
    Metadata: Metadata
    EnumTypes: List[EnumType]
    MainTable: MainTable
    LinkTables: List[LinkTable]

    def version(self) -> str:
        return self.Metadata.Version

def load_spec(yaml_file: str) -> ProgSnap2Spec:
    with open(yaml_file, "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return ProgSnap2Spec(**data)