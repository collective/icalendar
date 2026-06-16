from datetime import date, datetime, time, timedelta

import pytest

from icalendar.prop import vDDDTypes


def test_instance():
    assert isinstance(vDDDTypes.from_ical("20010101T123000"), datetime)
    assert isinstance(vDDDTypes.from_ical("20010101"), date)


def test_datetime_with_timezone(tzp):
    assert vDDDTypes.from_ical("20010101T123000Z") == tzp.localize_utc(
        datetime(2001, 1, 1, 12, 30)
    )


def test_timedelta():
    assert vDDDTypes.from_ical("P31D") == timedelta(31)
    assert vDDDTypes.from_ical("-P31D") == timedelta(-31)


def test_bad_input():
    with pytest.raises(TypeError):
        vDDDTypes(42)


def test_time_from_string():
    assert vDDDTypes.from_ical("123000") == time(12, 30)
    assert isinstance(vDDDTypes.from_ical("123000"), time)


def test_invalid_period_to_ical():
    invalid_period = (datetime(2000, 1, 1), datetime(2000, 1, 2), datetime(2000, 1, 2))
    with pytest.raises(ValueError):
        vDDDTypes(invalid_period).to_ical()


@pytest.mark.parametrize(
    "bad_input",
    [None, 42, 3.14, datetime(2025, 1, 1), date(2025, 1, 1), ["20250101"], {"dt": "20250101"}],
    ids=["None", "int", "float", "datetime", "date", "list", "dict"],
)
def test_from_ical_rejects_non_str_input(bad_input):
    """Non-str/bytes input should raise ValueError, not AttributeError.

    Previously vDDDTypes.from_ical called ``ical.upper()`` without guarding
    against non-string input, so passing None, a number, or a datetime
    instance surfaced a confusing ``AttributeError: 'NoneType' object has
    no attribute 'upper'``. The new path raises a clear ValueError naming
    the offending type, matching the wrapping pattern used by the sibling
    vDate / vDatetime / vTime / vPeriod / vDuration.from_ical helpers.
    """
    with pytest.raises(ValueError, match="Expected datetime, date, or time as str or bytes"):
        vDDDTypes.from_ical(bad_input)
