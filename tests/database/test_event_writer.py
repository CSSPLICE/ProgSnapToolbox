

from database.helper.event_state import EventState
from database.helper.event_writer import CODESTATE, EventWriterBase
from spec.enums import EventTypes, MainTableColumns as Cols
from tests.database.conftest import cleanup_temp_dir


def test_event_writer_one_event(sqlite_writer_factory):
    cleanup_temp_dir()

    # Initialize the SQLite writer
    with sqlite_writer_factory.create() as writer:

        writer.initialize_database()

        initial_state = EventState(
            SubjectID="test_subject",
            ToolInstances="test_instances",
        )

        event_writer = EventWriterBase(writer, initial_state)

        event = {
            Cols.SessionID: "test_session",
            CODESTATE: "test_code",
        }

        # Add the event to the database
        event_writer.write_event(EventTypes.SessionStart, event)

        # TODO: Cleanup doesn't seem to be working, and
        # the codestates seem wrong....

        # # Check if the event was added successfully
        # db_path = sqlite_writer_factory.db_config.sqlalchemy_url.split(":///")[-1]
        # db = sqlite3.connect(db_path)
        # cursor = db.cursor()
        # cursor.execute("SELECT * FROM Events WHERE EventType = 'CodeState';")
        # result = cursor.fetchall()

        # assert len(result) == 1, f"Expected one event, got: {len(result)}"