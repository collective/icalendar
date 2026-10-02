"""Add Todo.COMPLETED as a UTC datetime property.

See https://github.com/collective/icalendar/issues/1797
"""

from datetime import date, datetime

import pytest

from icalendar import Event, Todo
from icalendar.error import InvalidCalendar
from icalendar.prop import vDDDTypes


def test_completed_from_date_only_ics(calendars, tzp):
    """COMPLETED:20070501 is converted to midnight UTC."""
    todo = calendars.issue_1797_todo_completed.todos[0]
    assert todo.COMPLETED == tzp.localize_utc(datetime(2007, 5, 1))


def test_completed_from_value_date_ics(calendars, tzp):
    """COMPLETED;VALUE=DATE:20070501 is converted to midnight UTC."""
    todo = calendars.issue_1797_todo_completed_value_date.todos[0]
    assert todo.COMPLETED == tzp.localize_utc(datetime(2007, 5, 1))


def test_completed_set_and_get(tzp):
    """COMPLETED can be assigned a date or datetime and is stored in UTC."""
    todo = Todo()
    todo.COMPLETED = date(2007, 5, 1)
    assert todo.COMPLETED == tzp.localize_utc(datetime(2007, 5, 1))
    todo.COMPLETED = datetime(2007, 5, 1, 13, 17, 11)
    assert todo.COMPLETED == tzp.localize_utc(datetime(2007, 5, 1, 13, 17, 11))


def test_completed_missing_is_none():
    """Absent COMPLETED returns None."""
    assert Todo().COMPLETED is None


def test_completed_delete():
    """COMPLETED can be deleted."""
    todo = Todo()
    todo.COMPLETED = date(2007, 5, 1)
    del todo.COMPLETED
    assert todo.COMPLETED is None


def test_completed_invalid_set():
    """Non-date values cannot be assigned."""
    todo = Todo()
    with pytest.raises(TypeError, match="COMPLETED takes a datetime in UTC"):
        todo.COMPLETED = "not-a-date"


def test_completed_invalid_get():
    """Non-date stored values raise InvalidCalendar."""
    todo = Todo()
    todo["COMPLETED"] = "not-a-date"
    with pytest.raises(InvalidCalendar, match="COMPLETED must be a datetime in UTC"):
        todo.COMPLETED  # noqa: B018


def test_completed_not_on_event():
    """RFC 5545 defines COMPLETED only on VTODO."""
    assert not hasattr(Event(), "COMPLETED")


def test_completed_roundtrip_vdddtypes(tzp):
    """Values stored via add() are readable through the property."""
    todo = Todo()
    todo.add("COMPLETED", date(2007, 5, 1))
    assert isinstance(todo.get("COMPLETED"), vDDDTypes)
    assert todo.COMPLETED == tzp.localize_utc(datetime(2007, 5, 1))
