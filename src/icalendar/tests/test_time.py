import datetime
import os

import icalendar


def test_value_type_is_not_mapped():
    """Usually, the value should be absent."""
    assert "X-SOMETIME" not in icalendar.cal.types_factory.types_map


def test_value_type_is_mapped(x_sometime):
    """The value is mapped for the test."""
    assert "X-SOMETIME" in icalendar.cal.types_factory.types_map


def test_create_from_ical(x_sometime):
    directory = os.path.dirname(__file__)
    ics = open(os.path.join(directory, "calendars", "time.ics"), "rb")
    cal = icalendar.Calendar.from_ical(ics.read())
    ics.close()

    assert cal["X-SOMETIME"].dt == datetime.time(17, 20, 10)
    assert cal["X-SOMETIME"].to_ical() == "172010"


def test_create_to_ical(x_sometime):
    cal = icalendar.Calendar()
    cal.add("X-SOMETIME", datetime.time(17, 20, 10))
    assert b"X-SOMETIME;VALUE=TIME:172010" in cal.to_ical().splitlines()
