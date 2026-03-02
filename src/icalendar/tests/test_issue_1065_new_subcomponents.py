"""Tests for issue #1065: new() subcomponents parameter."""

from datetime import timedelta

from icalendar import Alarm, Event, Todo
from icalendar.cal.component import Component


def _make_alarm() -> Alarm:
    """Create a minimal valid Alarm with a TRIGGER."""
    alarm = Alarm()
    alarm["ACTION"] = "DISPLAY"
    alarm.TRIGGER = timedelta(minutes=-15)
    return alarm


def test_component_new_with_subcomponents():
    child = Component()
    child["X-TEST"] = "value"
    parent = Component.new(subcomponents=[child])
    assert len(parent.subcomponents) == 1
    assert parent.subcomponents[0] is child


def test_component_new_without_subcomponents():
    component = Component.new()
    assert component.subcomponents == []


def test_event_new_with_subcomponents():
    alarm = _make_alarm()
    event = Event.new(summary="Test", subcomponents=[alarm])
    assert len(event.subcomponents) == 1
    assert event.subcomponents[0] is alarm


def test_todo_new_with_subcomponents():
    alarm = _make_alarm()
    todo = Todo.new(summary="Test", subcomponents=[alarm])
    assert len(todo.subcomponents) == 1
    assert todo.subcomponents[0] is alarm


def test_event_new_without_subcomponents():
    event = Event.new(summary="Test")
    assert event.subcomponents == []


def test_todo_new_without_subcomponents():
    todo = Todo.new(summary="Test")
    assert todo.subcomponents == []
