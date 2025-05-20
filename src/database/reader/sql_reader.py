from pandas import DataFrame
from database.codestate.codestate_writer import CodeStateWriter
from database.reader.ps2_reader import PS2Reader
from database.sql_context import SQLContext

import pandas as pd
from pandas import DataFrame

from database.sql_table_manager import SQLTableManager


class SQLReader(PS2Reader):

    # TODO: If I'm not really using SQLalchemy directly, it's worth asking
    # if I need the whole SQLContext or if a better approach makes sense.
    # Will come back to this later.
    def __init__(self, codestate_io: CodeStateWriter, context: SQLContext):
        super().__init__(codestate_io, context)

    @property
    def table_manager(self) -> SQLTableManager:
        return self.context.table_manager

    def get_main_table(self) -> DataFrame:
        pd.read_sql(
            f"SELECT * FROM {self.table_manager.main_table_name}",
            self.context.conn,
        )