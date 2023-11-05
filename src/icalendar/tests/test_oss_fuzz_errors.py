"""This file collects errors that the OSS FUZZ build has found."""
from icalendar import Calendar
import pytest


def test_stack_is_empty():
    """If we get passed an invalid string, we expect to get a ValueError."""
    with pytest.raises(ValueError):
        Calendar.from_ical("END:CALENDAR")
