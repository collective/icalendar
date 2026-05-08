"""Test vTime ical_value property."""

from datetime import time, timezone

from icalendar.prop import vTime


def test_ical_value_local_time():
    """ical_value property returns time object for local time."""
    t = time(12, 30, 45)
    vt = vTime(t)
    assert vt.ical_value == t
    assert vt.ical_value.hour == 12
    assert vt.ical_value.minute == 30
    assert vt.ical_value.second == 45
    assert vt.ical_value.tzinfo is None


def test_ical_value_utc_time():
    """ical_value property returns time object with UTC timezone."""
    t = time(14, 0, 0, tzinfo=timezone.utc)
    vt = vTime(t)
    assert vt.ical_value == t
    assert vt.ical_value.tzinfo == timezone.utc


def test_ical_value_from_ical():
    """ical_value property works with time parsed from ical string."""
    t = vTime.from_ical("123045")
    vt = vTime(t)
    assert vt.ical_value == time(12, 30, 45)

    t_utc = vTime.from_ical("140000Z")
    vt_utc = vTime(t_utc)
    assert vt_utc.ical_value.hour == 14
    assert vt_utc.ical_value.tzinfo is not None  # Has timezone info
