from typing import Dict, List, Optional
from pydantic import BaseModel, computed_field, field_validator, model_validator
from enum import Enum
import yaml

from spec.datatypes import PS2Datatype


class EnumValue(BaseModel):
    name: str
    description: str = None


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
    description: str = None

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
    description: str = None
    required_columns: List[str] = None
    optional_columns: List[str] = None

    def is_column_specific_to_event(self, column_name: str) -> bool:
        return (self.required_columns and column_name in self.required_columns) or \
               (self.optional_columns and column_name in self.optional_columns)

    def is_column_required(self, column_name: str) -> bool:
        return self.required_columns and column_name in self.required_columns


class MainTable(BaseModel):
    columns: List[Column]
    event_types: List[EventType]

    @computed_field
    def _event_type_map(self) -> Dict[str, EventType]:
        return {event_type.name: event_type for event_type in self.event_types}

    def get_event_type(self, event_type_name: str) -> Optional[EventType]:
        return self._event_type_map.get(event_type_name)

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



class LinkTableSpec(BaseModel):
    name: str
    description: str = None
    id_column_names: List[str]
    additional_columns: List[Column]


class ProgSnap2Spec(BaseModel):
    Metadata: Metadata
    EnumTypes: List[EnumType]
    MainTable: MainTable
    LinkTables: List[LinkTableSpec]

    def version(self) -> str:
        return self.Metadata.Version

    @model_validator(mode="after")
    def validate_link_table_id_cols(cls, values):
        # Check if all ID columns in link tables are present in the main table
        id_columns = {col.name for col in values.MainTable.columns}
        for link_table in values.LinkTables:
            for id_col in link_table.id_column_names:
                if id_col not in id_columns:
                    raise ValueError(f"ID column '{id_col}' in LinkTable '{link_table.name}' not defined in MainTable")
        return values

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ProgSnap2Spec":
        with open(yaml_path, "r", encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return cls(**data)
