
from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib

from pydantic import BaseModel


class CodeStateSection(BaseModel):
    """
    A class representing the state of a file at a given time.
    """
    Code: str
    CodeStateSection: str = None

@dataclass
class CodeStateEntry():
    sections: list[CodeStateSection]
    # Must include the subject ID, since this is needed for
    # Directory and Git representations
    grouping_id: str
    ProjectID: str

    @classmethod
    def from_code(cls, code: str, grouping_id: str, ProjectID: str) -> "CodeStateEntry":
        return cls(sections=[CodeStateSection(Code=code)], grouping_id=grouping_id, ProjectID=ProjectID)

class CodeStateWriter(ABC):

    def get_codestate_id_from_hash(self, codestate: CodeStateEntry) -> str:
        sections = codestate.sections
        # Sort sections to ensure consistent ID generation
        sections = sorted(sections, key=lambda x: x.CodeStateSection or "")
        # Generate a unique ID based on the sections
        sections_str = "\0".join([
            section.Code if section.CodeStateSection is None else section.CodeStateSection + section.Code
            for section in sections
        ])
        # Hash the sections string to create a unique ID
        return hashlib.sha256(sections_str.encode('utf-8')).hexdigest()

    def _get_default_codestate_section():
        return 'default.txt'

    @abstractmethod
    def add_codestate_and_get_id(self, codestate: CodeStateEntry) -> str:
        pass

