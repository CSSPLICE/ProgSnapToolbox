from datetime import datetime
from sqlalchemy import MetaData, Table, Column as SQLColumn, Integer, String, Float, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import DATETIME

from spec.datatypes import PS2Datatype
from spec.spec_definition import ProgSnap2Spec, Property, Requirement, Column as SpecColumn


from sqlalchemy import Text, String, Integer, Float, Boolean
from sqlalchemy.dialects.sqlite import DATETIME

def map_datatype(datatype: PS2Datatype):
    """
    Maps ProgSnap2 datatype strings to SQLAlchemy column types.
    Expand this as needed for more precise typing or databases.
    """

    if datatype.max_str_length is not None:
        # If the datatype has a max string length, use that
        return String(datatype.max_str_length)

    if datatype.python_type == str:
        # If the datatype is a string but has no max length, use Text
        return Text

    # Convert python type to SQL type
    type_map = {
        int: Integer,
        float: Float,
        bool: Boolean,
        datetime: DATETIME,
    }
    if datatype.python_type not in type_map:
        raise ValueError(f"Unconvertible datatype: {datatype.python_type}")

    return type_map.get(datatype.python_type)



def define_column(column_spec: SpecColumn):
    """
    Define a SQLAlchemy column based on the column spec.
    """
    required = column_spec.requirement == Requirement.Required
    col_type = map_datatype(column_spec.datatype)
    kwargs = {
        'nullable': not required,
        'doc': column_spec.description
    }
    return SQLColumn(column_spec.name, col_type, **kwargs)


# May make sense to create these tables each time,
# and only create them when needed, since SQLAlchemy uses
# this construct a lot
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
            columns.append(SQLColumn(id_col, map_datatype(PS2Datatype.ID), nullable=False))
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

