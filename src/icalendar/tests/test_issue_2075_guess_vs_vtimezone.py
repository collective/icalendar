"""A VTIMEZONE takes precedence over a guessed globally unique TZID.

See https://github.com/collective/icalendar/issues/2075
"""

import warnings
from datetime import timedelta

import pytest

from icalendar import Calendar
from icalendar.error import GloballyUniqueTZIDGuessed

EVENT = (
    "BEGIN:VEVENT\r\nUID:b\r\nDTSTAMP:20200101T000000Z\r\n"
    "DTSTART;TZID=/example.org/Europe/Berlin:20200701T120000\r\nEND:VEVENT\r\n"
)
VTIMEZONE = (  # fixed +01:00, no DST
    "BEGIN:VTIMEZONE\r\nTZID:/example.org/Europe/Berlin\r\nBEGIN:STANDARD\r\n"
    "DTSTART:19700101T000000\r\nTZOFFSETFROM:+0100\r\nTZOFFSETTO:+0100\r\n"
    "END:STANDARD\r\nEND:VTIMEZONE\r\n"
)


@pytest.fixture(autouse=True)
def fresh_cache(tzp):
    tzp.use(tzp.name)


def cal(body):
    return (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:test\r\n" + body + "END:VCALENDAR\r\n"
    )


def offset(text):
    return Calendar.from_ical(text).events[0].DTSTART.utcoffset()


@pytest.mark.filterwarnings("ignore::icalendar.error.GloballyUniqueTZIDGuessed")
def test_vtimezone_before_event(tzp):
    assert offset(cal(VTIMEZONE + EVENT)) == timedelta(hours=1)


@pytest.mark.filterwarnings("ignore::icalendar.error.GloballyUniqueTZIDGuessed")
def test_vtimezone_after_event(tzp):
    assert offset(cal(EVENT + VTIMEZONE)) == timedelta(hours=1)


@pytest.mark.filterwarnings("ignore::icalendar.error.GloballyUniqueTZIDGuessed")
def test_vtimezone_after_guess_in_other_calendar(tzp):
    Calendar.from_ical(cal(EVENT))
    assert offset(cal(VTIMEZONE + EVENT)) == timedelta(hours=1)


def test_no_guess_warning_once_vtimezone_is_cached(tzp):
    with pytest.warns(GloballyUniqueTZIDGuessed):
        tzp.timezone("/example.org/Europe/Berlin")
    Calendar.from_ical(cal(VTIMEZONE))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert tzp.timezone("/example.org/Europe/Berlin") is not None
