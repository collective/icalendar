"""This file collects errors that the OSS FUZZ build has found."""

from datetime import time
from pathlib import Path

import pytest

from icalendar.cal.calendar import Calendar
from icalendar.parser import Parameters
from icalendar.parser.content_line import Contentline
from icalendar.prop import vDDDLists
from icalendar.tests.fuzzed import fuzz_v1_calendar


def test_stack_is_empty():
    """If we get passed an invalid string, we expect to get a ValueError."""
    with pytest.raises(ValueError):
        Calendar.from_ical("END:CALENDAR")


def test_vdd_list_type_mismatch():
    """If we pass in a string type, we expect it to be converted to bytes"""
    vddd_list = vDDDLists([time(hour=6, minute=6, second=6)])
    assert vddd_list.to_ical() == b"060606"


def test_rrule_raw_newline_serializes():
    """CIFuzz #1741: a malformed RRULE key with a raw LF must not crash to_ical."""
    path = Path(__file__).parent / "calendars" / "fuzz_testcase_rrule_raw_newline.ics"
    data = path.read_bytes()
    fuzz_v1_calendar(Calendar.from_ical, data, multiple=True, should_walk=False)
    for calendar in Calendar.from_ical(data, multiple=True):
        serialized = calendar.to_ical()
        assert b"\n" not in serialized.replace(b"\r\n", b"")


def test_from_parts_strips_raw_newline_in_non_text_value():
    """RECUR and other verbatim types can still emit LF; from_parts must strip it."""

    class _RawNewline:
        def to_ical(self) -> bytes:
            return b"FREQ=DAILY\nCOUNT=2"

    line = Contentline.from_parts("RRULE", Parameters(), _RawNewline())
    assert "\n" not in line
    assert line == "RRULE:FREQ=DAILYCOUNT=2"
