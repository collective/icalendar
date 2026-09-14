"""Tests for issue #1786: Todo.duration should be 0 when only DUE is given."""

from datetime import date, datetime, timedelta

import pytest

from icalendar import Event, Todo
from icalendar.error import IncompleteComponent


def test_issue_1786_exact_reproduction():
    """Test the exact scenario reported in issue #1786."""
    todo = Todo.new(end=datetime(2026, 5, 1, 12, 0))

    assert todo.duration == timedelta(0)
    assert "DUE" in todo
    assert "DTSTART" not in todo


def test_todo_duration_with_due_only_set_via_setter():
    """Duration is 0 when DUE is set directly via the .end setter, no DTSTART."""
    todo = Todo()
    todo.add("UID", "test-due-only")
    todo.end = datetime(2026, 5, 1, 12, 0)

    assert todo.duration == timedelta(0)


def test_todo_duration_with_date_due_only():
    """Duration is 0 for a date (not datetime) DUE with no DTSTART."""
    todo = Todo()
    todo.add("UID", "test-due-only-date")
    todo.end = date(2026, 5, 1)

    assert todo.duration == timedelta(0)


def test_todo_duration_without_any_time_info_still_raises():
    """A component with neither start nor end still raises, unlike DUE-only."""
    todo = Todo()
    todo.add("UID", "test-no-time-at-all")

    with pytest.raises(IncompleteComponent):
        _ = todo.duration


@pytest.mark.parametrize("component_class", [Event, Todo])
def test_component_duration_with_end_only_is_zero(component_class):
    """Both Event and Todo report a 0 duration when only their end is set."""
    component = component_class()
    component.add("UID", f"test-{component_class.__name__.lower()}-end-only")
    component.end = datetime(2026, 5, 1, 12, 0)

    assert component.duration == timedelta(0)
