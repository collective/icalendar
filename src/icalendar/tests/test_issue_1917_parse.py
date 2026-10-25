"""Tests for icalendar.parse, which detects iCal, jCal and xCal automatically.

See https://github.com/collective/icalendar/issues/1917
"""

import pytest

from icalendar import (
    Calendar,
    CalendarInformationLost,
    NoCalendarsFound,
    UnknownCalendarFormat,
    parse,
)

ICAL = b"BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:test\r\nEND:VCALENDAR\r\n"
JCAL = b'["vcalendar", [["version", {}, "text", "2.0"], ["prodid", {}, "text", "test"]], []]'
XCAL = (
    b'<?xml version="1.0"?>'
    b'<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0"><vcalendar><properties>'
    b"<version><text>2.0</text></version><prodid><text>test</text></prodid>"
    b"</properties></vcalendar></icalendar>"
)


@pytest.fixture(params=[ICAL, JCAL, XCAL], ids=["ical", "jcal", "xcal"])
def data(request):
    """Valid data for each supported format."""
    return request.param


@pytest.fixture
def data_path(data, tmp_path):
    """A path to a file that contains the data."""
    path = tmp_path / "calendar.ics"
    path.write_bytes(data)
    return path


@pytest.fixture
def data_file(data_path):
    """The data as a file opened in binary mode."""
    with data_path.open("rb") as file:
        yield file


def test_parse_bytes(data):
    """Each format is detected and parsed into a single calendar."""
    calendar = parse(data)
    assert isinstance(calendar, Calendar)
    assert calendar["PRODID"] == "test"


def test_parse_path(data_path):
    """A path to a file is read and parsed."""
    assert parse(data_path)["PRODID"] == "test"


def test_parse_open_file(data_file):
    """An open binary file is read and parsed."""
    assert parse(data_file)["PRODID"] == "test"


def test_parse_multiple_returns_list(data):
    """With multiple=True, each format returns a list of calendars."""
    calendars = parse(data, multiple=True)
    assert isinstance(calendars, list)
    assert len(calendars) == 1
    assert calendars[0]["PRODID"] == "test"


def test_leading_whitespace_is_ignored(data):
    """Whitespace before the data does not affect format detection."""
    assert parse(b"  \n" + data)["PRODID"] == "test"


def test_utf8_bom_is_ignored(data):
    """A UTF-8 byte order mark before the data does not affect format detection."""
    assert parse(b"\xef\xbb\xbf" + data)["PRODID"] == "test"


def test_lowercase_ical_is_detected():
    """iCalendar data that starts with a lowercase begin is detected."""
    assert parse(ICAL.lower())["PRODID"] == "test"


@pytest.mark.parametrize("data", [b"", b"   ", b"not a calendar"])
def test_unknown_format_raises_error(data):
    """Data with no detectable format raises an error that shows its start."""
    with pytest.raises(UnknownCalendarFormat, match="Could not detect"):
        parse(data)


def test_no_calendars_raises_error():
    """Data without any calendar raises an error."""
    with pytest.raises(NoCalendarsFound, match="No calendars found"):
        parse(b'<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0"></icalendar>')


def test_multiple_calendars_without_multiple_raises_error():
    """Several calendars with multiple=False raise an error."""
    with pytest.raises(CalendarInformationLost, match="multiple=True"):
        parse(ICAL + ICAL)


def test_str_raises_type_error():
    """Text instead of bytes raises a TypeError."""
    with pytest.raises(TypeError, match="Expected bytes, but got str"):
        parse(ICAL.decode())


def test_text_file_raises_type_error(data_path):
    """A file opened in text mode raises a TypeError."""
    with (
        data_path.open("r", encoding="utf-8") as file,
        pytest.raises(TypeError, match='"rb"'),
    ):
        parse(file)
