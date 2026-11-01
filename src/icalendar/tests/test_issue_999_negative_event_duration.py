"""Tests for issue #999: [Bug/Corner case] event.duration<0.

This verifies that negative durations for events are ignored, while negative
durations for todos are allowed.
This is because the iCalendar specification requires that events have a non-negative duration,
while todos can have a negative duration to indicate that they are overdue.
"""

from datetime import datetime, timedelta

from icalendar import Event, Todo


def test_event_negative_duration_ignored():
    event = Event()
    event.start = datetime(2000, 1, 1, 0, 0, 0)
    event.duration = timedelta(seconds=-4)
    assert event.end == event.start


def test_event_zero_duration_ignored():
    event = Event()
    event.start = datetime(2000, 1, 1, 0, 0, 0)
    event.duration = timedelta(seconds=0)
    assert event.end == event.start


def test_todo_negative_duration_allowed():
    todo = Todo()
    todo.start = datetime(2000, 1, 1, 0, 0, 0)
    todo.duration = timedelta(seconds=-4)
    assert todo.end == datetime(1999, 12, 31, 23, 59, 56)
