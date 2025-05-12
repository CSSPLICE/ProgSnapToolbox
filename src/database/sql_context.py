
from dataclasses import dataclass
from sqlalchemy import Connection, MetaData

from database.sql_table_manager import SQLTableManager

@dataclass
class SQLContext:
    conn: Connection
    table_manager: SQLTableManager