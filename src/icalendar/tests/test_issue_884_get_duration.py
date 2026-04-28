"""If the duration property exists, and it's not a ``default`` object but a
``timedelta`` instance, then it should return a ``duration``, not ``None``.

See https://github.com/collective/icalendar/issues/884
"""

from datetime import timedelta

import pytest

from icalendar import Event, InvalidCalendar


def test_duration_is_a_duration():
    """The duration is a duration."""
    event = Event()
    event["duration"] = timedelta(1)
    with pytest.raises(InvalidCalendar):
        event.DURATION


def test_duration_is_properly_set():
    event = Event()
    event.add("duration", timedelta(1))
    assert event.DURATION == timedelta(1)
