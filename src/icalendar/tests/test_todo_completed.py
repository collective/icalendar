from datetime import datetime, timezone

from icalendar import Calendar, Todo


def test_todo_completed_property(calendars):
    """Test Todo.COMPLETED property access with fixture calendar."""
    cal = calendars.issue_1797_todo_completed
    (todo,) = cal.todos
    assert todo.COMPLETED == datetime(2007, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert todo.completed == datetime(2007, 5, 1, 0, 0, tzinfo=timezone.utc)


def test_todo_completed_without_value_parameter():
    """Test Todo.COMPLETED with date string without VALUE=DATE."""
    ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VTODO
UID:20070313T123432Z-456553@example.com
DTSTAMP:20070313T123432Z
COMPLETED:20070501
SUMMARY:Submit Quebec Income Tax Return for 2006
CLASS:CONFIDENTIAL
CATEGORIES:FAMILY,FINANCE
STATUS:NEEDS-ACTION
END:VTODO
END:VCALENDAR"""
    cal = Calendar.from_ical(ics)
    (todo,) = cal.todos
    assert todo.COMPLETED == datetime(2007, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert todo.completed == datetime(2007, 5, 1, 0, 0, tzinfo=timezone.utc)


def test_todo_completed_with_utc_datetime():
    """Test Todo.COMPLETED with explicit UTC datetime."""
    ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VTODO
UID:20070313T123432Z-456553@example.com
DTSTAMP:20070313T123432Z
COMPLETED:20070501T133000Z
SUMMARY:Submit Quebec Income Tax Return for 2006
END:VTODO
END:VCALENDAR"""
    cal = Calendar.from_ical(ics)
    (todo,) = cal.todos
    assert todo.COMPLETED == datetime(2007, 5, 1, 13, 30, tzinfo=timezone.utc)
    assert todo.completed == datetime(2007, 5, 1, 13, 30, tzinfo=timezone.utc)


def test_todo_completed_setter_and_deleter():
    """Test setter and deleter for Todo.COMPLETED and todo.completed."""
    todo = Todo()
    assert todo.COMPLETED is None
    assert todo.completed is None

    todo.completed = datetime(2024, 10, 24, 12, 0, tzinfo=timezone.utc)
    assert todo.COMPLETED == datetime(2024, 10, 24, 12, 0, tzinfo=timezone.utc)

    del todo.completed
    assert todo.COMPLETED is None

    todo.COMPLETED = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert todo.completed == datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)

    del todo.COMPLETED
    assert todo.COMPLETED is None
