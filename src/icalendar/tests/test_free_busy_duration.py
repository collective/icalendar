from datetime import datetime, timedelta

import pytest

from icalendar import FreeBusy
from icalendar.error import InvalidCalendar


def test_freebusy_duration_without_start_or_end():
    """Duration should be None if DTSTART or DTEND is missing."""
    freebusy = FreeBusy.new()

    assert freebusy.duration is None


def test_freebusy_duration_with_start_and_end():
    """Duration should be computed from DTSTART and DTEND."""
    start = datetime(2026, 4, 1, 10, 0)
    end = datetime(2026, 4, 1, 12, 30)

    freebusy = FreeBusy.new(start=start, end=end)

    assert freebusy.duration == timedelta(hours=2, minutes=30)


def test_freebusy_invalid_date_order():
    start = datetime(2026, 3, 20, 15, 0)
    end = datetime(2026, 3, 20, 13, 0)

    with pytest.raises(InvalidCalendar):
        FreeBusy.new(start=start, end=end)
