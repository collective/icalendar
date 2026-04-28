"""If the duration property exist (so it's not default object) and it's already a timedelta instance,
then currently None is returned.

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
