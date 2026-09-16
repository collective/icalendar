import pytest

from icalendar import Calendar, InvalidCalendar
from icalendar.parser import Contentline, Contentlines

NON_UTF8_CALENDAR = (
    b"BEGIN:VCALENDAR\r\n"
    b"VERSION:2.0\r\n"
    b"BEGIN:VEVENT\r\n"
    b"SUMMARY:R\xe9union\r\n"
    b"DTSTART:20240101T100000Z\r\n"
    b"END:VEVENT\r\n"
    b"END:VCALENDAR\r\n"
)


def test_non_utf8_calendar_bytes_raise_invalid_calendar():
    with pytest.raises(InvalidCalendar, match="issues/1793") as raised:
        Calendar.from_ical(NON_UTF8_CALENDAR)

    assert isinstance(raised.value.__cause__, UnicodeDecodeError)


def test_non_utf8_calendar_bytes_can_use_source_encoding():
    calendar = Calendar.from_ical(NON_UTF8_CALENDAR, encoding="cp1252")

    assert str(calendar.events[0]["SUMMARY"]) == "R\u00e9union"


def test_non_utf8_calendar_bytes_can_explicitly_replace_errors():
    calendar = Calendar.from_ical(NON_UTF8_CALENDAR, errors="replace")

    assert str(calendar.events[0]["SUMMARY"]) == "R\ufffdunion"


def test_content_line_decoding_options_are_forwarded():
    assert Contentline.from_ical(b"SUMMARY:R\xe9union", encoding="cp1252") == (
        "SUMMARY:R\u00e9union"
    )
    assert Contentlines.from_ical(
        b"SUMMARY:R\xe9union\r\n", encoding="cp1252"
    ) == ["SUMMARY:R\u00e9union", ""]
