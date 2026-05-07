"""Test vDDDTypes ical_value property."""

from datetime import date, datetime, time, timedelta

from icalendar.prop import vDDDTypes


def test_ical_value_datetime():
    """ical_value property returns the datetime value."""
    dt = datetime(2021, 3, 2, 10, 15, 0)
    vddd = vDDDTypes(dt)
    assert vddd.ical_value == dt
    assert isinstance(vddd.ical_value, datetime)


def test_ical_value_date():
    """ical_value property returns the date value."""
    d = date(1997, 7, 14)
    vddd = vDDDTypes(d)
    assert vddd.ical_value == d
    assert isinstance(vddd.ical_value, date)


def test_ical_value_time():
    """ical_value property returns the time value."""
    t = time(17, 20, 10)
    vddd = vDDDTypes(t)
    assert vddd.ical_value == t
    assert isinstance(vddd.ical_value, time)


def test_ical_value_timedelta():
    """ical_value property returns the timedelta value."""
    td = timedelta(days=15, hours=5, seconds=20)
    vddd = vDDDTypes(td)
    assert vddd.ical_value == td
    assert isinstance(vddd.ical_value, timedelta)


def test_ical_value_period():
    """ical_value property returns the period tuple."""
    start = datetime(2021, 3, 2, 10, 0, 0)
    end = datetime(2021, 3, 2, 12, 0, 0)
    period = (start, end)
    vddd = vDDDTypes(period)
    assert vddd.ical_value == period
    assert isinstance(vddd.ical_value, tuple)
