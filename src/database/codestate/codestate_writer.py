
from abc import ABC, abstractmethod
import hashlib
from typing import Optional

from spec.codestate import CodeStateEntry, CodeStateSection


class ContextualCodeStateEntry(CodeStateEntry):
    """
    Represents a CodeState with additional context needed for logging for
    organization in filesystem-based representations (Git and Directory).
    This context can be inferred automatically from events. It is not used
    in the Table representation.
    """

    # There's a weird discrepancy in the 3 CodeState representations
    # where in Table a CodeStateID has nothing to do with the SubjectID or ProjectID,
    # but in the filesystem-based representations, we do use that information for subfolders.
    # Should this information be strictly required for all representations, even if not used?
    # I think if we infer it from events it will be fine. This can lead to identical codestates
    # for different subjects, but I think that's okay if using Git or Directory formats.

    # Must include the subject ID, since this is needed for
    # Directory and Git representations
    grouping_id: str = None
    ProjectID: Optional[str] = None

    @classmethod
    def from_codestate_entry(cls, codestate_entry: CodeStateEntry, grouping_id: str, project_id: str) -> "ContextualCodeStateEntry":
        return cls(
            sections=codestate_entry.sections,
            grouping_id=grouping_id,
            ProjectID=project_id
        )

    @classmethod
    def from_code(cls, code: str, grouping_id: str | None, project_id: str | None) -> "CodeStateEntry":
        return cls(sections=[CodeStateSection(Code=code)], grouping_id=grouping_id, ProjectID=project_id)


class CodeStateWriter(ABC):

    def get_codestate_id_from_hash(self, codestate: ContextualCodeStateEntry) -> str:
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

