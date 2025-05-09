from sqlalchemy import insert
from database.codestate.codestate_writer import CodeStateSection, CodeStateWriter
from database.db_writer import DBWriter
from database.sql_context import SQLContext
from spec.enums import MainTableColumns as MTC, CoreTables

class SQLWriter(DBWriter):

    def __init__(self, context: SQLContext, codestate_writer: CodeStateWriter):
        super().__init__()
        self.context = context
        self.codestate_writer = codestate_writer
        pass

    def add_events_with_codestates(self, events: dict[str,any], codestates: list[CodeStateSection]):
        temp_codestate_id_map = {}
        for codestate in codestates:
            code_state_id = self.codestate_writer.add_codestate_and_get_ID(codestate)
            temp_codestate_id_map[codestate.TempCodeStateID] = code_state_id

        for event in events:
            if "TempCodeStateID" in event:
                event[MTC.CodeStateID] = temp_codestate_id_map[event["TempCodeStateID"]]
                del event["TempCodeStateID"]

        main_table = self.context.metadata.tables[CoreTables.MainTable]
        statement = insert(main_table).values(events)