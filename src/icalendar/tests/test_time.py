import datetime
import os
from datetime import time

from icalendar import Calendar
from icalendar.prop.dt.time import vTime


def test_value_type_is_not_mapped(types_factory):
    """Usually, the value should be absent."""
    assert "X-SOMETIME" not in types_factory.types_map


def test_value_type_is_mapped(x_sometime, types_factory):
    """The value is mapped for the test."""
    assert "X-SOMETIME" in types_factory.types_map


def test_create_from_ical(x_sometime):
    directory = os.path.dirname(__file__)  # noqa: PTH120
    ics = open(os.path.join(directory, "calendars", "time.ics"), "rb")  # noqa: PTH118, PTH123, SIM115
    cal = Calendar.from_ical(ics.read())
    ics.close()

    assert cal["X-SOMETIME"].dt == datetime.time(17, 20, 10)
    assert cal["X-SOMETIME"].to_ical() == "172010"


def test_create_to_ical(x_sometime):
    cal = Calendar()
    cal.add("X-SOMETIME", datetime.time(17, 20, 10))
    assert b"X-SOMETIME;VALUE=TIME:172010" in cal.to_ical().splitlines()


def test_vtime_multiple_timezones(calendars):
    cal = calendars["multiple_timezones.ics"]

    events = list(cal.walk("VEVENT"))

    named = events[0]["RDATE"].dts[0].dt
    utc = events[1]["RDATE"].dts[0].dt
    floating = events[2]["RDATE"].dts[0].dt

    assert named.tzinfo is not None
    assert "America/New_York" in str(named.tzinfo)

    assert str(utc.tzinfo) == "UTC"

    assert floating.tzinfo is None


def test_vtime_with_tzinfo_object():
    tz = datetime.timezone.utc

    parsed = vTime.from_ical("083000", timezone=tz)

    assert parsed.tzinfo == tz


def test_localize_time(tzp):
    t = time(8, 30)
    tz = tzp.timezone("America/New_York")

    localized = tzp.localize(t, tz)

    assert isinstance(localized, time)
    assert localized.tzinfo is not None
    assert "America/New_York" in str(localized.tzinfo)


def test_localized_time_utc(tzp):
    t = time(8, 30)

    localized = tzp.localize_utc(t)

    assert isinstance(localized, time)
    assert str(localized.tzinfo) == "UTC"
