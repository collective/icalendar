"""Test the ical_value property of vDuration."""

from datetime import timedelta

import pytest

from icalendar import Event
from icalendar.prop import vDuration


@pytest.mark.parametrize(
    "td",
    [
        timedelta(days=15, seconds=18020),
        timedelta(weeks=7),
        timedelta(hours=-5),
        timedelta(days=-1, hours=-5),
        timedelta(0),
    ],
)
def test_ical_value(td):
    """ical_value returns the timedelta of the duration."""
    assert vDuration(td).ical_value == td


def test_ical_value_from_string():
    """ical_value also works when the duration is created from a string."""
    assert vDuration("-P14D").ical_value == timedelta(days=-14)


def test_decoded_uses_ical_value():
    """Component.decoded() returns the ical_value of a DURATION."""
    event = Event()
    event.add("DURATION", timedelta(hours=2))
    assert event.decoded("DURATION") == timedelta(hours=2)
