"""Tests for the lowercase accessors on :class:`icalendar.cal.Alarm`.

They cover #1569: the singleton properties previously only had
uppercase names.
"""

from datetime import datetime, timedelta, timezone

from icalendar import Alarm


def test_lowercase_accessors_alias_the_uppercase_properties():
    """The lowercase names expose the same property objects."""
    assert Alarm.action is Alarm.ACTION
    assert Alarm.trigger is Alarm.TRIGGER
    assert Alarm.duration is Alarm.DURATION
    assert Alarm.acknowledged is Alarm.ACKNOWLEDGED


def test_lowercase_accessors_roundtrip():
    """Setting through the lowercase name reads back from the uppercase one."""
    alarm = Alarm()
    acknowledged = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    alarm.action = "DISPLAY"
    alarm.trigger = timedelta(days=1)
    alarm.duration = timedelta(minutes=5)
    alarm.acknowledged = acknowledged
    assert alarm.ACTION == "DISPLAY"
    assert alarm.action == "DISPLAY"
    assert alarm.TRIGGER == timedelta(days=1)
    assert alarm.trigger == timedelta(days=1)
    assert alarm.DURATION == timedelta(minutes=5)
    assert alarm.duration == timedelta(minutes=5)
    assert alarm.ACKNOWLEDGED == acknowledged
    assert alarm.acknowledged == acknowledged
