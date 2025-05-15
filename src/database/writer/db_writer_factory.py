
from abc import ABC, abstractmethod
import os
from database.codestate.git_codestate_writer import GitCodeStateWriter
from database.codestate.directory_codestate_writer import DirectoryCodeStateWriter
from database.codestate.table_codestate_writer import TableCodeStateWriter
from database.config import PS2CSVConfig, PS2DatabaseConfig, PS2DataConfig

from sqlalchemy import Connection, create_engine
from database.config import PS2DatabaseConfig, PS2DataConfig
from database.sql_table_manager import SQLTableManager
from database.writer.sql_writer import SQLContext, SQLWriter
from spec.enums import CodeStateRepresentation
from spec.spec_definition import ProgSnap2Spec

class DBWriterFactory(ABC):
    def __init__(self, ps2_spec: ProgSnap2Spec, db_config: PS2DataConfig):
        self.ps2_spec = ps2_spec
        self.db_config = db_config

    @abstractmethod
    def create(self):
        pass

    def _create_codestate_writer(self, db_config: PS2DatabaseConfig, context: SQLContext):
        # TODO: These aren't actually the same enum right now... so need to str convert
        code_state_representation = str(self.db_config.metadata.CodeStateRepresentation)
        if code_state_representation == CodeStateRepresentation.Table:
            return TableCodeStateWriter(context)
        elif code_state_representation == CodeStateRepresentation.Directory:
            raise DirectoryCodeStateWriter(db_config.codestates_dir)
        elif code_state_representation == CodeStateRepresentation.Git:
            raise GitCodeStateWriter(db_config.codestates_dir)
        else:
            raise ValueError(f"Invalid code state representation: {code_state_representation}")

    @classmethod
    def create_factory(cls, ps2_spec: ProgSnap2Spec, db_config: PS2DataConfig) -> "DBWriterFactory":
        if isinstance(db_config, PS2DatabaseConfig):
            return SQLWriterFactory(ps2_spec, db_config)
        elif isinstance(db_config, PS2CSVConfig):
            # CSV Writer would be reasonable in a log translation context
            # But really what's the advantage? I think we should only
            # support SQL writing, but support SQL + CSV reading.
            raise NotImplementedError("CSV writer not implemented yet")


class SQLWriterFactory(DBWriterFactory):
    def __init__(self, ps2_spec: ProgSnap2Spec, db_config: PS2DataConfig):
        super().__init__(ps2_spec, db_config)
        # Create the root directory if it doesn't exist
        os.makedirs(db_config.root_path, exist_ok=True)
        self.engine = create_engine(db_config.sqlalchemy_url, echo=db_config.echo)
        self.table_manager = SQLTableManager(ps2_spec, db_config.metadata)

    def create(self) -> "SQLWriterContextManager":
        return SQLWriterContextManager(self)

# Use a context manager to handle the connection lifecycle
class SQLWriterContextManager:
    def __init__(self, factory: SQLWriterFactory):
        self.factory = factory
        self.conn = None

    def __enter__(self):
        self.conn = self.factory.engine.connect()
        context = SQLContext(self.conn, self.factory.table_manager, self.factory.db_config, self.factory.ps2_spec)
        return SQLWriter(context, self.factory._create_codestate_writer(self.factory.db_config, context))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

