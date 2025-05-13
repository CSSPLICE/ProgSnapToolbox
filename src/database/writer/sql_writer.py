from sqlalchemy import insert
from database.codestate.codestate_writer import CodeStateEntry, CodeStateSection, CodeStateWriter
from database.writer.db_writer import DBWriter
from database.sql_context import SQLContext
from spec.enums import MainTableColumns as MTC, CoreTables

# TODO: When stable, move non-SQL-specific methods to DBWriter
class SQLWriter(DBWriter):

    def __init__(self, context: SQLContext, codestate_writer: CodeStateWriter):
        super().__init__()
        self.context = context
        self.codestate_writer: CodeStateWriter = codestate_writer

    @property
    def conn(self):
        return self.context.conn

    def add_events_with_codestates(self, events: dict[str,any], codestates: dict[str, CodeStateEntry]):
        # TODO: Shouldn't I move the validator here? and maybe events too...
        # TODO: Add option to not auto-add codestates...?
        temp_codestate_id_map = {}
        for temp_id, codestate in codestates.items():
            code_state_id = self.codestate_writer.add_codestate_and_get_id(codestate)
            temp_codestate_id_map[temp_id] = code_state_id

        for event in events:
            if "TempCodeStateID" in event:
                event[MTC.CodeStateID] = temp_codestate_id_map[event["TempCodeStateID"]]
                del event["TempCodeStateID"]

        main_table = self.context.table_manager.main_table
        statement = insert(main_table).values(events)
        self.conn.execute(statement)
        self.conn.commit()

    def initialize_database(self):
        self.context.table_manager.create_tables(self.conn)
        self.context.table_manager.update_metadata_values(self.conn)