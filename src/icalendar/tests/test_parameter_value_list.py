"""Comma-separated VALUE parameters must not crash Parameters.value."""

from icalendar import Calendar
from icalendar.parser.parameter import Parameters


def test_parameters_value_uses_first_of_comma_list():
    params = Parameters.from_ical("VALUE=DATE,DATE")
    assert params.value == "DATE"


def test_from_ical_value_date_comma_list():
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//test//EN\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:1\r\n"
        "DTSTART:20200101T000000Z\r\n"
        "DTEND;VALUE=DATE,DATE:20200102\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    cal = Calendar.from_ical(ics)
    event = cal.walk("VEVENT")[0]
    assert event["DTEND"].dt.year == 2020
