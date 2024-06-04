from icalendar.prop import vDDDTypes
from datetime import date, datetime, timedelta
import pytest


def test_instance():
    assert isinstance(vDDDTypes.from_ical('20010101T123000'), datetime)
    assert isinstance(vDDDTypes.from_ical('20010101'), date)


def test_datetime_with_timezone(tzp):
    assert vDDDTypes.from_ical('20010101T123000Z') == \
                     tzp.localize_utc(datetime(2001, 1, 1, 12, 30))


def test_timedelta():
    assert vDDDTypes.from_ical('P31D') == timedelta(31)
    assert vDDDTypes.from_ical('-P31D') == timedelta(-31)


def test_bad_input():
    with pytest.raises(ValueError):
        vDDDTypes(42)
