
from abc import ABC, abstractmethod
import uuid

from pydantic import BaseModel
from sqlalchemy import Connection, MetaData, Table, insert

from progsnap2.database.sql_context import SQLContext


class CodeStateSection(BaseModel):
    """
    A class representing the state of a file at a given time.
    """
    Code: str
    CodeStateSection: str = None

class CodeStateWriter(ABC):

    def add_single_codestate_and_get_ID(self, code: str) -> str:
        return self.add_codestate_and_get_ID([CodeStateSection(Code=code)])

    def add_single_codestate_with_ID(self, code: str, ID: str) -> None:
        self.add_codestate_with_ID([CodeStateSection(Code=code)], ID)

    @abstractmethod
    def add_codestate_and_get_ID(self, sections: list[CodeStateSection]) -> str:
        pass

    @abstractmethod
    def add_codestate_with_ID(self, sections: list[CodeStateSection], ID: str) -> None:
        pass

class TableCodeStateWriter(CodeStateWriter):

    def __init__(self, context: SQLContext):
        super().__init__()
        self.conn = context.conn
        self.table = context.metadata.tables["CodeStates"]

    def add_codestate_and_get_ID(self, sections: list[CodeStateSection]) -> str:
        # Generate UUID for the code state
        code_state_id = str(uuid.uuid4())
        # Add the code state to the CodeStates table using a structured query
        # TODO: Replace with constants!
        for section in sections:
            statement = insert(
                self.table,
                values={
                    "CodeStateID": code_state_id,
                    "Code": section.Code,
                    # TODO: Should this be configurable?
                    "CodeStateSection": section.CodeStateSection
                }
            )
            self.conn.execute(statement)
        return code_state_id

    # def add_codestate_with_ID(self, sections: list[CodeStateSection], ID: str) -> None: