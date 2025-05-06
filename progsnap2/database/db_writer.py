
from abc import ABC, abstractmethod
from progsnap2.database.config import PS2CSVConfig, PS2DatabaseConfig, PS2DataConfig

from sqlalchemy import create_engine
from progsnap2.database.config import PS2DatabaseConfig, PS2DataConfig
from progsnap2.database.sql_writer import SQLWriter

class DBWriterFactor(ABC):
    def __init__(self, db_config: PS2DataConfig):
        self.db_config = db_config

    @abstractmethod
    def __call__(self):
        pass

class SQLWriterFactory(DBWriterFactor):
    def __init__(self, db_config):
        super().__init__(db_config)
        self.engine = create_engine(db_config.sqlalchemy_url, echo=db_config.echo)

    def __call__(self):
        try:
            conn = self.engine.connect()
            yield SQLWriter(conn)
        finally:
            conn.close()


def create_db_writer_factory(db_config: PS2DataConfig):
    if isinstance(db_config, PS2DatabaseConfig):
        return SQLWriterFactory(db_config)
    elif isinstance(db_config, PS2CSVConfig):
        # Implement CSV writer factory if needed
        pass

class DBWriter(ABC):
    pass

def create_db_writer(db_config: PS2DataConfig, metadata, engine):
    codestate_representation = metadata.CodeStateRepresentation
    if isinstance(db_config, PS2DatabaseConfig):
        codestate_writer = create_codestate_table_writer(db_config, codestate_representation)
    elif isinstance(db_config, PS2CSVConfig):
        pass
    else:
        raise ValueError("Invalid database configuration")

def create_codestate_table_writer(db_config: PS2DataConfig, code_state_representation):
    code_state_representation = code_state_representation.lower()
    if code_state_representation == 'table':
        pass
    elif code_state_representation == 'directory':
        pass
    elif code_state_representation == 'git':
        pass
    else:
        raise ValueError(f"Invalid code state representation: {code_state_representation}")