
from database.config import PS2DatabaseConfig
from spec.enums import CodeStateRepresentation
from spec.spec_definition import ProgSnap2Spec

from datetime import datetime
from sqlalchemy import Connection, Index, MetaData, Table, Column as SQLColumn, Integer, String, Float, Enum as SQLEnum, UniqueConstraint
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

class SQLTableManager:
    def __init__(self, spec: ProgSnap2Spec, metadata_values):
        self.metadata_values = metadata_values
        self.spec = spec
        self._sql_metadata: MetaData = None
        self.main_table: Table = None
        self.link_tables: dict[str, Table] = {}
        self.metadata_table: Table = None
        self.codestates_table: Table = None

        self._define_tables()

    def has_codestates_table(self) -> bool:
        """
        Check if the codestates table is defined.
        """
        return self.codestates_table is not None

    def _define_tables(self):
        self._sql_metadata = metadata = MetaData()
        spec = self.spec

        # --- Metadata Table ---
        self.metadata_table = Table(
            "Metadata", metadata,
            SQLColumn("Property", String(255), nullable=False),
            # Value has various datatypes, so we'll store all al strings
            SQLColumn("Value", String(2048), nullable=False)
        )

        # --- Main Table ---
        main_columns = []

        for col in spec.MainTable.columns:
            main_columns.append(define_column(col))

        self.main_table = Table(
            "MainTable", metadata,
            *main_columns
        )

        id_datatype = map_datatype(PS2Datatype.ID)
        path_datatype = map_datatype(PS2Datatype.RelativePath)

        for link_table in spec.LinkTables:
            columns = []
            # ID columns
            for id_col in link_table.id_column_names:
                columns.append(SQLColumn(id_col, id_datatype, nullable=False))
            # Additional columns
            for add_col in link_table.additional_columns:
                columns.append(define_column(add_col))

            tbl = Table(
                link_table.name, metadata,
                *columns
            )
            self.link_tables[link_table.name] = tbl

        # TODO: Replace hard-coded values with enum names
        if self.metadata_values.CodeStateRepresentation == CodeStateRepresentation.Table:

            self.codestates_table = Table(
                "CodeStates", metadata,
                SQLColumn("CodeStateID", id_datatype),
                SQLColumn("CodeStateSection", path_datatype, nullable=True),
                SQLColumn("Code", Text(), nullable=False),
                UniqueConstraint("CodeStateID", "CodeStateSection", name="uq_codestate_id_section"),
                Index("ix_codestate_id", "CodeStateID"),
            )

    def create_tables(self, conn: Connection):
        self._sql_metadata.create_all(conn)

    def update_tables(self, conn: Connection):
        """
        Update the tables in the database to match the current spec.
        Learns the current structure from the connection, and then
        iterates through each table defined in our spec-defined metadata
        and adds any missing columns. Should not delete tables or columns.
        """

        # Get the current structure of the database
        current_metadata = MetaData(bind=conn)
        current_metadata.reflect()

        # Iterate through each table defined in our spec-defined metadata
        for table_name, table in self.link_tables.items():
            # Check if the table exists in the current metadata
            if table_name in current_metadata.tables:
                # If it exists, check for missing columns
                existing_table = current_metadata.tables[table_name]
                self._update_table_columns(conn, existing_table, table)
            else:
                # If the table doesn't exist, create it
                table.create(conn)

    def _update_table_columns(self, conn: Connection, current_table: Table, new_table: Table):
        """
        Update the columns of a table in the database to match the new table.
        """
        for column in new_table.columns:
            if column.name not in current_table.columns:
                # If the column is missing, add it to the existing table
                column.create(current_table)
            if column.type != current_table.columns[column.name].type:
                # If the column type is different, alter the column
                raise NotImplementedError(
                    f"""Column type change not implemented for {column.name} in {current_table.name}.
                    Please update the database manually."""
                )

    def update_metadata_values(self, conn: Connection):
        """
        Update the metadata values in the database.
        """
        # Clear existing metadata values
        conn.execute(self.metadata_table.delete())

        metadata_dict = self.metadata_values.model_dump()
        print(f"Updating metadata values: {len(metadata_dict)}")

        # Insert new metadata values
        for property, value in metadata_dict.items():
            print(f"Inserting metadata: {property} = {value}")
            conn.execute(self.metadata_table.insert().values(Property=property, Value=value))

        conn.commit()
