"""Test vDate ical_value property."""

from datetime import date

from icalendar.prop import vDate


def test_ical_value_basic():
    """ical_value property returns date object."""
    d = date(1997, 7, 14)
    vd = vDate(d)
    assert vd.ical_value == d
    assert isinstance(vd.ical_value, date)


def test_ical_value_components():
    """ical_value property components match year, month, day."""
    d = date(2026, 5, 8)
    vd = vDate(d)
    assert vd.ical_value.year == 2026
    assert vd.ical_value.month == 5
    assert vd.ical_value.day == 8


def test_ical_value_from_ical():
    """ical_value property works with date parsed from ical string."""
    d = vDate.from_ical("19970714")
    vd = vDate(d)
    assert vd.ical_value == date(1997, 7, 14)


def test_ical_value_leap_year():
    """ical_value property handles leap year dates."""
    d = date(2024, 2, 29)  # Leap year
    vd = vDate(d)
    assert vd.ical_value == d
    assert vd.ical_value.day == 29


def test_ical_value_year_boundaries():
    """ical_value property handles year boundaries."""
    # First day of year
    d1 = date(2026, 1, 1)
    vd1 = vDate(d1)
    assert vd1.ical_value == d1

    # Last day of year
    d2 = date(2026, 12, 31)
    vd2 = vDate(d2)
    assert vd2.ical_value == d2
