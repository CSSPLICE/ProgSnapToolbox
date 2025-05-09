import os
from git import Repo

from progsnap2.database.codestate.codestate_writer import CodeStateWriter
from progsnap2.database.codestate.codestate_writer import CodeStateEntry

# TODO: Handle locking and other things?
# This would probably require a fair bit of work, may be out of scope
# but I can at least create this MVP for now
class GitCodeStateWriter(CodeStateWriter):

    def __init__(self, code_states_dir_path: str):
        super().__init__()
        self.root = code_states_dir_path

    def add_codestate_and_get_id(self, codestate: CodeStateEntry) -> str:
        grouping_id = codestate.grouping_id or ''
        directory = os.path.join(self.root, grouping_id, codestate.ProjectID)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            # create a new git repo in the director
            repo = Repo.init(directory)
        else:
            repo = Repo(directory)

        # Delete all non-git files in the directory
        for root, _, files in os.walk(directory):
            for file in files:
                if file != ".git":
                    os.remove(os.path.join(root, file))

        # Add the code state to the git repo
        for section in codestate.sections:
            # TODO: Should I force the section to exist (probably not good for Table format / convenience)
            # Or have the config supply a default filename?
            file_path = os.path.join(directory, section.CodeStateSection or self._get_default_codestate_section())
            with open(file_path, 'w') as f:
                f.write(section.Code)

        # Add all files to the repo
        repo.git.add(A=True)

        # Check whether anything has changed
        if repo.is_dirty(untracked_files=True):
            # Commit the changes
            repo.index.commit(f"Automatic update")

        # Get the commit hash
        commit = repo.head.commit
        # Return the commit hash as the ID
        return commit.hexsha
