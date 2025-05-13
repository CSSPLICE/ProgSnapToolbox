

from pydantic import BaseModel


class CodeStateSection(BaseModel):
    """
    A class representing the state of a file at a given time.
    """
    Code: str
    CodeStateSection: str = None

class CodeStateEntry(BaseModel):
    """
    A class representing the state of a whole project at a given time.
    """
    sections: list[CodeStateSection]

    @classmethod
    def from_code(cls, code: str) -> "CodeStateEntry":
        return cls(sections=[CodeStateSection(Code=code)])