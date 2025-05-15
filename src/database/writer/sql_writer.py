from sqlalchemy import insert
from database.codestate.codestate_writer import CodeStateEntry, CodeStateSection, CodeStateWriter
from database.writer.db_writer import DBWriter, LogResult
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

    def add_events_with_codestates(self, events: list[dict[str,any]], codestates: dict[str, CodeStateEntry]) -> LogResult:
        result = LogResult(True)

        # TODO: Rework this to work with the dict, not the object
        # for event in events:
        #     result.warnings.append([str(warning) for warning in self.context.event_validator.validate_event(event)])

        self.optimize_codestate_ids(events, codestates, result)

        main_table = self.context.table_manager.main_table

        # TODO: This doesn't appear to be working...
        for event in events:
            try:
                statement = insert(main_table).values(**event)
                self.conn.execute(statement)
                self.conn.commit()
            except Exception as e:
                result.errors.append(f"Error inserting events: {e}")
                self.conn.rollback()
                result.success = False

        return result

    def optimize_codestate_ids(self, events: list[dict[str,any]], codestates: dict[str, CodeStateEntry], result: LogResult) -> None:
        if not self.context.data_config.optimize_codestate_ids:
            return

        temp_codestate_id_map = {}
        for temp_id, codestate in codestates.items():
            code_state_id = self.codestate_writer.add_codestate_and_get_id(codestate)
            temp_codestate_id_map[temp_id] = code_state_id

        for event in events:
            if MTC.CodeStateID in event:
                if event[MTC.CodeStateID] not in temp_codestate_id_map:
                    result.warnings.append(f"CodeStateID {event[MTC.CodeStateID]} not found in temp_codestate_id_map.")
                    continue

                event[MTC.CodeStateID] = temp_codestate_id_map[event[MTC.CodeStateID]]

    def initialize_database(self):
        self.context.table_manager.create_tables(self.conn)
        self.context.table_manager.update_metadata_values(self.conn)