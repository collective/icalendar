"""Calendar data that is not valid UTF-8 raises an error instead of being corrupted.

See https://github.com/collective/icalendar/issues/1793
"""

import pytest

from icalendar import (
    Calendar,
    CalendarDecodeError,
    ICalDecodeError,
    ICalParsingError,
    LazyCalendar,
)

# \xe9 is "é" in cp1252, but not valid UTF-8
CP1252_CALENDAR = (
    b"BEGIN:VCALENDAR\r\n"
    b"VERSION:2.0\r\n"
    b"BEGIN:VEVENT\r\n"
    b"SUMMARY:R\xe9union\r\n"
    b"END:VEVENT\r\n"
    b"END:VCALENDAR\r\n"
)


@pytest.mark.parametrize("calendar_class", [Calendar, LazyCalendar])
def test_from_ical_raises_for_invalid_utf8(calendar_class):
    with pytest.raises(ICalDecodeError):
        calendar_class.from_ical(CP1252_CALENDAR)


def test_error_can_be_caught_as_parsing_or_decode_error():
    with pytest.raises(ICalParsingError):
        Calendar.from_ical(CP1252_CALENDAR)
    with pytest.raises(CalendarDecodeError):
        Calendar.from_ical(CP1252_CALENDAR)


def test_error_information():
    with pytest.raises(ICalDecodeError) as exc_info:
        Calendar.from_ical(CP1252_CALENDAR)
    error = exc_info.value
    assert error.encoding == "utf-8"
    assert error.value == b"\xe9"
    assert error.start == CP1252_CALENDAR.index(b"\xe9")
    assert error.line_number == 4
    assert isinstance(error.__cause__, UnicodeDecodeError)
    assert "issues/1793" in str(error)


def test_decode_with_known_encoding():
    calendar = Calendar.from_ical(CP1252_CALENDAR.decode("cp1252"))
    assert calendar.events[0]["SUMMARY"] == "Réunion"
