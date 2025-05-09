
from dataclasses import dataclass
from sqlalchemy import Connection, MetaData

@dataclass
class SQLContext:
    conn: Connection
    metadata: MetaData