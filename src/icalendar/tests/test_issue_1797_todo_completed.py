"""Tests for issue #1797: Todo.COMPLETED property."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from icalendar import Todo
from icalendar.error import InvalidCalendar

UTC = ZoneInfo("UTC")


def test_todo_example_completed(todos):
    """Test loading Todo example from todos/completed.ics."""
    todo = todos.completed
    assert todo.name == "VTODO"
    expected = datetime(2007, 5, 1, 0, 0, tzinfo=UTC)
    assert todo.COMPLETED == expected


def test_calendar_todo_completed(calendars):
    """Test loading calendar from calendars/todo_completed.ics."""
    todo = calendars.todo_completed.todos[0]
    expected = datetime(2007, 5, 1, 0, 0, tzinfo=UTC)
    assert todo.COMPLETED == expected


def test_rfc5545_completed_datetime_example(todos):
    """Test parsing RFC 5545 section 3.8.2.1 example: COMPLETED:19960401T150000Z."""
    todo = todos.rfc5545_completed
    assert todo.COMPLETED == datetime(1996, 4, 1, 15, 0, tzinfo=UTC)


def test_completed_get_set_del():
    """Test getting, setting, and deleting COMPLETED."""
    todo = Todo()
    assert todo.COMPLETED is None
    assert "COMPLETED" not in todo

    # Set UTC datetime via COMPLETED
    dt_utc = datetime(2026, 9, 16, 12, 0, tzinfo=timezone.utc)
    todo.COMPLETED = dt_utc
    assert todo.COMPLETED == datetime(2026, 9, 16, 12, 0, tzinfo=UTC)

    # Delete via COMPLETED
    del todo.COMPLETED
    assert todo.COMPLETED is None
    assert "COMPLETED" not in todo

    # Set date via COMPLETED
    d = date(2026, 9, 16)
    todo.COMPLETED = d
    assert todo.COMPLETED == datetime(2026, 9, 16, 0, 0, tzinfo=UTC)

    # Set None via COMPLETED
    todo.COMPLETED = None
    assert todo.COMPLETED is None
    assert "COMPLETED" not in todo


def test_todo_new_with_completed():
    """Test creating a new Todo with the completed parameter."""
    dt_utc = datetime(2026, 9, 16, 14, 30, tzinfo=timezone.utc)
    todo = Todo.new(summary="Test Todo", completed=dt_utc)
    assert todo.COMPLETED == datetime(2026, 9, 16, 14, 30, tzinfo=UTC)

    # With date
    d = date(2026, 9, 16)
    todo_date = Todo.new(summary="Test Todo", completed=d)
    assert todo_date.COMPLETED == datetime(2026, 9, 16, 0, 0, tzinfo=UTC)

    # Without completed
    todo_none = Todo.new(summary="Test Todo")
    assert todo_none.COMPLETED is None
    assert "COMPLETED" not in todo_none


def test_invalid_completed():
    """Test setting invalid types or invalid values raises appropriate errors."""
    todo = Todo()
    with pytest.raises(TypeError):
        todo.COMPLETED = "not a date"

    with pytest.raises(TypeError):
        todo.COMPLETED = 12345

    # Invalid value directly in component dict
    todo["COMPLETED"] = 12345
    with pytest.raises(InvalidCalendar):
        _ = todo.COMPLETED
