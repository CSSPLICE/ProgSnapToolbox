
import os
import copy
from database.codestate.codestate_writer import CodeStateEntry, CodeStateSection, CodeStateWriter
from database.codestate.directory_codestate_writer import DirectoryTableWriter
from database.codestate.git_codestate_writer import GitCodeStateWriter

temp_dir = "test_data/codestates"

class CodestateGenerator():

    def __init__(self):

        grouping_id = "subject_1"
        project_id = "project_1"

        self.codestate1 = CodeStateEntry(
            sections=[
                CodeStateSection(Code = "print('Hello, World!')", CodeStateSection = "main.py"),
                CodeStateSection(Code = "def greet(): pass", CodeStateSection = "greet.py")
            ],
            grouping_id=grouping_id,
            ProjectID=project_id
        )

        self.codestate2 = copy.deepcopy(self.codestate1)
        self.codestate2.sections[0].Code = "print('Hello, Universe!')"

        self.codestate3 = copy.deepcopy(self.codestate2)
        self.codestate3.sections[1].Code = "def greet(): print('Hello!')"

gen = CodestateGenerator()

def cleanup():
    # Clean up the temporary directory from prior tests
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)



def test_directory_codestate_writer():
    # Initialize the DirectoryTableWriter
    writer = DirectoryTableWriter(temp_dir)

    cleanup()

    # Add the codestate and get its ID
    codestate_id_1 = writer.add_codestate_and_get_id(gen.codestate1)

    # Check if the directory was created
    assert os.path.exists(os.path.join(temp_dir, gen.codestate1.grouping_id, codestate_id_1))

    codestate_id_1_again = writer.add_codestate_and_get_id(gen.codestate1)
    assert codestate_id_1_again == codestate_id_1, "Duplicate codestate should return the same ID"

    codestate_id_2 = writer.add_codestate_and_get_id(gen.codestate2)
    assert os.path.exists(os.path.join(temp_dir, gen.codestate2.grouping_id, codestate_id_2))
    assert codestate_id_2 != codestate_id_1, "Different codestates should return different IDs"

def test_git_codestate_writer():
    # Initialize the DirectoryTableWriter
    writer = GitCodeStateWriter(temp_dir)

    cleanup()

    # Add the codestate and get its ID
    codestate_id_1 = writer.add_codestate_and_get_id(gen.codestate1)

    # Check if the directory was created
    assert os.path.exists(os.path.join(temp_dir, gen.codestate1.grouping_id, gen.codestate1.ProjectID))

    codestate_id_1_again = writer.add_codestate_and_get_id(gen.codestate1)
    assert codestate_id_1_again == codestate_id_1, "Duplicate codestate should return the same ID"

    codestate_id_2 = writer.add_codestate_and_get_id(gen.codestate2)
    assert codestate_id_2 != codestate_id_1, "Different codestates should return different IDs"




