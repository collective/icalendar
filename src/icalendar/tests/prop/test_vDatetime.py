"""Test vDatetime ical_value property."""

from datetime import datetime
from zoneinfo import ZoneInfo

from icalendar.prop import vDatetime


def test_ical_value_naive():
    """ical_value property returns naive datetime object."""
    dt = datetime(2021, 3, 2, 10, 15, 30)
    vdt = vDatetime(dt)
    assert vdt.ical_value == dt
    assert isinstance(vdt.ical_value, datetime)
    assert vdt.ical_value.tzinfo is None


def test_ical_value_aware():
    """ical_value property returns timezone-aware datetime object."""
    tz = ZoneInfo("America/New_York")
    dt = datetime(2021, 3, 2, 10, 15, 30, tzinfo=tz)
    vdt = vDatetime(dt)
    assert vdt.ical_value == dt
    assert vdt.ical_value.tzinfo is not None
    assert vdt.ical_value.tzname() == "EST"


def test_ical_value_utc():
    """ical_value property handles UTC datetime."""
    tz = ZoneInfo("UTC")
    dt = datetime(2021, 3, 2, 10, 15, 30, tzinfo=tz)
    vdt = vDatetime(dt)
    assert vdt.ical_value == dt
    assert vdt.ical_value.tzname() == "UTC"


def test_ical_value_components():
    """ical_value property components match year, month, day, hour, minute, second."""
    dt = datetime(2026, 5, 8, 14, 30, 45)
    vdt = vDatetime(dt)
    assert vdt.ical_value.year == 2026
    assert vdt.ical_value.month == 5
    assert vdt.ical_value.day == 8
    assert vdt.ical_value.hour == 14
    assert vdt.ical_value.minute == 30
    assert vdt.ical_value.second == 45


def test_ical_value_from_ical():
    """ical_value property works with datetime parsed from ical string."""
    dt = vDatetime.from_ical("20210302T101500")
    vdt = vDatetime(dt)
    assert vdt.ical_value == datetime(2021, 3, 2, 10, 15, 0)

    # With timezone
    dt_tz = vDatetime.from_ical("20210302T101500", ZoneInfo("Europe/Berlin"))
    vdt_tz = vDatetime(dt_tz)
    assert vdt_tz.ical_value.year == 2021
    assert vdt_tz.ical_value.tzinfo is not None
