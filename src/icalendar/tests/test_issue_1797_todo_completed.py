"""Tests for issue #1797: Todo.COMPLETED and Todo.completed properties."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from icalendar import Todo
from icalendar.error import InvalidCalendar

UTC = ZoneInfo("UTC")


def test_todo_example_completed():
    """Test loading Todo example from todos/completed.ics."""
    todo = Todo.example("completed")
    assert todo.name == "VTODO"
    expected = datetime(2007, 5, 1, 0, 0, tzinfo=UTC)
    assert todo.COMPLETED == expected
    assert todo.completed == expected


def test_calendar_todo_completed(calendars):
    """Test loading calendar from calendars/todo_completed.ics."""
    cal = calendars.todo_completed
    vtodos = [c for c in cal.walk() if c.name == "VTODO"]
    assert len(vtodos) == 1
    todo = vtodos[0]
    expected = datetime(2007, 5, 1, 0, 0, tzinfo=UTC)
    assert todo.COMPLETED == expected
    assert todo.completed == expected


def test_rfc5545_completed_datetime_example():
    """Test parsing RFC 5545 section 3.8.2.1 example: COMPLETED:19960401T150000Z."""
    raw = (
        "BEGIN:VTODO\r\n"
        "UID:20070313T123432Z-456553@example.com\r\n"
        "DTSTAMP:20070313T123432Z\r\n"
        "COMPLETED:19960401T150000Z\r\n"
        "END:VTODO\r\n"
    )
    todo = Todo.from_ical(raw)
    assert todo.COMPLETED == datetime(1996, 4, 1, 15, 0, tzinfo=UTC)
    assert todo.completed == datetime(1996, 4, 1, 15, 0, tzinfo=UTC)


def test_completed_get_set_del():
    """Test getting, setting, and deleting COMPLETED and completed."""
    todo = Todo()
    assert todo.COMPLETED is None
    assert todo.completed is None
    assert "COMPLETED" not in todo

    # Set UTC datetime via COMPLETED
    dt_utc = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
    todo.COMPLETED = dt_utc
    assert todo.COMPLETED == datetime(2026, 9, 16, 12, 0, tzinfo=UTC)
    assert todo.completed == datetime(2026, 9, 16, 12, 0, tzinfo=UTC)

    # Delete via COMPLETED
    del todo.COMPLETED
    assert todo.COMPLETED is None
    assert todo.completed is None
    assert "COMPLETED" not in todo

    # Set date via completed
    d = date(2026, 9, 16)
    todo.completed = d
    assert todo.COMPLETED == datetime(2026, 9, 16, 0, 0, tzinfo=UTC)
    assert todo.completed == datetime(2026, 9, 16, 0, 0, tzinfo=UTC)

    # Set None via completed
    todo.completed = None
    assert todo.COMPLETED is None
    assert todo.completed is None
    assert "COMPLETED" not in todo

    # Set and delete via del todo.completed
    todo.completed = dt_utc
    assert "COMPLETED" in todo
    del todo.completed
    assert todo.COMPLETED is None
    assert todo.completed is None
    assert "COMPLETED" not in todo


def test_todo_new_with_completed():
    """Test creating a new Todo with the completed parameter."""
    dt_utc = datetime(2026, 9, 16, 14, 30, tzinfo=timezone.utc)
    todo = Todo.new(summary="Test Todo", completed=dt_utc)
    assert todo.completed == datetime(2026, 9, 16, 14, 30, tzinfo=UTC)
    assert todo.COMPLETED == todo.completed

    # With date
    d = date(2026, 9, 16)
    todo_date = Todo.new(summary="Test Todo", completed=d)
    assert todo_date.completed == datetime(2026, 9, 16, 0, 0, tzinfo=UTC)

    # Without completed
    todo_none = Todo.new(summary="Test Todo")
    assert todo_none.completed is None
    assert todo_none.COMPLETED is None
    assert "COMPLETED" not in todo_none


def test_invalid_completed():
    """Test setting invalid types or invalid values raises appropriate errors."""
    todo = Todo()
    with pytest.raises(TypeError):
        todo.COMPLETED = "not a date"

    with pytest.raises(TypeError):
        todo.completed = 12345

    # Invalid value directly in component dict
    todo["COMPLETED"] = 12345
    with pytest.raises(InvalidCalendar):
        _ = todo.COMPLETED
