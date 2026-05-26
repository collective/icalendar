from datetime import datetime, timedelta

import pytest

from icalendar import FreeBusy
from icalendar.error import InvalidCalendar


def test_freebusy_duration_none():
    freebusy = FreeBusy.new()

    assert freebusy.duration is None


def test_freebusy_duration_calculation():
    start = datetime(2026, 3, 20, 10, 0)
    end = datetime(2026, 3, 20, 12, 30)

    freebusy = FreeBusy.new(start=start, end=end)

    assert freebusy.duration == timedelta(hours=2, minutes=30)


def test_freebusy_invalid_date_order():
    start = datetime(2026, 3, 20, 15, 0)
    end = datetime(2026, 3, 20, 13, 0)

    with pytest.raises(InvalidCalendar):
        FreeBusy.new(start=start, end=end)
