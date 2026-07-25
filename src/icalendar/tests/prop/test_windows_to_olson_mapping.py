"""Test the mappings from windows to olson tzids"""

from datetime import datetime

import pytest

from icalendar import vDatetime
from icalendar.timezone import tzids_from_tzinfo
from icalendar.timezone.windows_to_olson import WINDOWS_TO_OLSON


def test_windows_timezone(tzp):
    """Test that the timezone is mapped correctly to olson."""
    dt = vDatetime.from_ical("20170507T181920", "Eastern Standard Time")
    expected = tzp.localize(datetime(2017, 5, 7, 18, 19, 20), "America/New_York")
    assert dt.tzinfo == expected.tzinfo
    assert dt == expected


def test_mountain_standard_time_mexico(tzp):
    """Test the current CLDR mapping for Mountain Standard Time (Mexico)."""
    dt = vDatetime.from_ical("20260706T110000", "Mountain Standard Time (Mexico)")
    expected = tzp.localize(datetime(2026, 7, 6, 11), "America/Mazatlan")
    assert dt.tzinfo == expected.tzinfo
    assert dt == expected


@pytest.mark.parametrize("olson_id", WINDOWS_TO_OLSON.values())
def test_olson_names(tzp, olson_id):
    """test if all mappings actually map to valid tzids"""
    assert olson_id in tzids_from_tzinfo(tzp.timezone(olson_id))
