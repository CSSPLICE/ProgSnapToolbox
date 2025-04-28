import enum

class EventType(enum.Enum):
    """
    Enum for event types in the Progsnap2 dataset.
    """

    """
    Marks the start of a work session.
    """
    Session_Start = "Session.Start"

    """
    Marks the end of a work session.
    """
    Session_End = "Session.End"


class IDColumn(enum.Enum):
    """
    Enum for ID columns in the Progsnap2 dataset.
    """

    """
    The ID of the student.
    """
    Subject_ID = "SubjectID"

    """
    The ID of the course.
    """
    Course_ID = "CourseID"

    """
    The ID of the assignment.
    """
    Assignment_ID = "AssignmentID"

class Test:
    def foo():
        assert IDColumn.Student_ID == "StudentID"