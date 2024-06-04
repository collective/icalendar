"""Test the mappings from windows to olson tzids"""
from icalendar.timezone.windows_to_olson import WINDOWS_TO_OLSON
import pytest
from icalendar import vDatetime
from datetime import datetime


def test_windows_timezone(tzp):
    """test that an example"""
    dt = vDatetime.from_ical('20170507T181920', 'Eastern Standard Time'),
    expected = tzp.localize(datetime(2017, 5, 7, 18, 19, 20), 'America/New_York')


@pytest.mark.parametrize("olson_id", WINDOWS_TO_OLSON.values())
def test_olson_names(tzp, olson_id):
    """test if all mappings actually map to valid tzids"""
    assert tzp.timezone(olson_id) is not None
