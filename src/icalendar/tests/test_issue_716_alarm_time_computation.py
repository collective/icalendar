"""Test the alarm time computation."""

from icalendar.alarms import Alarms
from datetime import datetime, timedelta, timezone


EXAMPLE_TRIGGER = datetime(1997, 3, 17, 13, 30, tzinfo=timezone.utc)


def test_absolute_alarm_time(alarms):
    """Check that the absolute alarm is recognized.

    The following example is for a "VALARM" calendar component
    that specifies an audio alarm that will sound at a precise time
    and repeat 4 more times at 15-minute intervals:
    """
    a = Alarms(alarms.rfc_5545_absolute_alarm_example)
    times = a.times
    assert len(times) == 5
    for i, t in enumerate(times):
        assert t.trigger == EXAMPLE_TRIGGER + timedelta(minutes=15 * i)

