from sqlalchemy import insert
from database.codestate.codestate_writer import ContextualCodeStateEntry, CodeStateWriter
from database.sql_context import SQLContext
from spec.enums import CodeStatesTableColumns as Cols


class TableCodeStateWriter(CodeStateWriter):

    def __init__(self, context: SQLContext):
        super().__init__()
        self.conn = context.conn
        self.table = context.table_manager.codestates_table

    def add_codestate_and_get_id(self, codestate: ContextualCodeStateEntry) -> str:
        codestate_id = self.get_codestate_id_from_hash(codestate)
        self.add_codestate_with_id(codestate, codestate_id)
        return codestate_id

    def add_codestate_with_id(self, codestate: ContextualCodeStateEntry, codestate_id: str):
        # Execute as a transaction to ensure atomicity
        with self.conn.begin():
            # Check if the code state already exists in the database
            select_statement = self.table.select().where(
                self.table.c.CodeStateID == codestate_id
            )
            result = self.conn.execute(select_statement).fetchone()
            if result:
                # TODO: It might be good to check that the stored code state matches
                # the one we are trying to add
                return

            # Add the code state to the CodeStates table using a structured query
            for section in codestate.sections:
                statement = self.table.insert().values(**{
                        Cols.CodeStateID: codestate_id,
                        Cols.Code: section.Code,
                        Cols.CodeStateSection: section.CodeStateSection
                })
                self.conn.execute(statement)



