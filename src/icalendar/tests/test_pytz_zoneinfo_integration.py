"""This tests the switch to different timezone implementations.

These are mostly located in icalendar.timezone.
"""
import pytz
from icalendar.timezone.zoneinfo import zoneinfo, ZONEINFO
from icalendar.timezone.pytz import PYTZ
import pytest


@pytest.mark.parametrize("tz_name", pytz.all_timezones + list(zoneinfo.available_timezones()))
@pytest.mark.parametrize("tzp_", [PYTZ(), ZONEINFO()])
def test_timezone_names_are_known(tz_name, tzp_):
    """Make sure that all timezones are understood."""
    assert tzp_.knows_timezone_id(tz_name), f"{tzp_.__class__.__name__} should know {tz_name}"
