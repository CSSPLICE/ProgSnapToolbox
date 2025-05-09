
import os
from database.codestate.codestate_writer import CodeStateEntry, CodeStateSection
from database.codestate.directory_codestate_writer import DirectoryTableWriter

temp_dir = "test_data/codestates"



def test_directory_codestate_writer():

    # Clean up the temporary directory from prior tests
    import shutil
    shutil.rmtree(temp_dir)

    # Initialize the DirectoryTableWriter
    writer = DirectoryTableWriter(temp_dir)

    grouping_id = "subject_1"
    project_id = "project_1"

    # Create a sample CodeStateEntry
    codestate = CodeStateEntry(
        sections=[
            CodeStateSection(Code = "print('Hello, World!')", CodeStateSection = "main.py"),
            CodeStateSection(Code = "def greet(): pass", CodeStateSection = "greet.py")
        ],
        grouping_id=grouping_id,
        ProjectID=project_id
    )

    # Add the codestate and get its ID
    codestate_id = writer.add_codestate_and_get_id(codestate)

    # Check if the directory was created
    assert os.path.exists(os.path.join(temp_dir, grouping_id, codestate_id))
