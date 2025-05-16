import datetime
from sqlalchemy import insert
from database.codestate.codestate_writer import CodeStateEntry, CodeStateWriter
from database.writer.db_writer import DBWriter, LogResult
from database.sql_context import SQLContext
from spec.datatypes import get_current_timestamp
from spec.enums import MainTableColumns as Cols

EventList = list[dict[str, any]]
CodeStatesMap = dict[str, CodeStateEntry]

# TODO: When stable, move non-SQL-specific methods to DBWriter
class SQLWriter(DBWriter):

    def __init__(self, context: SQLContext, codestate_writer: CodeStateWriter):
        super().__init__()
        self.context = context
        self.codestate_writer: CodeStateWriter = codestate_writer

    @property
    def conn(self):
        return self.context.conn

    def add_server_timestamps(self, events: EventList) -> None:
        for event in events:
            if Cols.ServerTimestamp not in event:
                event[Cols.ServerTimestamp] = get_current_timestamp()

    def add_events_with_codestates(self, events: EventList, codestates: CodeStatesMap) -> LogResult:
        result = LogResult(True)

        # TODO: Rework this to work with the dict, not the object
        # for event in events:
        #     result.warnings.append([str(warning) for warning in self.context.event_validator.validate_event(event)])

        # TODO: I wonder if we should pass the result to append warnings
        # TODO: Where does the ContextualCodeStateEntry get created here?
        if self.context.data_config.optimize_codestate_ids:
            self._optimize_codestate_ids(events, codestates, result)
        else:
            for codestate_id, codestate in codestates.items():
                self.codestate_writer.add_codestate_with_id(codestate, codestate_id)

        main_table = self.context.table_manager.main_table

        for event in events:
            try:
                print("Insert!")
                print(event)
                statement = insert(main_table).values(**event)
                self.conn.execute(statement)
            except Exception as e:
                result.errors.append(f"Error inserting events: {e}")
                self.conn.rollback()
                result.success = False
                break

        if result.success:
            self.conn.commit()

        return result

    def _optimize_codestate_ids(self, events: EventList, codestates: CodeStatesMap, result: LogResult) -> None:
        temp_codestate_id_map = {}
        for temp_id, codestate in codestates.items():
            code_state_id = self.codestate_writer.add_codestate_and_get_id(codestate)
            temp_codestate_id_map[temp_id] = code_state_id

        for event in events:
            if Cols.CodeStateID in event:
                if event[Cols.CodeStateID] not in temp_codestate_id_map:
                    result.warnings.append(f"CodeStateID {event[Cols.CodeStateID]} not found in temp_codestate_id_map.")
                    continue

                event[Cols.CodeStateID] = temp_codestate_id_map[event[Cols.CodeStateID]]

    def initialize_database(self):
        self.context.table_manager.create_tables(self.conn)
        self.context.table_manager.update_metadata_values(self.conn)