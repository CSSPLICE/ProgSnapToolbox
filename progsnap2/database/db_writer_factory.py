
from abc import ABC, abstractmethod
from progsnap2.api.config import PS2APIConfigBase
from progsnap2.database.codestate_writer import TableCodeStateWriter
from progsnap2.database.config import PS2CSVConfig, PS2DatabaseConfig, PS2DataConfig

from sqlalchemy import Connection, create_engine
from progsnap2.database.config import PS2DatabaseConfig, PS2DataConfig
from progsnap2.database.sql_writer import SQLContext, SQLWriter
from progsnap2.spec.enums import CodeStateRepresentation

class DBWriterFactor(ABC):
    def __init__(self, db_config: PS2DataConfig, metadata):
        self.db_config = db_config
        self.metadata = metadata

    @abstractmethod
    def __call__(self):
        pass

    def create_codestate_writer(self, context: SQLContext):
        # TODO: These aren't actually the same enum right now... so need to str convert
        code_state_representation = str(self.metadata.CodeStateRepresentation)
        if code_state_representation == CodeStateRepresentation.Table:
            return TableCodeStateWriter(context)
        elif code_state_representation == CodeStateRepresentation.Directory:
            raise NotImplementedError("Directory code state representation not implemented yet")
        elif code_state_representation == CodeStateRepresentation.Git:
            raise NotImplementedError("Git code state representation not implemented yet")
        else:
            raise ValueError(f"Invalid code state representation: {code_state_representation}")

class SQLWriterFactory(DBWriterFactor):
    def __init__(self, db_config, metadata):
        super().__init__(db_config, metadata)
        self.engine = create_engine(db_config.sqlalchemy_url, echo=db_config.echo)

    def __call__(self):
        try:
            conn = self.engine.connect()
            context = SQLContext(conn, None) # TODO: Metadata!
            writer = SQLWriter(context, self.create_codestate_writer(context))
            yield writer
        finally:
            conn.close()


def create_db_writer_factory(api_config: PS2APIConfigBase):
    db_config = api_config.database_config
    metadata = api_config.metadata
    if isinstance(db_config, PS2DatabaseConfig):
        return SQLWriterFactory(db_config, metadata)
    elif isinstance(db_config, PS2CSVConfig):
        # CSV Writer would be reasonable in a log translation context
        # But really what's the advantage? I think we should only
        # support SQL writing, but support SQL + CSV reading.
        raise NotImplementedError("CSV writer not implemented yet")
