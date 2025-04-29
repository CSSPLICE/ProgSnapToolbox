from typing import Dict
from sqlalchemy import create_engine, MetaData, Table, Column as SQLColumn, Integer, String, Float, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import DATETIME
from pydantic import BaseModel
from ..spec.spec_definition import ProgSnap2Spec
import yaml


from sqlalchemy import Text, String, Integer, Float, Boolean
from sqlalchemy.dialects.sqlite import DATETIME

def map_datatype(datatype: str):
    """
    Maps ProgSnap2 datatype strings to SQLAlchemy column types.
    Expand this as needed for more precise typing or databases.
    """
    # Normalize
    dtype = datatype.strip().lower()

    # TODO: Should probably be configurable in a db config
    short_string = String(255)
    path_string = String(2048)

    mapping = {
        # ID and Text types
        "id": short_string,
        "enum": short_string,
        "url": path_string,
        "relativepath": path_string,
        "sourcelocation": path_string,
        "string": Text,

        # Numbers
        "integer": Integer,
        "real": Float,
        "boolean": Boolean,

        # Time
        "timestamp": DATETIME,
        "timezone": short_string,
    }

    if dtype not in mapping:
        raise ValueError(f"Unrecognized datatype: {datatype}")

    return mapping[dtype]



# --- Step 1: Load your schema spec from YAML ---

def load_schema(yaml_file: str) -> ProgSnap2Spec:
    with open(yaml_file, "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return ProgSnap2Spec(**data)


# --- Step 2: Create tables from SchemaSpec ---

def define_column(column_spec):
    """
    Define a SQLAlchemy column based on the column spec.
    """
    col_type = map_datatype(column_spec.datatype)
    kwargs = {
        'nullable': not column_spec.required,
        'doc': column_spec.description
    }
    return SQLColumn(column_spec.name, col_type, **kwargs)


def create_tables_from_schema(schema: ProgSnap2Spec, engine):
    metadata = MetaData()

    # --- Metadata Table ---
    metadata_table = Table(
        "Metadata", metadata,
        SQLColumn("Property", String(255), nullable=False),
        # Value has various datatypes, so we'll store all al strings
        SQLColumn("Value", String(2048), nullable=False)
    )

    # --- Main Table ---
    main_columns = []

    for col in schema.MainTable.columns:
        main_columns.append(define_column(col))

    main_table = Table(
        "MainTable", metadata,
        *main_columns
    )

    # --- Link Tables ---
    link_tables = []

    for link_table in schema.LinkTables:
        columns = []
        # ID columns
        for id_col in link_table.id_column_names:
            columns.append(SQLColumn(id_col, map_datatype('ID'), nullable=False))
        # Additional columns
        for add_col in link_table.additional_columns:
            columns.append(define_column(add_col))

        tbl = Table(
            link_table.name, metadata,
            *columns
        )
        link_tables.append(tbl)

    # --- Create all tables ---
    metadata.create_all(engine)

    print("Tables created successfully.")

