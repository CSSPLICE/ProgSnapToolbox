from typing import List, Optional
from pydantic import BaseModel


class Metadata(BaseModel):
    Version: str
    IsEventOrderingConsistent: bool
    # Add any other metadata fields you need
    # e.g. Description: Optional[str] = None


class EnumValue(BaseModel):
    name: str
    description: Optional[str] = None


class EnumType(BaseModel):
    name: str
    values: List[EnumValue]


class Column(BaseModel):
    name: str
    required: Optional[bool] = False
    datatype: str  # you could make this an Enum if you want stricter validation
    description: Optional[str] = None


class EventType(BaseModel):
    name: str
    description: Optional[str] = None
    required_columns: List[str]


class MainTable(BaseModel):
    columns: List[Column]
    event_types: List[EventType]


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
