"""Tests for icalendar.parse, which detects iCal, jCal and xCal automatically.

See https://github.com/collective/icalendar/issues/1917
"""

import pytest

from icalendar import Calendar, parse

ICAL = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:test\r\nEND:VCALENDAR\r\n"
JCAL = b'["vcalendar", [["version", {}, "text", "2.0"], ["prodid", {}, "text", "test"]], []]'
XCAL = (
    b'<?xml version="1.0"?>'
    b'<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0"><vcalendar><properties>'
    b"<version><text>2.0</text></version><prodid><text>test</text></prodid>"
    b"</properties></vcalendar></icalendar>"
)


ALL_FORMATS = pytest.mark.parametrize(
    "data", [ICAL, JCAL, XCAL], ids=["ical", "jcal", "xcal"]
)


@ALL_FORMATS
def test_parse_returns_one_calendar(data):
    """Each format is detected and parsed into a single calendar."""
    calendar = parse(data)
    assert isinstance(calendar, Calendar)
    assert calendar["PRODID"] == "test"


def test_parse_path(tmp_path):
    """A path to a file is read and parsed."""
    path = tmp_path / "calendar.ics"
    path.write_bytes(ICAL)
    assert parse(path)["PRODID"] == "test"


def test_empty_data_raises_error():
    """Data with no detectable format raises a ValueError."""
    with pytest.raises(ValueError):
        parse(b"   ")


@ALL_FORMATS
def test_parse_multiple_returns_list(data):
    """With multiple=True, each format returns a list of calendars."""
    calendars = parse(data, multiple=True)
    assert isinstance(calendars, list)
    assert len(calendars) == 1
    assert calendars[0]["PRODID"] == "test"


def test_parse_open_file(tmp_path):
    """An open binary file is read and parsed."""
    path = tmp_path / "calendar.ics"
    path.write_bytes(ICAL)
    with path.open("rb") as file:
        assert parse(file)["PRODID"] == "test"


def test_leading_whitespace_is_ignored():
    """Whitespace before the data does not affect format detection."""
    assert parse(b"  \n" + ICAL)["PRODID"] == "test"


def test_no_calendars_raises_error():
    """Data without any calendar raises a ValueError."""
    with pytest.raises(ValueError, match="No calendars found"):
        parse(b'<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0"></icalendar>')


def test_multiple_calendars_without_multiple_raises_error():
    """Several calendars with multiple=False raise a ValueError."""
    with pytest.raises(ValueError, match="multiple=True"):
        parse(ICAL + ICAL)
