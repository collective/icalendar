"""Test vWeekday ical_value property."""

from icalendar.prop import vWeekday


def test_ical_value_simple_weekday():
    """ical_value property returns string for simple weekday."""
    wd = vWeekday("MO")
    assert wd.ical_value == "MO"
    assert isinstance(wd.ical_value, str)


def test_ical_value_all_weekdays():
    """ical_value property works for all weekday abbreviations."""
    weekdays = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    for day in weekdays:
        wd = vWeekday(day)
        assert wd.ical_value == day


def test_ical_value_positive_relative():
    """ical_value property returns string with positive relative position."""
    wd = vWeekday("2FR")
    assert wd.ical_value == "2FR"
    assert wd.relative == 2
    assert wd.weekday == "FR"


def test_ical_value_negative_relative():
    """ical_value property returns string with negative relative position."""
    wd = vWeekday("-1SU")
    assert wd.ical_value == "-1SU"
    assert wd.relative == -1
    assert wd.weekday == "SU"


def test_ical_value_from_ical():
    """ical_value property works with weekday parsed from ical string."""
    wd = vWeekday.from_ical("MO")
    assert wd.ical_value == "MO"

    wd2 = vWeekday.from_ical("3TH")
    assert wd2.ical_value == "3TH"
    assert wd2.relative == 3


def test_ical_value_case_insensitive():
    """ical_value property handles case-insensitive input."""
    wd_lower = vWeekday("mo")
    wd_upper = vWeekday("MO")
    # Both should normalize to uppercase
    assert wd_lower.ical_value.upper() == "MO"
    assert wd_upper.ical_value == "MO"


def test_ical_value_with_plus_sign():
    """ical_value property handles explicit plus sign."""
    wd = vWeekday("+2WE")
    assert wd.ical_value == "+2WE"
    assert wd.relative == 2
    assert wd.weekday == "WE"
