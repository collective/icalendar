import pytest

from icalendar import Calendar, Component, Event, InvalidCalendar, LazyCalendar
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

NON_UTF8_EVENT = b"BEGIN:VEVENT\r\n" b"SUMMARY:R\xe9union\r\n" b"END:VEVENT\r\n"


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
    assert Contentlines.from_ical(b"SUMMARY:R\xe9union\r\n", encoding="cp1252") == [
        "SUMMARY:R\u00e9union",
        "",
    ]


@pytest.mark.parametrize("parser", [Component, Event])
def test_component_invalid_utf8_raises(parser):
    """Generic components reject invalid UTF-8 like Calendar does."""
    with pytest.raises(InvalidCalendar):
        parser.from_ical(NON_UTF8_EVENT)


@pytest.mark.parametrize("parser", [Component, Event])
def test_component_explicit_encoding_recovers(parser):
    """A known legacy encoding decodes the same bytes successfully."""
    component = parser.from_ical(NON_UTF8_EVENT, encoding="cp1252")

    assert str(component["SUMMARY"]) == "R\u00e9union"


def test_lazy_calendar_invalid_utf8_raises():
    with pytest.raises(InvalidCalendar):
        LazyCalendar.from_ical(NON_UTF8_CALENDAR)


def test_lazy_calendar_explicit_replace_recovers():
    calendar = LazyCalendar.from_ical(NON_UTF8_CALENDAR, errors="replace")

    assert str(calendar.events[0]["SUMMARY"]) == "R\ufffdunion"


@pytest.mark.parametrize(
    "parse",
    [
        lambda **kwargs: Contentline.from_ical(b"SUMMARY:R\xe9union", **kwargs),
        lambda **kwargs: Contentlines.from_ical(b"SUMMARY:R\xe9union\r\n", **kwargs),
    ],
    ids=["Contentline", "Contentlines"],
)
def test_content_lines_invalid_utf8_raises(parse):
    with pytest.raises(InvalidCalendar):
        parse()


def test_content_lines_explicit_replace_recovers():
    assert "�" in Contentline.from_ical(b"SUMMARY:R\xe9union", errors="replace")
    assert "�" in Contentlines.from_ical(b"SUMMARY:R\xe9union\r\n", errors="replace")[0]


def test_valid_str_input_is_unaffected():
    """Text input bypasses byte decoding entirely."""
    text = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "BEGIN:VEVENT\r\n"
        "SUMMARY:Réunion\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    assert str(Calendar.from_ical(text).events[0]["SUMMARY"]) == "Réunion"


def test_utf8_sig_bom_still_handled_under_strict_decoding():
    """A leading UTF-8 BOM must not turn into InvalidCalendar."""
    calendar = Calendar.from_ical(
        b"\xef\xbb\xbfBEGIN:VCALENDAR\r\nVERSION:2.0\r\nEND:VCALENDAR\r\n"
    )

    assert calendar.name == "VCALENDAR"
